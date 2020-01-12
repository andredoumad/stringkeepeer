from django.urls import path, re_path

from subscription.views import (
    SubscriptionListView, 
    #subscription_list_view, 
    
    #SubscriptionDetailView, 
    #subscription_detail_view,

    #SubscriptionFeaturedListView,    
    #SubscriptionFeaturedDetailView,
    SubscriptionDetailSlugView,
    SubscriptionDownloadView
)

app_name = 'subscription'
urlpatterns = [
    path('', SubscriptionListView.as_view(), name='list'), # as view means callable 
    path('<str:slug>/', SubscriptionDetailSlugView.as_view(), name='detail'), 
    re_path(r'^(?P<slug>[\w-]+)/(?P<pk>\d+)/$', SubscriptionDownloadView.as_view(), name='download'),

]