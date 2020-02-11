from django.conf.urls import url
from django.urls import path, re_path, include
from django.urls import reverse
from subscription.views import UserSubscriptionHistoryView 
# from webharvest.api import WebharvestMessageModelViewSet, WebharvestUserModelViewSet
from rest_framework.routers import DefaultRouter

from .views import(
    WebHarvestHomeView,
    ThreadView,
    InboxView
)

app_name='webharvest'
urlpatterns = [
    # path("", InboxView.as_view()),
    path("", ThreadView.as_view()),
    re_path(r"^(?P<username>[\w.@+-]+)", ThreadView.as_view()),
    
]