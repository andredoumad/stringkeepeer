from django.conf.urls import url
from django.urls import path, re_path, include
from django.urls import reverse
from subscription.views import UserSubscriptionHistoryView 

from .views import(
    AccountHomeView,
    AccountEmailActivateView,
    UserDetailUpdateView
)


app_name='accounts'
urlpatterns = [
    path('', AccountHomeView.as_view(), name='home'),
    path('details/', UserDetailUpdateView.as_view(), name='user-update'),
    path('history/subscriptions/', UserSubscriptionHistoryView.as_view(), name='user-subscription-history'),
    re_path(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', 
            AccountEmailActivateView.as_view(), 
            name='email-activate'),
    path('email/resend-activation/',
            AccountEmailActivateView.as_view(),
            name='resend-activation'),
]