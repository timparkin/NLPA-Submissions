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

from django.forms import BaseInlineFormSet

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from nlpa.settings.config import entry_products, portfolio_products

class ValidateImagesModelFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # example custom validation across forms in the formset
        for f in self.forms:
            if f.cleaned_data['photo'] == "entries/default-entry.png":
                continue
            # your custom formset validation
            if not f.cleaned_data['photo']:
                raise forms.ValidationError("No image!")
            else:
                w, h = get_image_dimensions(f.cleaned_data['photo'])
                if w > h:
                    long_edge = w
                else:
                    long_edge = h
                if long_edge <1600:
                    f.add_error('photo','The long side of the image is %i pixels. We recommend 2048.' % long_edge)




category_list = ['GL', 'IA', 'N', 'A']

entries_categories = (
        ('GL','Grand Landscape'),
        ('IA','Intimate & Abstract'),
        ('N','Nightscape'),
        ('A','Aerial'),

)

class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = 'django/forms/widgets/clearable_file_input.html'



@login_required
def get_entries(request):




    payment_status = request.user.payment_status
    if payment_status is None or ('checkout.session.completed' not in payment_status and 'payment_pending' not in payment_status):
        return HttpResponseRedirect('/paymentplan')
    user = request.user
    if request.user.payment_plan is not None:
        payment_plan = json.loads(request.user.payment_plan)
    else:
        payment_plan = None
    request.session['payment_plan'] = payment_plan



    EntryInlineFormSet = inlineformset_factory(User,
                            Entry,
                            fields=('photo','filename', 'category','photo_size','photo_dimensions'),
#                            formset=ValidateImagesModelFormset,
                            can_delete=False,
                            max_num=int(payment_plan['entries']),
                            validate_max=True,
                            min_num=int(payment_plan['entries']),
                            widgets={
                                'filename':forms.HiddenInput,
                                'photo_dimensions':forms.HiddenInput,
                                'photo_size':forms.HiddenInput,
                                'photo':ImageWidget,
                                })

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EntryInlineFormSet(request.POST, request.FILES, instance=user, queryset=Entry.objects.filter(category__in=category_list))

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            myformset = form.save(commit=False)
            for f in myformset:
                name = f.photo.name
                tagdata = {
                    'filename': name,
                    'user_email': request.user.email,
                    'category': f.category,
                    'is_young_entrant': request.user.is_young_entrant
                    }
                if hasattr(f.photo.storage,'custom'):
                    f.photo.storage.custom[ name ] = tagdata
                else:
                    f.photo.storage.custom = { name : tagdata }
                f.photo_dimensions = '%s x %s'%(f.photo.width, f.photo.height)
                f.photo_size = f.photo.size
                f.filename = f.photo.name

            form.save()



            # redirect to a new URL:
            return HttpResponseRedirect('/entries/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EntryInlineFormSet(instance=user, queryset=Entry.objects.filter(category__in=category_list))

    return render(request, 'entries.html', {'formset': form})







class ProjectDescription(forms.Form):
    title = forms.CharField()
    description = forms.CharField(help_text="Please enter a description of your project", widget=forms.Textarea(attrs={
                'rows': '5',
                'cols': '90',
                'maxlength': '1000',
            }))







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


        EntryInlineFormSet = inlineformset_factory(User,
                                Entry,
                                fields=('photo','filename','photo_size','photo_dimensions'),
                                can_delete=False,
                                max_num=10,
                                validate_max=True,
                                min_num=10,
                                widgets={
                                    'filename':forms.HiddenInput,
                                    'photo_dimensions':forms.HiddenInput,
                                    'photo_size':forms.HiddenInput,
                                    'photo':ImageWidget,
                                    })

        payment_status = request.user.payment_status
        if payment_status is None or ('checkout.session.completed' not in payment_status and 'payment_pending' not in payment_status):
            return HttpResponseRedirect('/paymentplan')
        ctxt['portfolio1'] = EntryInlineFormSet(instance=request.user, queryset=Entry.objects.filter(category='P1'))
        ctxt['portfolio2'] = EntryInlineFormSet(instance=request.user, queryset=Entry.objects.filter(category='P2'))

        ctxt['description_form1'] = ProjectDescription(initial={'title': request.user.project_title_one,'description': request.user.project_description_one})
        ctxt['description_form2'] = ProjectDescription(initial={'title': request.user.project_title_two,'description': request.user.project_description_two})
        ctxt['payment_plan_portfolios'] = int(json.loads(self.request.user.payment_plan)['portfolios'])


        return render(request, self.template_name, self.get_context_data(**ctxt))

    def post(self, request, *args, **kwargs):
        ctxt = {}



        EntryInlineFormSet = inlineformset_factory(User,
                                Entry,
                                fields=('photo','filename','photo_size','photo_dimensions'),
                                can_delete=False,
                                max_num=10,
                                validate_max=True,
                                min_num=10,
                                widgets={
                                    'filename':forms.HiddenInput,
                                    'photo_dimensions':forms.HiddenInput,
                                    'photo_size':forms.HiddenInput,
                                    'photo':ImageWidget,
                                    })

        if 'description1' in request.POST:
            description_form1 = ProjectDescription(request.POST)
            if description_form1.is_valid():
                title1 = description_form1.cleaned_data['title']
                description1 = description_form1.cleaned_data['description']
                request.user.project_title_one = title1
                request.user.project_description_one = description1
                request.user.save()
            else:
                ctxt['description_form1'] = ProjectDescription(initial={'title': request.user.project_title_one,'description': request.user.project_description_one})



        if 'portfolio1' in request.POST:
            portfolio1 = EntryInlineFormSet(request.POST, request.FILES, instance=request.user, queryset=Entry.objects.filter(category='P1'))
            if portfolio1.is_valid():
                myformset = portfolio1.save(commit=False)
                for f in myformset:
                    f.category = 'P1'
                    name = f.photo.name
                    tagdata = {
                        'filename': name,
                        'user_email': request.user.email,
                        'category': f.category,
                        'is_young_entrant': request.user.is_young_entrant
                        }
                    if hasattr(f.photo.storage,'custom'):
                        f.photo.storage.custom[ name ] = tagdata
                    else:
                        f.photo.storage.custom = { name : tagdata }

                    f.photo_dimensions = '%s x %s'%(f.photo.width, f.photo.height)
                    f.photo_size = f.photo.size
                    f.filename = f.photo.name
                portfolio1.save()
            else:
                ctxt['portfolio1'] = portfolio1

        if 'description2' in request.POST:
            description_form2 = ProjectDescription(request.POST)
            if description_form2.is_valid():
                title2 = description_form2.cleaned_data['title']
                description2 = description_form2.cleaned_data['description']
                request.user.project_title_two = title2
                request.user.project_description_two = description2
                request.user.save()
            else:
                ctxt['description_form2'] = ProjectDescription(initial={'title': request.user.project_title_two,'description': request.user.project_description_two})



        if 'portfolio2' in request.POST:
            description2 = ProjectDescription(request.POST)
            portfolio2 = EntryInlineFormSet(request.POST, request.FILES, instance=request.user, queryset=Entry.objects.filter(category='P2'))
            if portfolio2.is_valid():
                myformset = portfolio2.save(commit=False)
                for f in myformset:
                    f.category = 'P2'
                    name = f.photo.name
                    tagdata = {
                        'filename': name,
                        'user_email': request.user.email,
                        'category': f.category,
                        'is_young_entrant': request.user.is_young_entrant
                        }
                    if hasattr(f.photo.storage,'custom'):
                        f.photo.storage.custom[ name ] = tagdata
                    else:
                        f.photo.storage.custom = { name : tagdata }
                    f.photo_dimensions = '%s x %s'%(f.photo.width, f.photo.height)
                    f.photo_size = f.photo.size
                    f.filename = f.photo.name
                portfolio2.save()
            else:
                ctxt['portfolio2'] = portfolio2
        ctxt['payment_plan_portfolios'] = int(json.loads(self.request.user.payment_plan)['portfolios'])


        return HttpResponseRedirect('/portfolios/')
