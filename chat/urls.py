from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'chat'

urlpatterns = [

    # path('admin/', admin.site.urls),

    path('', include('core.urls')),


    # path('login/', LoginView.as_view(), name='login'),

    # path('logout/', LogoutView.as_view(), name='logout'),
]
