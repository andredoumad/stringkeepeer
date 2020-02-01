from django.conf.urls import url
from django.urls import path, re_path, include
from django.urls import reverse
from subscription.views import UserSubscriptionHistoryView 

from .views import(
    WebHarvestHomeView,
)
# from core import consumers

# from django.conf.urls import url

app_name='webharvest'
urlpatterns = [
    # url(r'^ws$', consumers.ChatConsumer),
    # url(r'^wss$', consumers.ChatConsumer),
    path('', WebHarvestHomeView.as_view(), name='home'),

]