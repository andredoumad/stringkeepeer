from django.urls import path, re_path

from subscription.views import (
    SubscriptionListView, 
    #subscription_list_view, 
    
    #SubscriptionDetailView, 
    #subscription_detail_view,

    #SubscriptionFeaturedListView,    
    #SubscriptionFeaturedDetailView,
    SubscriptionDetailSlugView

)

urlpatterns = [
    # path('featured/', SubscriptionFeaturedListView.as_view()),
    # re_path(r'^featured/(?P<pk>\d+)/$', SubscriptionFeaturedDetailView.as_view()), # as view means callable
    path('', SubscriptionListView.as_view()), # as view means callable 
    # path('subscription-fbv/', subscription_list_view),
    #re_path(r'^subscription/(?P<pk>\d+)/$', SubscriptionDetailView.as_view()), # as view means callable 
    #re_path(r'^subscription/(?P<slug>[\w-]+)/$', SubscriptionDetailSlugView.as_view()),
    path('<str:slug>/', SubscriptionDetailSlugView.as_view()), 
    # re_path(r'^subscription-fbv/(?P<pk>\d+)/$', subscription_detail_view),
]