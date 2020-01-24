from django.conf.urls import url
from django.urls import path, re_path, include
from django.urls import reverse
from subscription.views import UserSubscriptionHistoryView 

from .views import(
    WebHarvestHomeView,
)


app_name='webharvest'
urlpatterns = [
    path('', WebHarvestHomeView.as_view(), name='home'),

]