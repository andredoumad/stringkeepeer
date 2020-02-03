from django.conf.urls import url
from example import views


app_name = 'example'
urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),
]