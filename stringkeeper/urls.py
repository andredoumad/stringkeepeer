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
# import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path, include #url
from django.views.generic import TemplateView, RedirectView
from blog.views import (
    blog_post_create_view,
)

from django.views.generic.base import TemplateView # new


from carts.views import cart_home

from accounts.views import LoginView, RegisterView, guest_register_view
from billing.views import payment_method_view, payment_method_createview, payment
from addresses.views import (
    AddressCreateView,
    AddressListView,
    AddressUpdateView,
    checkout_address_create_view, 
    checkout_address_reuse_view
    )
from analytics.views import SalesView, SalesAjaxView

from carts.views import cart_detail_api_view
from marketing.views import MarketingPreferenceUpdateView, MailchimpWebhookView
from orders.views import LibraryView
from webharvest.views import WebHarvestHomeView, WebHarvestWebhookView


from .views import (
    home_page,
    about_page,
    contact_page,
    preview_page,
    maintenance_page,
    #example_page,
    #login_page,
    #register_page
)

admin.site.site_header = 'Stringkeeper Admin'                    # default: "Django Administration"
admin.site.index_title = 'Stringkeeper Admin'                 # default: "Site administration"
admin.site.site_title = 'Stringkeeper Admin' # default: "Django site admin"

from django.conf.urls import url


# if socket.gethostname()=="www.stringkeeper.com":
#     User = get_user_model()
#     for user in User.objects.all():
#         user.bool_webharvest_chat_active = False
#         user.save(update_fields=["bool_webharvest_chat_active"])


urlpatterns = [
    # path('__debug__/', include(debug_toolbar.urls)),
    # path('', home_page, name='home'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    path('', RedirectView.as_view(url='webharvest/'), name='home'),
    path('maintenance_page/', maintenance_page, name='maintenance_page'),
    path('blog-new/', blog_post_create_view),
    path('blog/', include('blog.urls', namespace='blog'), name='blog'),
    path('about/', about_page, name='about'),
    path('accounts/', RedirectView.as_view(url='/account')),
    path('account/', include('accounts.urls', namespace='account'), name='account'),
    path('accounts/', include('accounts.passwords.urls')),
    re_path(r'^address/$', RedirectView.as_view(url='/addresses')),
    re_path(r'^addresses/$', AddressListView.as_view(), name='addresses'),
    re_path(r'^addresses/create/$', AddressCreateView.as_view(), name='address-create'),
    re_path(r'^addresses/(?P<pk>\d+)/$', AddressUpdateView.as_view(), name='address-update'),
    re_path(r'^analytics/sales/$', SalesView.as_view(), name='sales-analytics'),
    re_path(r'^analytics/sales/data/$', SalesAjaxView.as_view(), name='sales-analytics-data'),
    path('contact/', contact_page, name='contact'),
    path('preview/', preview_page, name='preview'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('register/guest/', guest_register_view, name='guest_register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/cart/', cart_detail_api_view, name='api-cart'),
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('cart/', include('carts.urls', namespace='cart'), name='cart'),
    path('billing/payment-method/', payment_method_view, name='billing-payment-method'),
    path('billing/payment/', payment, name='payment'),
    path('billing/payment-method/create/', payment_method_createview, name='billing-payment-method-endpoint'),
    path('register/', RegisterView.as_view(), name='register'),
    path('library/', LibraryView.as_view(), name='library'),
    path('orders/', include('orders.urls', namespace='orders'), name='orders'),
    path('subscriptions/', include('subscription.urls', namespace='subscription'), name='subscription'),
    path('search/', include('search.urls', namespace='search'), name='search'),
    path('settings/', RedirectView.as_view(url='/account')),
    path('settings/email/', MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    path('webhooks/mailchimp/', MailchimpWebhookView.as_view(), name='webhooks-mailchimp'),
    path('webhooks/webharvest/', WebHarvestWebhookView.as_view(), name='webhooks-webharvest'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls, name='site_admin'),
    path('webharvest/', include('webharvest.urls', namespace='webharvest'), name='webharvest'),
    path('web-harvest/', include('webharvest.urls', namespace='webharvest'), name='web-harvest'),
    # path('data-mining/', LibraryView.as_view(), name='library'),
    # path('email-automation/', LibraryView.as_view(), name='library'),

    # path('dante/', include('webharvest.urls', namespace='webharvest'), name='webharvest'),
    # path('ws', consumers.ChatConsumer)    
    # path('wss', consumers.ChatConsumer)
    # path('webharvest/', include('core.urls', namespace='chat'), name='chat'),
    # path('webharvest/', include('core.urls', namespace='chat'), name='chat'),
    #url(r'^', include('example.urls', namespace='example')),
    # path('', include('core.urls', namespace='chat'), name='chat'),

    path('messages/', include('chat.urls')),
]
