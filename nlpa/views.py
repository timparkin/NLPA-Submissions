from django.conf import settings # new
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
import csv
import stripe

from nlpa.forms import PaymentPlanForm
from userauth.models import CustomUser as User, Year
from entries.models import Entry
import json

from nlpa.settings.config import entry_products, portfolio_products

from django.contrib.admin.views.decorators import staff_member_required
from django_thumbor import generate_url
from mailchimp3 import MailChimp
from .data import  *
from nlpa.settings.config import ENTRIES_CLOSED



class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({'ENTRIES_CLOSED': ENTRIES_CLOSED})
        return context

class FAQPageView(TemplateView):
    template_name = 'faq.html'

    def get_context_data(self, **kwargs):
        context = super(FAQPageView, self).get_context_data(**kwargs)
        context.update({'ENTRIES_CLOSED': ENTRIES_CLOSED})
        return context


@login_required
def get_paymentplan(request):

    # testing code to tweak status
    #request.user.payment_plan = json.dumps( {'entries': '12', 'portfolios': '1' })
    #request.session['number_of_portfolios'] = '1'
    #request.session['number_of_entries'] = '12'
    #request.user.payment_status = 'checkout.session.completed'
    #request.user.save()

    if ENTRIES_CLOSED:
        return HttpResponseRedirect('/')


    payment_status = request.user.payment_status
    if payment_status is not None:
        if 'checkout.session.completed' in payment_status:
            return HttpResponseRedirect('/entries')
        if 'payment_pending' in payment_status:
            return HttpResponseRedirect('/entries')
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PaymentPlanForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            request.session['number_of_entries'] = form.cleaned_data['number_of_entries']
            request.session['number_of_portfolios'] = form.cleaned_data['number_of_portfolios']
            request.session['youth_entry'] = form.cleaned_data['youth_entry']

            # redirect to a new URL:
            if request.user.is_young_entrant =='True':
                return HttpResponseRedirect('/paymentplanconfirm_youth/')
            else:
                return HttpResponseRedirect('/paymentplanconfirm/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PaymentPlanForm()


    if request.user.is_young_entrant == 'True':
        return render(request, 'paymentplan_youth.html', {'form': form})
    else:
        return render(request, 'paymentplan.html', {'form': form})


@login_required
def get_paymentupgrade(request):

    if ENTRIES_CLOSED:
        return HttpResponseRedirect('/secondround')


    if request.user.payment_plan is not None:
        payment_plan = json.loads(request.user.payment_plan)
    else:
        payment_plan = None
    payment_status = request.user.payment_status
    is_young_entrant = request.user.is_young_entrant
    entries = int(payment_plan['entries'])
    portfolios = int(payment_plan['portfolios'])

    ### TESTING
    #portfolios=1
    #entries=18

    request.session['entries'] = entries
    request.session['portfolios'] = portfolios
    request.session['is_young_entrant'] = is_young_entrant

    request.session['total_price'] = \
        float(
            entry_products[ str(entries) ]['price'] )/100 + \
        float(
            portfolio_products[ str(portfolios) ]['price'] )/100

    # build plan plantext
    plantext = "Your current plan is "
    if entries >0:
        if entries == 1:
            plantext += "%s single entry"%entries
        else:
            plantext += "%s single entries"%entries
    if portfolios>0:
        if entries >0:
            plantext += " and "
        if portfolios == 1:
            plantext += "%s project entry"%portfolios
        else:
            plantext += "%s project entries"%portfolios
    request.session['plantext'] = plantext

    if payment_status is None or ('checkout.session.completed' not in payment_status and 'payment_pending' not in payment_status):
        return HttpResponseRedirect('/paymentplan')

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PaymentPlanForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            request.session['number_of_additional_entries'] = int(form.cleaned_data['number_of_entries'])-entries
            request.session['number_of_additional_portfolios'] = int(form.cleaned_data['number_of_portfolios'])-portfolios
            request.session['youth_entry'] = form.cleaned_data['youth_entry']



            # redirect to a new URL:
            return HttpResponseRedirect('/paymentupgradeconfirm/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PaymentPlanForm(initial={
                'number_of_entries': entries,
                'number_of_portfolios': portfolios,
                'youth_entry': is_young_entrant,
                })

    return render(request, 'paymentupgrade.html', {'form': form})


