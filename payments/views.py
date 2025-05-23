from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render
import stripe
import datetime
import json
from userauth.models import CustomUser as User
from allauth.account.models import EmailAddress
import logging
from nlpa.settings.config import entry_products, portfolio_products, coupon_product, GOOGLEANALYTICS, ENTRIES_CLOSED, PROJECT_DIR, BASE_DIR, WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET
import random
from woocommerce import API
import smtplib
from . import welcome

logger = logging.getLogger(__name__)

class PurchasePageView(TemplateView):
    template_name = 'purchase.html'


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


# CONFIRM CHOICES ##########################################
@login_required
def payment_plan_confirm(request):
    request.session['total_price'] = \
        float(
            entry_products[ str(request.session['number_of_entries']) ]['price'] )/100 + \
        float(
            portfolio_products[ str(request.session['number_of_portfolios']) ]['price'] )/100
    if request.session['youth_entry']:
        request.session['total_price'] = request.session['total_price'] * 0.3
    request.session['total_price'] = '${:.0f}'.format( request.session['total_price'] )

    return render(request, 'paymentplanconfirm.html')


@login_required
def payment_upgrade_confirm(request):



    print(request.user.coupon)
    if request.user.payment_plan is not None:
        payment_plan = json.loads(request.user.payment_plan)
    else:
        payment_plan = None
    payment_status = request.user.payment_status
    is_young_entrant = request.user.is_young_entrant
    entries = int(payment_plan['entries'])
    portfolios = int(payment_plan['portfolios'])

    new_total = \
        float(
            entry_products[ str(request.session['number_of_additional_entries']+entries) ]['price'] )/100 + \
        float(
            portfolio_products[ str(request.session['number_of_additional_portfolios']+portfolios) ]['price'] )/100

    original_total = \
        float(
            entry_products[ str(entries) ]['price'] )/100 + \
        float(
            portfolio_products[ str(portfolios) ]['price'] )/100

    request.session['entries'] = str(payment_plan['entries'])
    request.session['portfolios'] = str(payment_plan['portfolios'])

    request.session['upgrade_price'] = '${:.0f}'.format( new_total - original_total )
    request.session['total_entries'] = str(request.session['number_of_additional_entries'] + entries)
    request.session['total_portfolios'] = str(request.session['number_of_additional_portfolios'] + portfolios)
    request.session['coupon'] = request.user.coupon


    return render(request, 'paymentupgradeconfirm.html')

#### CREATE CHECKOUT SESSION ##################################
@csrf_exempt
@login_required
def create_checkout_session(request):
    if request.method == 'GET':
        # PICK UP THE coupon GET PARAMETER AND ADD THE PRODUCT
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            line_items = []
            if (int(request.session['number_of_entries'])>0):
                line_items=[
                    {
                        'quantity': 1,
                        'price': entry_products[request.session['number_of_entries']]['price_id']
                    }
                ]
            if (int(request.session['number_of_portfolios'])>0):
                line_items.append(
                    {
                    'quantity': 1,
                    'price': portfolio_products[request.session['number_of_portfolios']]['price_id']
                    }
                )

            if request.GET.get('coupon') == 'true':
                line_items.append(
                    {
                        'quantity': 1,
                        'price': coupon_product['price_id']
                    }
                )
            print(request.GET.get('coupon'))
            request.session['coupon_product'] = request.GET.get('coupon') == 'true'


            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                allow_promotion_codes=True,
                payment_intent_data={'statement_descriptor_suffix': 'ENTRY','description': 'ENTRY'},
            )
            request.user.payment_plan = json.dumps( {'entries': request.session['number_of_entries'], 'portfolios': request.session['number_of_portfolios'] })
            request.user.payment_status = 'checkingout %s'%datetime.datetime.now()
            request.user.save()
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

