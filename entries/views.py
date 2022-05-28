from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View,TemplateView
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt

from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe

from entries.models import Entry
from userauth.models import CustomUser as User

from django.core.files.uploadedfile import InMemoryUploadedFile
import json
from nlpa.custom_storages import create_custom_storage, CustomS3Boto3Storage

from django.forms import BaseInlineFormSet

from django.db.models import Q

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from nlpa.settings.config import entry_products, portfolio_products, ENTRIES_CLOSED, CURRENT_YEAR

from . import confirmation

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
                if long_edge <3000:
                    f.add_error('photo','The long side of the image is %i pixels. The minimum is 3000.' % long_edge)
                if long_edge >4000:
                    f.add_error('photo','The long side of the image is %i pixels. The maximum is 4000.' % long_edge)

class ValidateRawsModelFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        # example custom validation across forms in the formset
        for f in self.forms:
            if f.cleaned_data['photo'] == "raws/default-entry.png":
                continue
            # your custom formset validation
            if not f.cleaned_data['photo']:
                raise forms.ValidationError("No image!")






category_list = ['GS', 'IL', 'AD']

entries_categories = (
        ('GS','Grand Scenic'),
        ('IL','Intimate Landscapes'),
        ('AD','Abstracts & Details'),
)

class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = 'django/forms/widgets/clearable_file_input.html'

class FileWidget(forms.widgets.ClearableFileInput):
    template_name = 'django/forms/widgets/clearable_file_input.html'



@login_required
def get_entries(request):




    payment_status = request.user.payment_status
    if payment_status is None or ('checkout.session.completed' not in payment_status and 'payment_pending' not in payment_status):
        return HttpResponseRedirect('/paymentplan')
    if ENTRIES_CLOSED:
        return HttpResponseRedirect('/secondround')
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

    request.session['ENTRIES_CLOSED'] = ENTRIES_CLOSED

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EntryInlineFormSet(request.POST, request.FILES, instance=user, queryset=Entry.objects.filter(year=CURRENT_YEAR, category__in=category_list))

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
                f.year = CURRENT_YEAR

            form.save()



            # redirect to a new URL:
            return HttpResponseRedirect('/entries/')

    # if a GET (or any other method) we'll create a blank form
    else:

        form = EntryInlineFormSet(instance=user, queryset=Entry.objects.filter( year=CURRENT_YEAR, category__in=category_list ))

    return render(request, 'entries.html', {'formset': form, 'ENTRIES_CLOSED': ENTRIES_CLOSED})







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
        if ENTRIES_CLOSED:
            return HttpResponseRedirect('/secondround')

        ctxt['portfolio1'] = EntryInlineFormSet(prefix='1',instance=request.user, queryset=Entry.objects.filter(year=CURRENT_YEAR, category='P1'))
        ctxt['portfolio2'] = EntryInlineFormSet(prefix='2',instance=request.user, queryset=Entry.objects.filter(year=CURRENT_YEAR, category='P2'))

        ctxt['description_form1'] = ProjectDescription(prefix='1',initial={'title': request.user.project_title_one,'description': request.user.project_description_one})
        ctxt['description_form2'] = ProjectDescription(prefix='2',initial={'title': request.user.project_title_two,'description': request.user.project_description_two})
        ctxt['payment_plan_portfolios'] = int(json.loads(self.request.user.payment_plan)['portfolios'])
        ctxt['ENTRIES_CLOSED'] = ENTRIES_CLOSED

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

        if ENTRIES_CLOSED:
            return HttpResponseRedirect('/secondround')


        description_form1 = ProjectDescription(request.POST,prefix='1')
        if description_form1.is_valid():
            title1 = description_form1.cleaned_data['title']
            description1 = description_form1.cleaned_data['description']
            request.user.project_title_one = title1
            request.user.project_description_one = description1
            request.user.save()
        else:
            ctxt['description_form1'] = ProjectDescription(prefix='1',initial={'title': request.user.project_title_one,'description': request.user.project_description_one})



        portfolio1 = EntryInlineFormSet(request.POST, request.FILES, prefix='1', instance=request.user, queryset=Entry.objects.filter(year=CURRENT_YEAR, category='P1'))
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
                f.year = CURRENT_YEAR
            portfolio1.save()
        else:
            ctxt['portfolio1'] = portfolio1


        if '2-title' in request.POST:
            description_form2 = ProjectDescription(request.POST,prefix='2')
            if description_form2.is_valid():
                title2 = description_form2.cleaned_data['title']
                description2 = description_form2.cleaned_data['description']
                request.user.project_title_two = title2
                request.user.project_description_two = description2
                request.user.save()
            else:
                ctxt['description_form2'] = ProjectDescription(prefix='2',initial={'title': request.user.project_title_two,'description': request.user.project_description_two})



            portfolio2 = EntryInlineFormSet(request.POST, request.FILES, prefix='2', instance=request.user, queryset=Entry.objects.filter(year=CURRENT_YEAR, category='P2'))
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
                    f.year = CURRENT_YEAR

                portfolio2.save()
            else:
                ctxt['portfolio2'] = portfolio2

        ctxt['payment_plan_portfolios'] = int(json.loads(self.request.user.payment_plan)['portfolios'])

        ctxt['ENTRIES_CLOSED'] = ENTRIES_CLOSED

        return HttpResponseRedirect('/portfolios/')



