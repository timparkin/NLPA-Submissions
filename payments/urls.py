from django.urls import path

from . import views

urlpatterns = [
    path('paymentplanconfirm/', views.payment_plan_confirm),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.success),
    path('cancelled/', views.cancelled),
    path('webhook/', views.stripe_webhook),
]