#### CREATE UPGRADE CHECKOUT SESSION ##################################
@csrf_exempt
@login_required
def create_checkout_session_upgrade(request):
    if request.method == 'GET':


        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if request.user.payment_plan is not None:
            payment_plan = json.loads(request.user.payment_plan)
        else:
            payment_plan = None
        payment_status = request.user.payment_status
        is_young_entrant = request.user.is_young_entrant
        entries = int(payment_plan['entries'])
        portfolios = int(payment_plan['portfolios'])


        additional_entries = int(request.session['number_of_additional_entries'])
        additional_portfolios = int(request.session['number_of_additional_portfolios'])

    #    try:
        line_items = []
        if (additional_entries>0):
            line_items.append(
                {
                    'quantity': 1,
                    'price': entry_products['%s+%s'%(entries,additional_entries)]['price_id']
                }
            )
        if (additional_portfolios>0):
            line_items.append(
                {
                'quantity': 1,
                'price': portfolio_products['%s+%s'%(portfolios,additional_portfolios)]['price_id']
                }
            )

        if request.GET.get('coupon') == 'true':
            line_items.append(
                {
                    'quantity': 1,
                    'price': coupon_product['price_id']
                }
            )
        print(request.GET.get('coupon'))
        request.session['coupon_product'] = request.GET.get('coupon') == 'true'

        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id if request.user.is_authenticated else None,
            success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + 'cancelled/',
            payment_method_types=['card'],
            mode='payment',
            line_items=line_items,
            allow_promotion_codes=True,
            payment_intent_data={'statement_descriptor_suffix': 'ENTRY','description': 'ENTRY'},
        )
        request.user.payment_upgrade_plan = json.dumps( {'entries': request.session['total_entries'], 'portfolios': request.session['total_portfolios'] })
        request.user.payment_upgrade_status = 'checkingout %s'%datetime.datetime.now()
        request.user.save()
        return JsonResponse({'sessionId': checkout_session['id']})
    #    except Exception as e:
    #        return JsonResponse({'error': str(e)})

#### CANCELLED ##############################################
@login_required
def cancelled(request):

    user = request.user

    if user.payment_upgrade_status is not None:
        if 'checkout' in user.payment_upgrade_status or 'pending' in user.payment_upgrade_status:
            user.payment_upgrade_status='cancelled %s'%datetime.datetime.now()
    else:
        user.payment_status='cancelled %s'%datetime.datetime.now()

    user.save()
    return render(request, 'cancelled.html')

