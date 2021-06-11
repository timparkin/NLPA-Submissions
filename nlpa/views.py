from django.conf import settings # new
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
import csv
import stripe

from nlpa.forms import PaymentPlanForm
from userauth.models import CustomUser as User
from entries.models import Entry
import json

from nlpa.settings.config import entry_products, portfolio_products

from django.contrib.admin.views.decorators import staff_member_required
from django_thumbor import generate_url
from mailchimp3 import MailChimp



class HomePageView(TemplateView):
    template_name = 'home.html'

class FAQPageView(TemplateView):
    template_name = 'faq.html'


@login_required
def get_paymentplan(request):

    # testing code to tweak status
    #request.user.payment_plan = json.dumps( {'entries': '12', 'portfolios': '1' })
    #request.session['number_of_portfolios'] = '1'
    #request.session['number_of_entries'] = '12'
    #request.user.payment_status = 'checkout.session.completed'
    #request.user.save()


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
            return HttpResponseRedirect('/paymentplanconfirm/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PaymentPlanForm()

    return render(request, 'paymentplan.html', {'form': form})


@login_required
def get_paymentupgrade(request):

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


    mailchimp_api_key = "d27bd5dfdc92f62ee663893a2422cd56-us7"
    client = MailChimp(mc_api=mailchimp_api_key,mc_user='naturallandscapeawards')
    mc = client.lists.members.all('06156c9627',get_all=True, fields="members.email_address,members.id")
    print(mc)
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
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse()

    response['Content-Disposition'] = 'attachment; filename="nlpa_combined_mailing_list.csv"'

    cusers = {}
    cusers_by_id = {}
    users = User.objects.all()

    for user in users:
        if user.payment_plan is not None:
            pp = json.loads(request.user.payment_plan)
            entries = pp['entries']
            projects = pp['portfolios']
        else:
            entries = 0
            projects = 0
        cusers[user.email] = {
                'name': '%s %s'%(user.first_name,user.last_name),
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'payment_status': user.payment_status,
                'entries': entries,
                'projects': projects,
                'uploads': user.entry_set.count(),
                'source': 'system'
                }

        cusers_by_id[user.id] = cusers[user.email]


    mailchimp_api_key = "d27bd5dfdc92f62ee663893a2422cd56-us7"
    client = MailChimp(mc_api=mailchimp_api_key,mc_user='naturallandscapeawards')
    mc = client.lists.members.all('06156c9627',get_all=True, fields="members.email_address,members.id")

    for m in mc['members']:
        if m['email_address'] not in cusers:
            cusers[m['email_address']] = {'email': m['email_address'], 'source': 'mailchimp'}
        else:
            cusers[m['email_address']]['source'] = 'mailchimp'


    # NEED TO BLEND MAILCHIMP & SYSTEM USERS WITH MAIN USERS

    stripe.api_key = settings.STRIPE_SECRET_KEY
    sessions = stripe.checkout.Session.list(limit=100)
    customers = stripe.Customer.list(limit=100)
    cleaned_sessions = []

    pc = {}


    for c in sessions.auto_paging_iter():
        if c.get('customer_details'):
            email = c['customer_details']['email']
        else:
            try:
                email = cusers_by_id[int(c['client_reference_id'])]['email']
            except:
                email = c['client_reference_id']

        if email not in pc:
            pc[email] = {'paid': 0, 'unpaid':0}
        pc[email]['email'] = email
        pc[email][c['payment_status']] += c['amount_total']
        pc[email]['user_id'] = c['client_reference_id']
        pc[email]['pi_id'] = c['payment_intent']
        pc[email]['stripe_user_id'] = c['customer']

        cleaned_sessions.append(
            {
            'email': email,
            'user_id': c['client_reference_id'],
            'stripe_user_id': c['customer'],
            'pi_id': c['payment_intent'],
            'paid': c['amount_total'],
            'payment_status': c['payment_status'],
            }
        )

    CUSERS = []
    for v in cleaned_sessions:
        try:
            cusers[v['email']].update(v)
        except:
            pass
        CUSERS.append(v)

    extras = []
    for C in CUSERS:
        if C['email'] not in cusers:
            extras.append(C)

    Cs = []
    for email, cuser in cusers.items():
        Cs.append(cuser)
    Cs.extend(extras)




    cleaned_customers = {}
    for c in customers.auto_paging_iter():

        cleaned_customers[c['email']] = {
            'email': c['email'],
            'user_id': c['id'],
            'name': c['name'],
            }

    final_cc = []
    for k,v in cleaned_customers.items():
        final_cc.append(v)





    # return render(request, 'datamining_csv.html', {'sessions': cleaned_sessions, 'compiled_customers': compiled_customers, 'customers': final_cc})

    writer = csv.writer(response)
    writer.writerow(['email','source','name', 'id', 'stripe_user_id', 'payment_status','entries','projects','uploads','paid','unpaid'])
    for C in Cs:
        writer.writerow([ C['email'], C.get('source'), C.get('name'), C.get('id'), C.get('stripe_user_id'),  C.get('payment_status'), C.get('entries'), C.get('projects'), C.get('uploads'), C.get('paid'), C.get('unpaid'), ])

    return response
