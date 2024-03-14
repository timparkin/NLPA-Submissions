from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.views import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from . import views
from entries import views as eviews

urlpatterns = [
    path('', eviews.get_entries, name='entries'),
    path('faq/', views.FAQPageView.as_view(), name='faq'),
    re_path(r'^.well-known/pki-validation/(?P<path>.*)$', static.serve, {'document_root': settings.BASE_DIR + "/nlpa/static/pki-validation"}),



    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path("django-admin/", include('loginas.urls')),
    path('django-admin/', admin.site.urls),
    path('search/', search_views.search, name='search'),

    path('paymentplan/', views.get_paymentplan, name='paymentplan'),
    path('paymentupgrade/', views.get_paymentupgrade, name='paymentupgrade'),
    path('072348-datamining/', views.datamining, name='datamining'),
    path('072348-datamining/nlpa_combined_mailing_list.csv', views.datamining_child, name='datamining_child'),
    path('072348-datamining/nlpa_combined_entries.csv', views.datamining_child_entries, name='datamining_child_entries'),
    path('072348-datamining/nlpa_missing_raws.csv', views.missing_raws, name='missing_raws'),
    path('072348-datamining/nlpa_combined_users.csv', views.datamining_child_users, name='datamining_child_users'),

    path("socialmedia", views.socialmedia, name="socialmedia"),

    path('', include('payments.urls')),
    path('', include('entries.urls')),

    path('accounts/', include('userauth.urls')),
    path('accounts/', include('allauth.urls')),
    re_path(r'^assets/(?P<path>.*)$', static.serve, {'document_root': settings.BASE_DIR + "/nlpa/static/public/assets"}),
    re_path(r'^vendors/(?P<path>.*)$', static.serve, {'document_root': settings.BASE_DIR + "/nlpa/static/public/vendors"}),
    re_path(r'^apps/(?P<path>.*)$', static.serve, {'document_root': settings.BASE_DIR + "/nlpa/static/public/apps"}),
# urls.py

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = urlpatterns + [

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
