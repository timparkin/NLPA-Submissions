from django.urls import path

from . import views

urlpatterns = [
    path('entries/', views.get_entries, name='entries'),
    path('portfolios/', views.GetPortfolios.as_view(), name='portfolios'),
    path('confirmationemail/', views.ConfirmationEmail.as_view(), name='confirmationemail'),
    path('previousyears/', views.PreviousYears.as_view(), name='previousyears'),
    path('secondround/', views.get_raws, name='secondround'),
]
