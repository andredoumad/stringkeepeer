#from django.shortcuts import render
from django.http import Http404
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from stringkeeper.standalone_tools import *
import stringkeeper.standalone_tools

from analytics.mixins import ObjectViewedMixin
from carts.models import Cart

from .models import Subscription



class SubscriptionFeaturedListView(ListView):
    template_name = 'subscription/list.html'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Subscription.objects.all().featured()

class SubscriptionFeaturedDetailView(ObjectViewedMixin, DetailView):
    queryset = Subscription.objects.all().featured()
    template_name = 'subscription/featured-detail.html'

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     return Subscription.objects.featured()


class SubscriptionListView(ListView):
    #everything in the database
    #queryset = Subscription.objects.all()
    template_name = 'subscription/list.html'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(SubscriptionListView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return context

    def get_context_data(self, *args, **kwargs):
        context = super(SubscriptionListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        context['ascii_art'] = get_ascii_art()
        # eventlog(context)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Subscription.objects.all()

def subscription_list_view(request):
    queryset = Subscription.objects.all()
    ascii_art = get_ascii_art()
    context = {
        'title': 'Subscription List',
        'object_list': queryset,
        'ascii_art': ascii_art
    }
    return render(request, "subscription/list.html", context)

class SubscriptionDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Subscription.objects.all()
    template_name = "subscription/detail.html"

    def get_context_data(self, *args, **kwargs):
        ascii_art = get_ascii_art()
        context = super(SubscriptionDetailSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        ascii_art = get_ascii_art()

        #instance = get_object_or_404(Subscription, slug=slug, active=True)
        #eventlog('instance: ' + str(instance))
        try:
            instance = Subscription.objects.get(slug=slug, active=True)
        except Subscription.DoesNotExist:
            raise Http404("Not Found...")
        except Subscription.MultipleObjectsReturned:
            qs = Subscription.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except:
            raise Http404("This is odd... I couldn't find what you're looking for.")
        # object_viewed_signal.send(instance.__class__, instance=instance, request=request)        
        eventlog('instance: ' + str(instance))
        return instance


class SubscriptionDetailView(ObjectViewedMixin, DetailView):
    #everything in the database
    #queryset = Subscription.objects.all()
    template_name = 'subscription/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SubscriptionDetailView, self).get_context_data(*args, **kwargs)
        # eventlog(context)
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Subscription.objects.get_by_id(pk)
        eventlog('instance: ' + str(instance))
        if instance is None:
            raise Http404('Subscription does not exist')
        return instance

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     pk = self.kwargs.get('pk')
    #     return Subscription.objects.filter(pk=pk)



def subscription_detail_view(request, pk=None, *args, **kwargs):
    ascii_art = get_ascii_art()
    #pk stands for primary key
    eventlog('pk = ' + str(pk))
    eventlog('args = ' + str(args))
    eventlog('kwargs = ' + str(kwargs))

    #instance = Subscription.objects.get(pk=pk) #id
    #instance = get_object_or_404(Subscription, pk=pk)

    # try:
    #     instance = Subscription.objects.get(id=pk)
    # except Subscription.DoesNotExist:
    #     print('no subscription found')
    #     raise Http404("subscription doesn't exist")
    # except:
    #     print('huh?')

    instance = Subscription.objects.get_by_id(pk)
    eventlog('instance: ' + str(instance))
    if instance is None:
        raise Http404('Subscription does not exist')

    # qs = Subscription.objects.filter(id=pk)

    # #print(qs)
    # #count is more efficient than len 
    # if qs.exists() and qs.count() == 1: #len(qs)
    #     instance = qs.first()
    # else:
    #     raise Http404("subscription doesn't exist")


    context = {
        'title': 'Subscription Details',
        'object': instance,
        'ascii_art': ascii_art
    }
    return render(request, "subscription/detail.html", context)