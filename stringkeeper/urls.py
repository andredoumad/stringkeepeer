"""stringkeeper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include #url
from django.views.generic import TemplateView
from blog.views import (
    blog_post_create_view,
)

# from subscription.views import (
#     SubscriptionListView, 
#     subscription_list_view, 
    
#     SubscriptionDetailView, 
#     subscription_detail_view,

#     SubscriptionFeaturedListView,    
#     SubscriptionFeaturedDetailView,
#     SubscriptionDetailSlugView

# )

from django.views.generic.base import TemplateView # new

from searches.views import search_view

from .views import (
    home_page,
    about_page,
    contact_page,
    #example_page,
    login_page,
    register_page
)


urlpatterns = [
    path('admin/', admin.site.urls, name='site_admin'),
    path('', home_page, name='home'),

    path('blog-new/', blog_post_create_view),
    path('blog/', include('blog.urls', namespace='blog'), name='blog'),
    # path('search/', search_view),
    # path('search/', include('searches.urls', namespace='searches')),
    #old django == re_path(r'^blog/(?P<slug>\w+)/$', blog_post_detail_page),
    #path('page/', about_page),
    #path('pages/', about_page),
    #re_path(r'^pages?/$', about_page),
    #re_path('^about/$', about_page),
    #path('example/', example_page),
    path('contact/', contact_page, name='contact'),
    path('login/', login_page, name='auth_login'),
    path('register/', register_page, name='auth_register'),
    path('bootstrap/', TemplateView.as_view(template_name='bootstrap/example.html')),
    #path('subscriptions/', include('subscription.urls')),
    path('subscriptions/', include('subscription.urls', namespace='subscription'), name='subscription'),
    path('search/', include('search.urls', namespace='search'), name='search'),
    #two examples here:
    #djangoproject.com django-views-generic list view
    # path('featured/', SubscriptionFeaturedListView.as_view()),
    # re_path(r'^featured/(?P<pk>\d+)/$', SubscriptionFeaturedDetailView.as_view()), # as view means callable

    # path('subscription/', SubscriptionListView.as_view()), # as view means callable 
    # path('subscription-fbv/', subscription_list_view),

    # #re_path(r'^subscription/(?P<pk>\d+)/$', SubscriptionDetailView.as_view()), # as view means callable 
    # re_path(r'^subscription/(?P<slug>[\w-]+)/$', SubscriptionDetailSlugView.as_view()), 
    # re_path(r'^subscription-fbv/(?P<pk>\d+)/$', subscription_detail_view),

    path('accounts/', include('django.contrib.auth.urls')),





]

#if settings.DEBUG:
    #from django.conf.urls.static import static
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