#
# First thing - get all the entries and portfolios including descriptions etc..
# Build an email template showing all submitted images and categories extra_css
#
#

class ConfirmationEmail(LoginRequiredMixin, View):
    template_name = 'confirmationemail.html'

    def get_context_data(self, **kwargs):
        if self.request.user.payment_plan is not None:
            kwargs['payment_plan'] = json.loads(self.request.user.payment_plan)
        else:
            kwargs['payment_plan'] = None

        return kwargs

    def get(self, request, *args, **kwargs):
        ctxt = {}
        user = request.user
        payment_plan = json.loads(user.payment_plan)
        entries_plan = int(payment_plan['entries'])
        portfolios_plan = int(payment_plan['portfolios'])
        plantext = "Your current plan is "
        if entries_plan >0:
            if entries_plan == 1:
                plantext += "%s single entry"%entries_plan
            else:
                plantext += "%s single entries"%entries_plan
        if portfolios_plan>0:
            if entries_plan >0:
                plantext += " and "
            if portfolios_plan == 1:
                plantext += "%s project entry"%portfolios_plan
            else:
                plantext += "%s project entries"%portfolios_plan

        entries = request.user.entry_set.filter( year=CURRENT_YEAR, category__in=category_list )
        num_entries = len(entries)
        project_entries_one = request.user.entry_set.filter( year=CURRENT_YEAR, category='P1' )
        num_portfolio_one = len(project_entries_one)
        project_entries_two = request.user.entry_set.filter( year=CURRENT_YEAR, category='P2' )
        num_portfolio_two = len(project_entries_two)


        entries_complete = (num_entries == entries_plan)

        if portfolios_plan >= 1:
            project_one_complete = (num_portfolio_one >= 6)
        else:
            project_one_complete = None

        if portfolios_plan >= 2:
            project_two_complete = (num_portfolio_two >= 6)
        else:
            project_two_complete = None

        entries_exceed_max = 0
        entries_perfect = 0
        entries_acceptable = 0
        entries_too_small = 0
        for entry in entries:
            print(entry.photo_dimensions)
            if 'x' in entry.photo_dimensions:
                wtext,htext = entry.photo_dimensions.split(' x ')
                w = int(wtext)
                h = int(htext)
            if w>4000 or h>4000:
                entries_exceed_max +=1
            elif (w==4000 and h<=4000) or (w<=4000 and h==4000):
                entries_perfect +=1
            elif w>=3000 or h>=3000:
                entries_acceptable +=1
            else:
                entries_too_small +=1


        project_one_entries_exceed_max = 0
        project_one_entries_perfect = 0
        project_one_entries_acceptable = 0
        project_one_entries_too_small = 0
        for entry in project_entries_one:
            if 'x' in entry.photo_dimensions:
                wtext,htext = entry.photo_dimensions.split(' x ')
                w = int(wtext)
                h = int(htext)
            if w>4000 or h>4000:
                project_one_entries_exceed_max +=1
            elif (w==4000 and h<=4000) or (w<=4000 and h==4000):
                project_one_entries_perfect +=1
            elif w>=3000 or h>=3000:
                project_one_entries_acceptable +=1
            else:
                project_one_entries_too_small +=1

        project_two_entries_exceed_max = 0
        project_two_entries_perfect = 0
        project_two_entries_acceptable = 0
        project_two_entries_too_small = 0
        for entry in project_entries_one:
            if 'x' in entry.photo_dimensions:
                wtext,htext = entry.photo_dimensions.split(' x ')
                w = int(wtext)
                h = int(htext)
            if w>4000 or h>4000:
                project_two_entries_exceed_max +=1
            elif (w==4000 and h<=4000) or (w<=4000 and h==4000):
                project_two_entries_perfect +=1
            elif w>=3000 or h>=3000:
                project_two_entries_acceptable +=1
            else:
                project_two_entries_too_small +=1

        category_text_map = {}
        for e in entries_categories:
            category_text_map[e[0]] = e[1]



        ctxt.update({
            'name': '%s %s'%(user.first_name,user.last_name),
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'payment_status': user.payment_status,
            'payment_plan': user.payment_plan,
            'plantext': plantext,
            'entries_plan': entries_plan,
            'portfolios_plan': portfolios_plan,
            'project_title_one': user.project_title_one,
            'project_description_one': user.project_description_one,
            'project_title_two': user.project_title_two,
            'project_description_two': user.project_description_two,
            'entries': entries,
            'project_entries_one': project_entries_one,
            'project_entries_two': project_entries_two,
            'num_entries': num_entries,
            'num_portfolio_one': num_portfolio_one,
            'num_portfolio_two': num_portfolio_two,

            'entries_exceed_max': entries_exceed_max,
            'entries_perfect': entries_perfect,
            'entries_acceptable': entries_acceptable,
            'entries_too_small': entries_too_small,

            'project_one_complete': project_one_complete,
            'project_two_complete': project_two_complete,
            'project_one_entries_exceed_max': project_one_entries_exceed_max,
            'project_one_entries_perfect': project_one_entries_perfect,
            'project_one_entries_acceptable': project_one_entries_acceptable,
            'project_one_entries_too_small': project_one_entries_too_small,
            'project_two_entries_exceed_max': project_two_entries_exceed_max,
            'project_two_entries_perfect': project_two_entries_perfect,
            'project_two_entries_acceptable': project_two_entries_acceptable,
            'project_two_entries_too_small': project_two_entries_too_small,

            'entries_size_error': entries_exceed_max+entries_too_small,
            'project_one_entries_size_error': project_one_entries_exceed_max+project_one_entries_too_small,
            'project_two_entries_size_error': project_two_entries_exceed_max+project_two_entries_too_small,

            'category_text_map': category_text_map,
        })




        return render(request, self.template_name, self.get_context_data(**ctxt))

    def post(self, request, *args, **kwargs):
        ctxt = {}
        user = request.user
        payment_plan = json.loads(user.payment_plan)
        entries = int(payment_plan['entries'])
        portfolios = int(payment_plan['portfolios'])
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

        user_dict = {
            'name': '%s %s'%(user.first_name,user.last_name),
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'payment_status': user.payment_status,
            'payment_plan': user.payment_plan,
            'project_title_one': user.project_title_one,
            'project_description_one': user.project_description_one,
            'project_title_two': user.project_title_two,
            'project_description_two': user.project_description_two,
            'entries': user.entry_set.filter( year=CURRENT_YEAR, category__in=category_list )
        }

        confirmation.send_email(user_dict)

        return HttpResponseRedirect('/confirmationemail/')



