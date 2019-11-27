"""stringkeeper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path, include #url
from django.views.generic import TemplateView
from blog.views import (
    blog_post_create_view,
)

from django.views.generic.base import TemplateView # new

from searches.views import search_view

from carts.views import cart_home

from accounts.views import login_page, register_page, guest_register_view


from .views import (
    home_page,
    about_page,
    contact_page,
    #example_page,
    #login_page,
    #register_page
)


urlpatterns = [
    path('admin/', admin.site.urls, name='site_admin'),
    path('', home_page, name='home'),
    path('blog-new/', blog_post_create_view),
    path('blog/', include('blog.urls', namespace='blog'), name='blog'),
    path('contact/', contact_page, name='contact'),
    # path('login/', login_page, name='login'),
    #how come i cant use anything beyond auth_login - everytime i try just login it breaks
    #even if i change the navbar template, its not right...
    path('login/', login_page, name='auth_login'),
    path('register/guest/', guest_register_view, name='guest_register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cart/', include('carts.urls', namespace='cart'), name='cart'),
    path('register/', register_page, name='register'),
    path('bootstrap/', TemplateView.as_view(template_name='bootstrap/example.html')),
    path('subscriptions/', include('subscription.urls', namespace='subscription'), name='subscription'),
    path('search/', include('search.urls', namespace='search'), name='search'),
    path('accounts/', include('django.contrib.auth.urls')),

]

#if settings.DEBUG:
    #from django.conf.urls.static import static
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
