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
from .data import  *



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


    mailchimp_api_key = settings.MAILCHIMP_API_KEY
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
    # Prepare Response
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="nlpa_combined_mailing_list.csv"'

    # GET DB USERS
    db_users = clean_db_users(User.objects.all())

    # GET MAILCHIMP USERS
    mailchimp_api_key = settings.MAILCHIMP_API_KEY
    client = MailChimp(mc_api=mailchimp_api_key,mc_user='naturallandscapeawards')
    mc_users = clean_mc_users(client.lists.members.all('06156c9627',get_all=True, fields="members.email_address,members.id"))


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
    writer.writerow(['email','name','id', 'entries', 'projects', 'uploads','in_db','in_mailchimp','in_stripe','paid','unpaid'])
    for C in db_user_list:
        writer.writerow([ C['email'], C.get('name'), C.get('id'), C.get('entries'), C.get('projects'),  C.get('uploads'), C.get('in_db'), C.get('in_mailchimp'), C.get('in_stripe'), C.get('paid'), C.get('unpaid'), ])

    return response
