from django.conf.urls import url
from django.urls import path, re_path, include
from django.urls import reverse
from subscription.views import UserSubscriptionHistoryView 
from webharvest.api import WebharvestMessageModelViewSet, WebharvestUserModelViewSet
from rest_framework.routers import DefaultRouter

from .views import(
    WebHarvestHomeView,
    ThreadView,
    InboxView
)

router = DefaultRouter()
router.register(r'message', WebharvestMessageModelViewSet, basename='message-api')
router.register(r'user', WebharvestUserModelViewSet, basename='user-api')

app_name='webharvest'
urlpatterns = [
    # url(r'^ws$', consumers.ChatConsumer),
    # url(r'^wss$', consumers.ChatConsumer),
    # path('', WebHarvestHomeView.as_view(), name='home'),
    path("", InboxView.as_view()),
    re_path(r"^(?P<username>[\w.@+-]+)", ThreadView.as_view()),
    path(r'api/v1/', include(router.urls)),
    
]