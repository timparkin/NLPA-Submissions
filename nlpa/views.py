from django.conf import settings # new
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from nlpa.forms import PaymentPlanForm
from userauth.models import CustomUser as User


class HomePageView(TemplateView):
    template_name = 'home.html'

class FAQPageView(TemplateView):
    template_name = 'faq.html'

class PaymentPlanConfirmView(TemplateView):
    template_name = 'paymentplanconfirm.html'



@login_required
def get_paymentplan(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PaymentPlanForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            request.session['number_of_entries'] = form.cleaned_data['number_of_entries']
            request.session['number_of_portfolios'] = form.cleaned_data['number_of_portfolios']

            # redirect to a new URL:
            return HttpResponseRedirect('/paymentplanconfirm/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PaymentPlanForm()

    return render(request, 'paymentplan.html', {'form': form})
