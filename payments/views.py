from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse, HttpResponse
import stripe

entry_products = {
'18': {'price_id':'price_1Ib3y1IyfIE0cGLTwiEUEsDA','product_id':'prod_JDUxYgaLhmsJXu','name':'Eighteen Images','price':10000},
'12': {'price_id':'price_1Ib3xdIyfIE0cGLTjx4XBqug','product_id':'prod_JDUxEseu8zbaYL','name':'Twelve Images','price':6000},
'6': {'price_id':'price_1Ib3vmIyfIE0cGLTQHyDqJh8','product_id':'prod_JDUvNXYOvwRyQm','name':'Six Images','price':4000},
}
portfolio_products = {
'1': {'price_id':'price_1Ib3z5IyfIE0cGLTZxKExvnG','product_id':'prod_JDUz2CF7GA0wOR','name':'One Project Submission','price':3000},
'2': {'price_id':'price_1Ib3zdIyfIE0cGLT4uc5jU6Q','product_id':'prod_JDUzO4PtT5PYv6','name':'Two Project Submissions','price':6000},
}


class PaymentPlanConfirmView(TemplateView):
    template_name = 'paymentplanconfirm.html'


class PurchasePageView(TemplateView):
    template_name = 'purchase.html'


class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelledView(TemplateView):
    template_name = 'cancelled.html'


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://192.168.64.3:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
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

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here
        # register the payment on the customer system
        # profile page can then show image upload info

    return HttpResponse(status=200)
