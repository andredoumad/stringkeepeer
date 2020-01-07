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
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path, include #url
from django.views.generic import TemplateView, RedirectView
from blog.views import (
    blog_post_create_view,
)

from django.views.generic.base import TemplateView # new

from searches.views import search_view

from carts.views import cart_home

from accounts.views import LoginView, RegisterView, guest_register_view
from billing.views import payment_method_view, payment_method_createview
from addresses.views import checkout_address_create_view, checkout_address_reuse_view

from carts.views import cart_detail_api_view
from marketing.views import MarketingPreferenceUpdateView, MailchimpWebhookView

from .views import (
    home_page,
    about_page,
    contact_page,
    #example_page,
    #login_page,
    #register_page
)

admin.site.site_header = 'Administration'                    # default: "Django Administration"
admin.site.index_title = 'Administration'                 # default: "Site administration"
admin.site.site_title = 'Administration' # default: "Django site admin"


urlpatterns = [
    path('', home_page, name='home'),
    path('blog-new/', blog_post_create_view),
    path('blog/', include('blog.urls', namespace='blog'), name='blog'),
    path('about/', about_page, name='about'),
    path('accounts/', RedirectView.as_view(url='/account')),
    path('account/', include('accounts.urls', namespace='account'), name='account'),
    path('accounts/', include('accounts.passwords.urls')),
    path('contact/', contact_page, name='contact'),
    # path('login/', login_page, name='login'),
    #how come i cant use anything beyond auth_login - everytime i try just login it breaks
    #even if i change the navbar template, its not right...
    path('login/', LoginView.as_view(), name='auth_login'),
    path('register/guest/', guest_register_view, name='guest_register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/cart/', cart_detail_api_view, name='api-cart'),
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('cart/', include('carts.urls', namespace='cart'), name='cart'),
    path('billing/payment-method/', payment_method_view, name='billing-payment-method'),
    path('billing/payment-method/create/', payment_method_createview, name='billing-payment-method-endpoint'),
    path('register/', RegisterView.as_view(), name='register'),
    path('bootstrap/', TemplateView.as_view(template_name='bootstrap/example.html')),
    path('subscriptions/', include('subscription.urls', namespace='subscription'), name='subscription'),
    path('search/', include('search.urls', namespace='search'), name='search'),
    path('settings/', RedirectView.as_view(url='/account')),
    path('settings/email/', MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    path('webhooks/mailchimp/', MailchimpWebhookView.as_view(), name='webhooks-mailchimp'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls, name='site_admin'),

]

#if settings.DEBUG:
    #from django.conf.urls.static import static
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
