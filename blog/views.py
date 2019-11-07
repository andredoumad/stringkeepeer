from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

# Create your views here.
from blog.forms import BlogPostModelForm
from blog.models import BlogPost
from stringkeeper.views import get_ascii_art

# CRUD
# GET -> Retrieve / List
# POST -> Create / Update / DELETE
# Create Retrieve Update Delete

def blog_post_list_view(request):
    ascii_art = get_ascii_art()
    #now = timezone.now()
    # list out objects
    # could be search
        #qs = BlogPost.objects.filter(title__icontains='hello')
    #qs = BlogPost.objects.all() # queryset -> list of python object
    #__lte = less than or equal to while gte is greater than or equal to
    #qs = BlogPost.objects.filter(publish_date__lte=now)
    qs = BlogPost.objects.all().published()
    if request.user.is_authenticated:
        #only show blogs from current user
        my_qs = BlogPost.objects.filter(user=request.user)
        #combbines queries of the same class and then uses only the ones that are unique
        qs = (qs | my_qs).distinct()
    template_name = 'blog/list.html'
    context = {
        'title': 'blog',
        'object_list': qs,
        'ascii_art': ascii_art
        }
    return render(request, template_name, context)

#wrapper that goes around this view
#ensures a user has a session and logged in before allowing the use of it.
#we can make it go to the login page automatically based on the settings.py url
#@login_required
# note it's possible to use multiple decorators
#in this demo case we can use staff member required until we have a more advanced user model

@staff_member_required
def blog_post_create_view(request):
    ascii_art = get_ascii_art()
    # create objects
    # use forms
    # request.user -> return something
    form = BlogPostModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        # could also edit the commit like this:
        obj = form.save(commit=False) # so don't save just yet
        #add data or manipulate data like this - adding a 0 to the end of the title
        #obj.title = form.cleaned_data.get('title') + '0'
        
        #user data association
        #if not request.user.is_authenticated:
        #    return render(request, 'not-a-user.html', {})
        obj.user = request.user # associate the current user with this data
        #then save like this
        form.save()
        
        #clear form like this
        form = BlogPostModelForm()
        # ** turns the data from the from , each key value pair into ARGUMENTS :)
        #obj = BlogPost.objects.create(**form.cleaned_data)
    template_name = 'form.html'
    context = {
        'title': 'blog create',
        'form': form,
        'ascii_art': ascii_art
        }
    return render(request, template_name, context)

def blog_post_detail_view(request, slug):
    ascii_art = get_ascii_art()
    # retrieve
    # 1 object -> detail view
    obj = get_object_or_404(BlogPost, slug=slug)
    template_name = 'blog/detail.html'
    context = {
        'title': 'blog detail',
        'object': obj,
        'ascii_art': ascii_art
        }
    return render(request, template_name, context)

@staff_member_required
def blog_post_update_view(request, slug):
    ascii_art = get_ascii_art()
    obj = get_object_or_404(BlogPost, slug=slug)
    form = BlogPostModelForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
    template_name = 'form.html'
    context = {
        'title': 'blog update',
        'title': f'Update {obj.title}',
        'form': form,
        'ascii_art': ascii_art        
        }
    return render(request, template_name, context)

@staff_member_required
def blog_post_delete_view(request, slug):
    ascii_art = get_ascii_art()
    obj = get_object_or_404(BlogPost, slug=slug)
    template_name = 'blog/delete.html'
    if request.method == 'POST':
        obj.delete()
        return redirect('/blog')
    context = {
        'title': 'blog delete',
        'object': obj,
        'ascii_art': ascii_art
        }
    return render(request, template_name, context)