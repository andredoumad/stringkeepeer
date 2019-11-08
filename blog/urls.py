from django.urls import path, re_path #url
from blog.views import (
    blog_post_detail_view,
    blog_post_list_view,
    blog_post_update_view,
    blog_post_delete_view,
)

app_name = 'blog'
urlpatterns = [
    path('', blog_post_list_view, name='list'),
    path('<str:slug>/', blog_post_detail_view),
    path('<str:slug>/edit/', blog_post_update_view),
    path('<str:slug>/delete/', blog_post_delete_view),
]
