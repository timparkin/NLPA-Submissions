from django.urls import path

from . import views

urlpatterns = [
    path('paymentplanconfirm/', views.payment_plan_confirm, name='paymentplanconfirm'),
    path('paymentplanconfirm_youth/', views.payment_plan_confirm_youth, name='paymentplanconfirm_youth'),
    path('paymentupgradeconfirm/', views.payment_upgrade_confirm, name='paymentupgradeconfirm'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('create-checkout-session-upgrade/', views.create_checkout_session_upgrade),
    path('success/', views.success, name='success'),
    path('success_youth/', views.success_youth, name='success_youth'),
    path('cancelled/', views.cancelled, name='cancelled'),
    path('webhook/', views.stripe_webhook),
]