@staff_member_required
def datamining(request):


    cusers = {}
    users = User.objects.all()

    for user in users:
        cusers[user.email] = {
                'name': '%s %s'%(user.first_name,user.last_name),
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'payment_status': user.payment_status,
                'payment_plan': user.payment_plan,
                'entries': user.entry_set.all()
                }


    mailchimp_api_key = settings.MAILCHIMP_API_KEY
    client = MailChimp(mc_api=mailchimp_api_key,mc_user='naturallandscapeawards')
    mc = client.lists.members.all('06156c9627',get_all=True, fields="members.email_address,members.id")

    for m in mc['members']:
        if m['email_address'] not in cusers:
            cusers[m['email_address']] = {'email': m['email_address'], 'source': 'mailchimp'}
        else:
            cusers[m['email_address']]['source'] = 'mailchimp'


    if 'email' in request.GET:
        email = request.GET['email']
    else:
        email = None

    tusers = []
    for k,v in cusers.items():
        if email:
            if k == email:
                tusers.append(v)
        else:
            tusers.append(v)



    return render(request, 'datamining.html', {'users': tusers})

@staff_member_required
def datamining_child(request):
    # Prepare Response
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="nlpa_combined_mailing_list.csv"'

    # GET DB USERS
    db_users = clean_db_users(User.objects.all())

    # GET MAILCHIMP USERS
    mailchimp_api_key = settings.MAILCHIMP_API_KEY
    client = MailChimp(mc_api=mailchimp_api_key,mc_user='naturallandscapeawards')
    mc_users = clean_mc_users(client.lists.members.all('06156c9627',get_all=True, fields="members.email_address,members.id,members.tags"))


    # STRIPE SESSION USERS
    stripe.api_key = settings.STRIPE_SECRET_KEY
    email_by_cus_id, ss_users, sessions = clean_ss_users(stripe.checkout.Session.list(limit=100), db_users)

    # STRIPE CUSTOMERS
    sc_users = clean_sc_users(stripe.Customer.list(limit=100))


    for email, mc_user in mc_users.items():
        if email in  db_users:
            db_users[email].update(mc_user)
        else:
            db_users[email] = mc_user

    for email, ss_user in ss_users.items():
        if email in db_users:
            db_users[email].update(ss_user)
        else:
            db_users[email] = ss_user

    db_user_list = []
    for email, db_user in db_users.items():
        db_user_list.append(db_user)



    # return render(request, 'datamining_csv.html', {'db_user_list': db_user_list, 'db_users': db_users, 'mc_users': mc_users, 'ss_users': ss_users, 'sc_users': sc_users, 'sessions': sessions })

    writer = csv.writer(response)
    writer.writerow(['email','name','id', 'entries', 'projects', 'uploads','np1','np2','np12','ne','misent','misproj','in_db','in_mailchimp','in_stripe','payment_status','paid','unpaid','mc_optin','mc_discount','mc_monster','is_young_entrant','date_of_birth'])
    for C in db_user_list:
        entries = int(C.get('entries',0))
        projects = int(C.get('projects',0))
        num_entries = int(C.get('ne',0))
        num_p1 = int(C.get('np1',0))
        num_p2 = int(C.get('np2',0))
        if entries-num_entries != 0:
            missing_entries = 1
        else:
            missing_entries = 0
        if projects ==1 and num_p1 <6:
            missing_projects = 1
        elif projects ==2 and (num_p1 < 6 or num_p2 <6):
            missing_projects = 1
        else:
            missing_projects = 0


        writer.writerow([ C.get('email'), C.get('name'), C.get('id'), C.get('entries'), C.get('projects'),  C.get('uploads'), C.get('np1'), C.get('np2'), C.get('np1',0)+C.get('np2',0), C.get('ne'), missing_entries, missing_projects, C.get('in_db'), C.get('in_mailchimp'), C.get('in_stripe'), C.get('payment_status'), C.get('paid'), C.get('unpaid'), C.get('mc_optin'),C.get('mc_discount'),C.get('mc_monster'),C.get('is_young_entrant'), C.get('date_of_birth') ])

    return response

