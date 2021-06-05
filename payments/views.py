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

from nlpa.settings.config import entry_products, portfolio_products




class PurchasePageView(TemplateView):
    template_name = 'purchase.html'




@login_required
def cancelled(request):
    request.user.payment_status='cancelled %s'%datetime.datetime.now()
    request.user.save()
    return render(request, 'cancelled.html')

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
    request.session['upgrade_price'] = \
        float(
            entry_products[ str(request.session['number_of_additional_entries']) ]['price'] )/100 + \
        float(
            portfolio_products[ str(request.session['number_of_additional_portfolios']) ]['price'] )/100
    if request.session['youth_entry']:
        request.session['upgrade_price'] = request.session['total_price'] * 0.3
    request.session['upgrade_price'] = '${:.0f}'.format( request.session['upgrade_price'] )
    request.session['total_entries'] = request.session['number_of_additional_entries'] + request.session['entries']
    request.session['total_portfolios'] = request.session['number_of_additional_portfolios'] + request.session['portfolios']


    return render(request, 'paymentupgradeconfirm.html')



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
      "id": "%(item_id)s",
      "name": "%(item_desc)s",
      "category": "entry",
      "quantity": 1,
      "price": %(item_unit_price)s
    }
"""

    gtag_portfolio_item = """
    {
      "id": "%(item_id)s",
      "name": "%(item_desc)s",
      "category": "portfolio",
      "quantity": %(quantity)s,
      "price": %(item_unit_price)s
    }
"""


    entry_item = entry_products[ str(request.session['number_of_entries']) ]
    portfolio_item = portfolio_products[ str(request.session['number_of_portfolios']) ]

    items = []
    price = 0

    if entry_item['price'] > 0:
        items.append( gtag_entry_item % {

          "item_id": entry_item['product_id'],
          "item_desc": entry_item['name'],
          "item_unit_price": entry_item['price']/100
          } )
        price = entry_item['price']


    if portfolio_item['price'] == 3000:

        items.append( gtag_portfolio_item % {
              "item_id": portfolio_item['product_id'],
              "item_desc": portfolio_item['name'],
              "category": 'Portfolio',
              "quantity": 1,
              "item_unit_price": portfolio_item['price']/100
              } )
        price = price + portfolio_item['price']
    if portfolio_item['price'] == 6000:

        items.append( gtag_portfolio_item % {
              "item_id": portfolio_item['product_id'],
              "item_desc": portfolio_item['name'],
              "category": 'Portfolio',
              "quantity": 2,
              "item_unit_price": portfolio_item['price']/200
              } )
        price = price + portfolio_item['price']

    gtag_items = ','.join(items)
    gtag = gtag_body % { "email": request.user.email, "value": price/100, "items": gtag_items }
    request.session['gtag'] = gtag

    request.user.payment_status='payment_pending %s'%datetime.datetime.now()
    request.user.save()

    if entry_item['price'] == 0:
        request.session['nextpage'] = 'portfolios'
    else:
        request.session['nextpage'] = 'entries'

    return render(request, 'success.html')

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
@login_required
def create_checkout_session(request):
    if request.method == 'GET':
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


            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                allow_promotion_codes=True,
            )
            request.user.payment_plan = json.dumps( {'entries': request.session['number_of_entries'], 'portfolios': request.session['number_of_portfolios'] })
            request.user.payment_status = 'checkingout %s'%datetime.datetime.now()
            request.user.save()
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
@login_required
def create_checkout_session_upgrade(request):
    if request.method == 'GET':
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            line_items = []
            if (int(request.session['number_of_additional_entries'])>0):
                line_items=[
                    {
                        'quantity': 1,
                        'price': entry_products['+%s'%request.session['number_of_additional_entries']]['price_id']
                    }
                ]
            if (int(request.session['number_of_additional_portfolios'])>0):
                line_items.append(
                    {
                    'quantity': 1,
                    'price': portfolio_products['+%s'%request.session['number_of_additional_portfolios']]['price_id']
                    }
                )

            print(line_items)
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                allow_promotion_codes=True,
            )
            print('%s : %s' % (request.session['total_entries'], request.session['total_portfolios']))
            request.user.payment_upgrade_plan = json.dumps( {'entries': request.session['total_entries'], 'portfolios': request.session['total_portfolios'] })
            request.user.payment_upgrade_status = 'checkingout %s'%datetime.datetime.now()
            request.user.save()
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})



@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    print('in webook')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('invalid payload')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if request.user.payment_status == 'checkout.session.completed':
        print('upgrading')
        request.user.payment_upgrade_status='%s %s'%(event['type'],datetime.datetime.now())
        print('r.s.u.s %s' % request.user.payment_upgrade_status)
        request.user.payment_plan = request.user.payment_upgrade_plan
    else:
        request.user.payment_status='%s %s'%(event['type'],datetime.datetime.now())
        print('r.u.p.s %s' % request.user.payment_status)
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here
        # register the payment on the customer system
        # profile page can then show image upload info

    return HttpResponse(status=200)
