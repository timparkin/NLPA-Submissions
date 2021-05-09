from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View,TemplateView
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin


from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe

from entries.models import Entry
from userauth.models import CustomUser as User

from django.core.files.uploadedfile import InMemoryUploadedFile
import json
from nlpa.custom_storages import create_custom_storage, CustomS3Boto3Storage



category_list = ['GL', 'IA', 'N', 'A']

class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = 'django/forms/widgets/clearable_file_input.html'





@login_required
def get_entries(request):
    payment_status = request.user.payment_status
    print(payment_status)
    if payment_status is None or ('checkout.session.completed' not in payment_status and 'payment_pending' not in payment_status):
        return HttpResponseRedirect('/paymentplan')
    user = request.user
    if request.user.payment_plan is not None:
        payment_plan = json.loads(request.user.payment_plan)
    else:
        payment_plan = None
    request.session['payment_plan'] = payment_plan



    EntryInlineFormSet = inlineformset_factory(User, Entry, fields=('photo','filename', 'category',), can_delete=False, max_num=int(payment_plan['entries']), min_num=int(payment_plan['entries']), widgets={'filename':forms.HiddenInput,'photo':ImageWidget})

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EntryInlineFormSet(request.POST, request.FILES, instance=user, queryset=Entry.objects.filter(category_list))
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            myformset = form.save(commit=False)
            for f in myformset:
                f.photo.storage.custom = {'filename': f.photo.name, 'user_email': request.user.email, 'category': f.category, 'is_young_entrant': request.user.is_young_entrant}
                f.filename = f.photo.name
            form.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/entries/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EntryInlineFormSet(instance=user, queryset=Entry.objects.filter(category__in=category_list))

    return render(request, 'entries.html', {'formset': form})









class GetPortfolios(LoginRequiredMixin, View):
    template_name = 'portfolios.html'





    def get_context_data(self, **kwargs):
        if self.request.user.payment_plan is not None:
            kwargs['payment_plan'] = json.loads(self.request.user.payment_plan)
        else:
            kwargs['payment_plan'] = None

        return kwargs

    def get(self, request, *args, **kwargs):
        ctxt = {}
        EntryInlineFormSet = inlineformset_factory(
                                 User,
                                 Entry,
                                 fields=('photo','filename', 'category',),
                                 can_delete=False,
                                 max_num=10,
                                 min_num=10,
                                 widgets={'filename':forms.HiddenInput,'photo':ImageWidget, 'category':forms.HiddenInput}
                                 )
        payment_status = request.user.payment_status
        if payment_status is None or ('checkout.session.completed' not in payment_status and 'payment_pending' not in payment_status):
            return HttpResponseRedirect('/paymentplan')
        ctxt['portfolio1'] = EntryInlineFormSet(instance=request.user, queryset=Entry.objects.filter(category='P1'))
        ctxt['portfolio2'] = EntryInlineFormSet(instance=request.user, queryset=Entry.objects.filter(category='P2'))


        return render(request, self.template_name, self.get_context_data(**ctxt))

    def post(self, request, *args, **kwargs):
        ctxt = {}
        EntryInlineFormSet = inlineformset_factory(
                                 User,
                                 Entry,
                                 fields=('photo','filename', 'category',),
                                 can_delete=False,
                                 max_num=10,
                                 min_num=10,
                                 widgets={'filename':forms.HiddenInput,'photo':ImageWidget,'category':forms.HiddenInput}
                                 )
        if 'portfolio1' in request.POST:
            portfolio1 = EntryInlineFormSet(request.POST, request.FILES, instance=request.user, queryset=Entry.objects.filter(category='P1'))
            if portfolio1.is_valid():
                myformset = portfolio1.save(commit=False)
                for f in myformset:
                    f.category = 'P1'
                    f.photo.storage.custom = {'filename': f.photo.name, 'user_email': request.user.email, 'category': f.category, 'is_young_entrant': request.user.is_young_entrant}
                    f.filename = f.photo.name
                portfolio1.save()
            else:
                ctxt['portfolio1'] = portfolio1

        elif 'portfolio2' in request.POST:
            portfolio2 = EntryInlineFormSet(request.POST, request.FILES, instance=request.user, queryset=Entry.objects.filter(category='P2'))
            if portfolio2.is_valid():
                myformset = portfolio2.save(commit=False)
                for f in myformset:
                    f.category = 'P2'
                    f.photo.storage.custom = {'filename': f.photo.name, 'user_email': request.user.email, 'category': f.category, 'is_young_entrant': request.user.is_young_entrant}
                    f.filename = f.photo.name
                portfolio2.save()
            else:
                ctxt['portfolio2'] = portfolio2

        return HttpResponseRedirect('/portfolios/')
