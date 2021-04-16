from django.conf import settings # new
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse, HttpResponse


class HomePageView(TemplateView):
    template_name = 'home.html'
