from django.urls import path, re_path #url

from .views import (
        OrderListView, 
        OrderDetailView,
        # VerifyOwnership
        )

app_name = 'orders'
urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    # path('endpoint/verify/ownership/', VerifyOwnership.as_view(), name='verify-ownership'),
    re_path('^(?P<order_id>[0-9A-Za-z]+)/$', OrderDetailView.as_view(), name='detail'),
]