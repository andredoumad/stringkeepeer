#from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
# Create your views here.

from .models import Subscription


class SubscriptionListView(ListView):
    #everything in the database
    queryset = Subscription.objects.all()
    template_name = 'subscription/list.html'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(SubscriptionListView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return context

def subscription_list_view(request):
    queryset = Subscription.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, "subscription/list.html", context)


class SubscriptionDetailView(DetailView):
    #everything in the database
    queryset = Subscription.objects.all()
    template_name = 'subscription/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SubscriptionDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        return context

def subscription_detail_view(request, pk=None, *args, **kwargs):
    print('args: ' + str(args))
    print('kwargs: ' + str(kwargs))
    instance = Subscription.objects.get(pk=pk) #id
    instance = get_object_or_404(Subscription, pk=pk)
    context = {
        'object': instance
    }
    return render(request, "subscription/detail.html", context)