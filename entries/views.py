from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms



from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe

from entries.models import Entry
from userauth.models import CustomUser as User

from django.core.files.uploadedfile import InMemoryUploadedFile



categories=['Grand Landscape','Intimate and Abstract','Nightscape','Aerial']

class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = 'django/forms/widgets/clearable_file_input.html'





@login_required
def get_entries(request):
    user = request.user
    entries = Entry.objects.filter(user=user.id)

    EntryInlineFormSet = inlineformset_factory(User, Entry, fields=('photo','category','filename'), can_delete=True, max_num=6, min_num=6, widgets={'filename':forms.HiddenInput,'photo':ImageWidget})

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EntryInlineFormSet(request.POST, request.FILES, instance=user)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            myformset = form.save(commit=False)
            for f in myformset:
                f.filename = f.photo.name
            form.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/entries/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EntryInlineFormSet(instance=user)

    return render(request, 'entries.html', {'formset': form})