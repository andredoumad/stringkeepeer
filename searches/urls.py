from django.conf.urls import url
from .views import(
    search_view
)

app_name = 'searches'
urlpatterns = [
    url(r'^$', search_view.as_view(), name='list')
]