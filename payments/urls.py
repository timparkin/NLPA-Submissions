from django.urls import path

from . import views

urlpatterns = [
    path('paymentplanconfirm/', views.payment_plan_confirm, name='paymentplanconfirm'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.success, name='success'),
    path('cancelled/', views.cancelled, name='cancelled'),
    path('webhook/', views.stripe_webhook),
]
