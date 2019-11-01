from django.shortcuts import render

from blog.models import BlogPost
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
        context['blog_list'] = blog_list
    
    return render(request, 'searches/view.html', context)