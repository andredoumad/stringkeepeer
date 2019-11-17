from django.conf.urls import url

from .views import (
    SearchSubscriptionView
)

app_name = 'search'
urlpatterns = [
    url(r'^$', SearchSubscriptionView.as_view(), name='list'),
    url(r'^$', SearchSubscriptionView.as_view(), name='query'),
]