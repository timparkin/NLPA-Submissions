from django.urls import path

from . import views

urlpatterns = [
    path('entries/', views.get_entries, name='entries'),
    path('portfolios/', views.GetPortfolios.as_view(), name='portfolios'),
    path('secondround/', views.get_raws, name='secondround'),
]