@staff_member_required
def datamining_child_entries(request):
    # Prepare Response
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="nlpa_combined_entries.csv"'

    # GET DB USERS
    db_users = clean_db_users(User.objects.all())

    # GET MAILCHIMP USERS
    mailchimp_api_key = settings.MAILCHIMP_API_KEY
    client = MailChimp(mc_api=mailchimp_api_key,mc_user='naturallandscapeawards')
    mc_users = clean_mc_users(client.lists.members.all('06156c9627',get_all=True, fields="members.email_address,members.id,members.tags"))


    # STRIPE SESSION USERS
    stripe.api_key = settings.STRIPE_SECRET_KEY
    email_by_cus_id, ss_users, sessions = clean_ss_users(stripe.checkout.Session.list(limit=100), db_users)

    # STRIPE CUSTOMERS
    sc_users = clean_sc_users(stripe.Customer.list(limit=100))


    for email, mc_user in mc_users.items():
        if email in  db_users:
            db_users[email].update(mc_user)
        else:
            db_users[email] = mc_user

    for email, ss_user in ss_users.items():
        if email in db_users:
            db_users[email].update(ss_user)
        else:
            db_users[email] = ss_user

    db_user_list = []
    for email, db_user in db_users.items():
        db_user_list.append(db_user)

 # Entry Object attributes
 # 'category',
 # 'datetime',
 # 'filename',
 # 'id',
 # 'internal_notes',
 # 'photo',
 # 'photo_dimensions',
 # 'photo_size',
 # 'project_id',
 # 'title',
 # 'user',
 # 'user_id',
 # 'year'


    users_entries = []
    for user in db_user_list:
        if 'entry_objects' in user:

            for entry in user['entry_objects']:
                user_entry = {
                  'entry_id':  entry.id,
                  'entry_category': entry.category,
                  'entry_datetime': entry.datetime,
                  'entry_filename': entry.filename,
                  'entry_url': entry.photo.url,
                  'entry_photo_dimensions': entry.photo_dimensions,
                  'entry_photo_size': entry.photo_size,

                }
                user_entry.update(user)
                users_entries.append(user_entry)
        else:
            user_entry = {
              'entry_id':  '',
              'entry_category': '',
              'entry_datetime': '',
              'entry_filename': '',
              'entry_url': '',
              'entry_photo_dimensions': '',
              'entry_photo_size': '',

            }
            user_entry.update(user)
            users_entries.append(user_entry)


    # return render(request, 'datamining_csv.html', {'db_user_list': db_user_list, 'db_users': db_users, 'mc_users': mc_users, 'ss_users': ss_users, 'sc_users': sc_users, 'sessions': sessions })

    writer = csv.writer(response)
    writer.writerow([
        'email',
        'mc_email',
        'ss_email',
        'sc_email',
        'name',
        'id',
        'entries',
        'projects',
        'uploads',
        'in_db',
        'in_mailchimp',
        'in_stripe',
        'paid',
        'unpaid',
        'mc_optin',
        'mc_discount',
        'mc_monster',
        'is_young_entrant',
        'date_of_birth',
        'project_title_one',
        'project_description_one',
        'project_title_two',
        'project_description_two',
        'entry_id',
        'entry_category',
        'entry_datetime',
        'entry_filename',
        'entry_url',
        'entry_photo_dimensions',
        'entry_photo_size',
        ])


    for C in users_entries:
        writer.writerow([
        C.get('email'),
        C.get('mc_email'),
        C.get('ss_email'),
        C.get('sc_email'),
        C.get('name'),
        C.get('id'),
        C.get('entries'),
        C.get('projects'),
        C.get('uploads'),
        C.get('in_db'),
        C.get('in_mailchimp'),
        C.get('in_stripe'),
        C.get('paid'),
        C.get('unpaid'),
        C.get('mc_optin'),
        C.get('mc_discount'),
        C.get('mc_monster'),
        C.get('is_young_entrant'),
        C.get('date_of_birth'),
        C.get('project_title_one'),
        C.get('project_description_one'),
        C.get('project_title_two'),
        C.get('project_description_two'),
        C.get('entry_id'),
        C.get('entry_category'),
        C.get('entry_datetime'),
        C.get('entry_filename'),
        C.get('entry_url'),
        C.get('entry_photo_dimensions'),
        C.get('entry_photo_size'),
        ])

    return response


