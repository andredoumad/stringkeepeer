from django.shortcuts import render
from django.views.generic import ListView
from blog.models import BlogPost
from subscription.models import Subscription
# Create your views here.
from .models import SearchQuery
from stringkeeper.standalone_tools import *




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
#         # subscription_list = Subscription.objects.search(query=query)
#         context['blog_list'] = blog_list
#         # context['subscription_list'] = subscription_list
#     return render(request, 'searches/view.html', context)




class search_view(ListView):
    template_name = 'searches/view.html'

    def get_context_data(self, *args, **kwargs):
        context = super(search_view, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        SearchQuery.objects.create(query=query)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        query = method_dict.get('q', None) # method_dict['q']
        if query is not None:
            return Subscription.objects.search(query)
        return Subscription.objects.featured()



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