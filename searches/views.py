from django.shortcuts import render
from django.views.generic import ListView
from blog.models import BlogPost
from subscription.models import Subscription
# Create your views here.
from .models import SearchQuery
from stringkeeper.views import get_ascii_art

def search_view(request):
    ascii_art = get_ascii_art()
    query = request.GET.get('q', None)
    user = None
    if request.user.is_authenticated:
        user = request.user
    context = {
        'query': query,
        'ascii_art': ascii_art
        }
    if query is not None:
        SearchQuery.objects.create(user=user, query=query)
        blog_list = BlogPost.objects.search(query=query)
        # subscription_list = Subscription.objects.search(query=query)
        context['blog_list'] = blog_list
        # context['subscription_list'] = subscription_list
    return render(request, 'searches/view.html', context)



# def search_view(request):
#     ascii_art = get_ascii_art()
#     query = request.GET.get('q', None)
#     user = None
#     if request.user.is_authenticated:
#         user = request.user
#     context = {
#         'query': query,
#         'ascii_art': ascii_art
#         }
#     if query is not None:
#         SearchQuery.objects.create(user=user, query=query)
#         blog_list = BlogPost.objects.search(query=query)
#         context['blog_list'] = blog_list
    
#     return render(request, 'searches/view.html', context)