@staff_member_required
def missing_raws(request):
    just_missing = request.GET.get('just_missing',None) is not None
    get_all = request.GET.get('get_all',None) is not None

    # Prepare Response
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="nlpa_missing_raws.csv"'

    # GET DB USERS
    db_users = clean_db_users(User.objects.all())

    # GET MAILCHIMP USERS
    mailchimp_api_key = settings.MAILCHIMP_API_KEY
    client = MailChimp(mc_api=mailchimp_api_key,mc_user='naturallandscapeawards')
    mc_users = clean_mc_users(client.lists.members.all('06156c9627',get_all=True, fields="members.email_address,members.id,members.tags"))


    # STRIPE SESSION USERS
    stripe.api_key = settings.STRIPE_SECRET_KEY
    email_by_cus_id, ss_users, sessions = clean_ss_users(stripe.checkout.Session.list(limit=100), db_users)

    # STRIPE CUSTOMERS
    sc_users = clean_sc_users(stripe.Customer.list(limit=100))


    for email, mc_user in mc_users.items():
        if email in  db_users:
            db_users[email].update(mc_user)
        else:
            db_users[email] = mc_user

    for email, ss_user in ss_users.items():
        if email in db_users:
            db_users[email].update(ss_user)
        else:
            db_users[email] = ss_user

    for email, sc_user in sc_users.items():
        if email in db_users:
            db_users[email].update(sc_user)
        else:
            db_users[email] = sc_user

    db_user_list = []
    for email, db_user in db_users.items():
        db_user_list.append(db_user)

 # Entry Object attributes
 # 'category',
 # 'datetime',
 # 'filename',
 # 'id',
 # 'internal_notes',
 # 'photo',
 # 'photo_dimensions',
 # 'photo_size',
 # 'project_id',
 # 'title',
 # 'user',
 # 'user_id',
 # 'year'


    users_entries = []
    for user in db_user_list:
        if 'entry_objects' in user:

            for entry in user['entry_objects']:
                try:
                    eu1 = entry.evidence_file_1.url
                except ValueError as e:
                    eu1 = ''
                try:
                    eu2 = entry.evidence_file_2.url
                except ValueError as e:
                    eu2 = ''
                try:
                    eu3 = entry.evidence_file_3.url
                except ValueError as e:
                    eu3 = ''
                try:
                    eu4 = entry.evidence_file_4.url
                except ValueError as e:
                    eu4 = ''
                try:
                    eu5 = entry.evidence_file_5.url
                except ValueError as e:
                    eu5 = ''

                user_entry = {
                  'entry_id':  entry.id,
                  'entry_category': entry.category,
                  'entry_datetime': entry.datetime,
                  'entry_filename': entry.filename,
                  'entry_url': entry.photo.url,
                  'entry_photo_dimensions': entry.photo_dimensions,
                  'entry_photo_size': entry.photo_size,
                  'in_second_round': entry.in_second_round,
                  'evidence_file_1': entry.evidence_file_1.name[5:],
                  'evidence_file_2': entry.evidence_file_2.name[5:],
                  'evidence_file_3': entry.evidence_file_3.name[5:],
                  'evidence_file_4': entry.evidence_file_4.name[5:],
                  'evidence_file_5': entry.evidence_file_5.name[5:],
                  'evidence_url_1': eu1,
                  'evidence_url_2': eu2,
                  'evidence_url_3': eu3,
                  'evidence_url_4': eu4,
                  'evidence_url_5': eu5,

                }
                user_entry.update(user)
                users_entries.append(user_entry)
        else:
            user_entry = {
              'entry_id':  '',
              'entry_category': '',
              'entry_datetime': '',
              'entry_filename': '',
              'entry_url': '',
              'entry_photo_dimensions': '',
              'entry_photo_size': '',
              'entry_photo_size': '',
              'entry_photo_size': '',
              'entry_photo_size': '',
              'in_second_round': '',
              'evidence_file_1': '',
              'evidence_file_2': '',
              'evidence_file_3': '',
              'evidence_file_4': '',
              'evidence_file_5': '',
              'evidence_url_1': '',
              'evidence_url_2': '',
              'evidence_url_3': '',
              'evidence_url_4': '',
              'evidence_url_5': '',

            }
            user_entry.update(user)
            users_entries.append(user_entry)


    # return render(request, 'datamining_csv.html', {'db_user_list': db_user_list, 'db_users': db_users, 'mc_users': mc_users, 'ss_users': ss_users, 'sc_users': sc_users, 'sessions': sessions })

    writer = csv.writer(response)
    writer.writerow([
        'email',
        'mc_email',
        'ss_email',
        'sc_email',
        'name',
        'sc_name',
        'id',
	'user_id',
	'cr_id',
        'entries',
        'projects',
        'uploads',
        'in_db',
        'in_mailchimp',
        'in_stripe',
        'city',
        'country',
        'locales',
        'postcode',
        'paid',
        'unpaid',
        'mc_optin',
        'mc_discount',
        'mc_monster',
        'is_young_entrant',
        'date_of_birth',
        'project_title_one',
        'project_description_one',
        'project_title_two',
        'project_description_two',
        'entry_id',
        'entry_category',
        'entry_datetime',
        'entry_filename',
        'entry_url',
        'entry_photo_dimensions',
        'entry_photo_size',
        'in_second_round',
        'evidence_file_1',
        'evidence_file_2',
        'evidence_file_3',
        'evidence_file_4',
        'evidence_file_5',
        'evidence_url_1',
        'evidence_url_2',
        'evidence_url_3',
        'evidence_url_4',
        'evidence_url_5',
        ])


    for C in users_entries:
        if C.get('in_second_round') and just_missing:
            eu1 = C.get('evidence_url_1')
            eu2 = C.get('evidence_url_2')
            eu3 = C.get('evidence_url_3')
            eu4 = C.get('evidence_url_4')
            eu5 = C.get('evidence_url_5')
            # print('** %s'%C.get('entry_filename'))
            # print('1: %s'%eu1)
            # print('2: %s'%eu2)
            # print('3: %s'%eu3)
            # print('4: %s'%eu4)
            # print('5: %s'%eu5)


            e1 = eu1 and 'default-entry.png' not in eu1
            e2 = eu2 and 'default-entry.png' not in eu2
            e3 = eu3 and 'default-entry.png' not in eu3
            e4 = eu4 and 'default-entry.png' not in eu4
            e5 = eu5 and 'default-entry.png' not in eu5
            include_entry = e1 or e2 or e3 or e4 or e5
            # print('=== %s'%include_entry)
        else:
            include_entry = False

        if (C.get('in_second_round') and not include_entry) or get_all:
        #if True:
            writer.writerow([
            C.get('email'),
            C.get('mc_email'),
            C.get('ss_email'),
            C.get('sc_email'),
            C.get('name'),
            C.get('sc_name'),
            C.get('id'),
            C.get('user_id'),
            C.get('cr_id'),
            C.get('entries'),
            C.get('projects'),
            C.get('uploads'),
            C.get('in_db'),
            C.get('in_mailchimp'),
            C.get('in_stripe'),
            C.get('city'),
            C.get('country'),
            C.get('locales'),
            C.get('postcode'),
            C.get('paid'),
            C.get('unpaid'),
            C.get('mc_optin'),
            C.get('mc_discount'),
            C.get('mc_monster'),
            C.get('is_young_entrant'),
            C.get('date_of_birth'),
            C.get('project_title_one'),
            C.get('project_description_one'),
            C.get('project_title_two'),
            C.get('project_description_two'),
            C.get('entry_id'),
            C.get('entry_category'),
            C.get('entry_datetime'),
            C.get('entry_filename'),
            C.get('entry_url'),
            C.get('entry_photo_dimensions'),
            C.get('entry_photo_size'),
            C.get('in_second_round'),
            C.get('evidence_file_1'),
            C.get('evidence_file_2'),
            C.get('evidence_file_3'),
            C.get('evidence_file_4'),
            C.get('evidence_file_5'),
            C.get('evidence_url_1'),
            C.get('evidence_url_2'),
            C.get('evidence_url_3'),
            C.get('evidence_url_4'),
            C.get('evidence_url_5'),
            ])

    return response

