from django.urls import path

from . import views

urlpatterns = [
    path('entries/', views.get_entries, name='entries'),
]