@login_required
def get_raws(request):


    payment_status = request.user.payment_status
    if payment_status is None or ('checkout.session.completed' not in payment_status and 'payment_pending' not in payment_status):
        return HttpResponseRedirect('/paymentplan')
    user = request.user
    if request.user.payment_plan is not None:
        payment_plan = json.loads(request.user.payment_plan)
    else:
        payment_plan = None
    request.session['payment_plan'] = payment_plan
    request.session['ENTRIES_CLOSED'] = ENTRIES_CLOSED


    EntryInlineFormSet = inlineformset_factory(User,
                            Entry,
                            fields=(
                                    'evidence_file_1',
                                    'ef1_filename',
                                    'evidence_file_2',
                                    'ef2_filename',
                                    'evidence_file_3',
                                    'ef3_filename',
                                    'evidence_file_4',
                                    'ef4_filename',
                                    'evidence_file_5',
                                    'ef5_filename',
                                    ),
                            can_delete=False,
                            #formset = ValidateRawsModelFormset,
                            widgets={

                                'evidence_file_1':FileWidget,
                                'ef1_filename':forms.HiddenInput,
                                'evidence_file_2':FileWidget,
                                'ef2_filename':forms.HiddenInput,
                                'evidence_file_3':FileWidget,
                                'ef3_filename':forms.HiddenInput,
                                'evidence_file_4':FileWidget,
                                'ef4_filename':forms.HiddenInput,
                                'evidence_file_5':FileWidget,
                                'ef5_filename':forms.HiddenInput,

                                },
                                extra=0)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = EntryInlineFormSet(request.POST, request.FILES, instance=user, queryset=Entry.objects.filter(year=CURRENT_YEAR, in_second_round=True))

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            myformset = form.save(commit=False)
            for f in myformset:
                ef1_name = f.evidence_file_1.name
                ef2_name = f.evidence_file_2.name
                ef3_name = f.evidence_file_3.name
                ef4_name = f.evidence_file_4.name
                ef5_name = f.evidence_file_5.name

                if hasattr(f.evidence_file_1.storage,'custom'):
                    f.evidence_file_1.storage.custom[ ef1_name ] = {'ef1_filename': ef1_name }
                else:
                    f.evidence_file_1.storage.custom = { ef1_name : {'ef1_filename': ef1_name} }
                f.ef1_filename = f.evidence_file_1.name

                if hasattr(f.evidence_file_2.storage,'custom'):
                    f.evidence_file_2.storage.custom[ ef2_name ] = {'ef2_filename': ef2_name }
                else:
                    f.evidence_file_2.storage.custom = { ef2_name : {'ef2_filename': ef2_name} }
                f.ef2_filename = f.evidence_file_2.name

                if hasattr(f.evidence_file_3.storage,'custom'):
                    f.evidence_file_3.storage.custom[ ef3_name ] = {'ef3_filename': ef3_name }
                else:
                    f.evidence_file_3.storage.custom = { ef3_name : {'ef3_filename': ef3_name} }
                f.ef3_filename = f.evidence_file_3.name

                if hasattr(f.evidence_file_4.storage,'custom'):
                    f.evidence_file_4.storage.custom[ ef4_name ] = {'ef4_filename': ef4_name }
                else:
                    f.evidence_file_4.storage.custom = { ef4_name : {'ef4_filename': ef4_name} }
                f.ef4_filename = f.evidence_file_4.name

                if hasattr(f.evidence_file_5.storage,'custom'):
                    f.evidence_file_5.storage.custom[ ef5_name ] = {'ef5_filename': ef5_name }
                else:
                    f.evidence_file_5.storage.custom = { ef5_name : {'ef5_filename': ef5_name} }
                f.ef5_filename = f.evidence_file_5.name


            form.save()



            # redirect to a new URL:
            return HttpResponseRedirect('/secondround/')


    # if a GET (or any other method) we'll create a blank form
    else:
        form = EntryInlineFormSet(instance=user, queryset=Entry.objects.filter(year=CURRENT_YEAR, in_second_round=True))

    return render(request, 'secondround.html', {'formset': form, 'ENTRIES_CLOSED': ENTRIES_CLOSED})