#### SUCCESS ##############################################
@login_required
def success(request):
    gtag_body = """
    <script>
 gtag('event', 'purchase', {
  "transaction_id": "%(email)s",
  "affiliation": "NLPA Submission System",
  "value": %(value)s,
  "currency": "USD",
  "shipping": 0.00,
  "tax": 0.00,
  "items": [
%(items)s
  ]
});
</script>
"""

    gtag_entry_item = """
    {
      "item_id": "%(item_id)s",
      "item_name": "%(item_desc)s",
      "item_category": "entry",
      "quantity": 1,
      "price": %(item_unit_price)s
    }
"""

    gtag_portfolio_item = """
    {
      "item_id": "%(item_id)s",
      "item_name": "%(item_desc)s",
      "item_category": "portfolio",
      "quantity": 1,
      "price": %(item_unit_price)s
    }
"""

    gtag_coupon_item = """
        {
          "item_id": "%(item_id)s",
          "item_name": "%(item_desc)s",
          "item_category": "coupon",
          "quantity": 1,
          "price": %(item_unit_price)s
        }
"""
    sn = ''
  

    if 'number_of_entries' in request.session:

        if 'entries' in request.session and  request.session['entries'] > request.session['number_of_entries']:
            number_of_entries = request.session['entries']
        else:
            number_of_entries = request.session['number_of_entries']
    else:
        number_of_entries = request.session['entries']

    if 'number_of_portfolios' in request.session:

        if 'portfolios' in request.session and request.session['portfolios'] > request.session['number_of_portfolios']:
            number_of_portfolios = request.session['portfolios']
        else:
            number_of_portfolios = request.session['number_of_portfolios']

    else:
        number_of_portfolios = request.session['portfolios']

 
    
    if 'number_of_additional_entries' in request.session:
        addentries = True
        number_of_additional_entries = request.session['number_of_additional_entries']
        number_of_additional_portfolios = request.session['number_of_additional_portfolios']
        entry_item = entry_products['%s+%s'%(str(number_of_entries), str(number_of_additional_entries))]
        portfolio_item = portfolio_products['%s+%s'%(str(number_of_portfolios), str(number_of_additional_portfolios))]
    else:
        addentries = False
        number_of_additional_entries = 0
        number_of_additional_portfolios = 0
        entry_item = entry_products[str(number_of_entries)]
        portfolio_item = portfolio_products[str(number_of_portfolios)]
    
    
    
    items = []
    price = 0
    
    if entry_item['price'] > 0:
        items.append(gtag_entry_item % {
    
            "item_id": entry_item['product_id'],
            "item_desc": entry_item['name'],
            "item_unit_price": entry_item['price'] / 100
        })
        price = entry_item['price']
    
    
    if portfolio_item['price']>0:
        items.append(gtag_portfolio_item % {
            "item_id": portfolio_item['product_id'],
            "item_desc": portfolio_item['name'],
            "item_unit_price": portfolio_item['price'] / 100
        })
        price = price + portfolio_item['price']
    
    
    if request.session['coupon_product']:
        items.append(gtag_coupon_item % {
            "item_id": coupon_product['product_id'],
            "item_desc": coupon_product['name'],
            "item_unit_price": coupon_product['price'] / 100
        })
        price = price + coupon_product['price']
    
    gtag_items = ','.join(items)
    gtag = gtag_body % {"email": request.user.email, "value": price / 100, "items": gtag_items}
    
    if GOOGLEANALYTICS is True:
        request.session['gtag'] = gtag
    else:
        request.session['gtag'] = ''
    
    coupon_code = None
    
    if request.session['coupon_product']:
        wcapi = API(
            url="https://naturallandscapeawards.com/",
            consumer_key=WOO_CONSUMER_KEY,
            consumer_secret=WOO_CONSUMER_SECRET,
            wp_api=True,
            version="wc/v3",
            timeout=20
        )
    
        coupon_code = '%s%s%s' % (request.user.first_name, request.user.last_name, random.randint(1111, 9999))
    
        data = {
            "code": coupon_code,
            "discount_type": "percent",
            "amount": "50",
            "individual_use": True,
            "maximum_amount": "300.00",
            "date_expires": "2024-01-32T23:59:59",
            "usage_limit": "2",
        }
    
        result = wcapi.post("coupons", data).json()
    
    request.user.payment_status = 'payment_pending %s' % datetime.datetime.now()
    
    # NEED TO CHECK WHEThER THIS IS AN UPGRADE OR JUST A PURCHASE AND SET PAYMENT PLAN ACCORDINGLY
    if request.user.payment_upgrade_status is not None:
        if 'checkingout' in request.user.payment_upgrade_status or 'checkout.session.completed' in request.user.payment_upgrade_status:
            request.user.payment_plan = request.user.payment_upgrade_plan
    
    request.user.save()
    
    if request.user.email:
        email = request.user.email
    else:
        email_object = EmailAddress.objects.get(user=request.user, primary=True)
        email = email_object.email
        request.user.email = email
        request.user.save()
    user_dict = {
    'email': email,
    'name': '%s %s'%(request.user.first_name,request.user.last_name),
    'coupon_code': coupon_code,
    }

    try: 
        welcome.send_email(user_dict)
    except smtplib.SMTPNotSupportedError:
        pass
    request.session['nextpage'] = 'entries'
    if addentries:
        request.session['htmlid'] = 'addentries_true'
    else:
        request.session['htmlid'] = 'addentries_false'

    # How we know the
    request.user.coupon = coupon_code
    request.user.save()

    return render(request, 'success.html')





@login_required
def success_youth(request):

    request.user.payment_status='payment_pending %s'%datetime.datetime.now()
    request.user.payment_plan= json.dumps( {'entries': '12', 'portfolios': '0'})
    request.user.save()
    request.session['nextpage'] = 'entries'

    return render(request, 'success_youth.html')

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('invalid payload')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print('verification error')
        return HttpResponse(status=400)

    try:
        user_id = int(event['data']['object']['client_reference_id'])
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print('no user')
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        if user.payment_upgrade_status:
            if 'checkingout' in user.payment_upgrade_status or 'checkout' in user.payment_upgrade_status or 'pending' in user.payment_upgrade_status:
                user.payment_upgrade_status='checkout.session.completed %s'%datetime.datetime.now()
        user.payment_status='checkout.session.completed %s'%datetime.datetime.now()
        user.save()

    return HttpResponse(status=200)