@staff_member_required
def datamining_child_users(request):
    # Prepare Response
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="nlpa_combined_users.csv"'

    # GET DB USERS
    db_users = clean_db_users(User.objects.all())


 # Entry Object attributes
 # 'category',
 # 'datetime',
 # 'filename',
 # 'id',
 # 'internal_notes',
 # 'photo',
 # 'photo_dimensions',
 # 'photo_size',
 # 'project_id',
 # 'title',
 # 'user',
 # 'user_id',
 # 'year'





# 'name': '%s %s'%(user.first_name,user.last_name),
# 'id': str(user.id),
# 'email': user.email,
# 'username': user.username,
# 'payment_status': user.payment_status,
# 'entries': entries,
# 'entry_objects': entry_objects,
# 'projects': projects,
# 'uploads': user.entry_set.count(),
# 'in_db': True,


    # return render(request, 'datamining_csv.html', {'db_user_list': db_user_list, 'db_users': db_users, 'mc_users': mc_users, 'ss_users': ss_users, 'sc_users': sc_users, 'sessions': sessions })

    writer = csv.writer(response)
    writer.writerow([
        'email',
        'name',
        'id',
        'entries',
        'projects',
        'uploads',
        'is_young_entrant',
        'date_of_birth',
        ])


    for email, C in db_users.items():
        writer.writerow([
        C.get('email'),
        C.get('name'),
        C.get('id'),
        C.get('entries'),
        C.get('projects'),
        C.get('uploads'),
        C.get('is_young_entrant'),
        C.get('date_of_birth'),

        ])

    return response
