from django.shortcuts import render
from django.views.generic import ListView
from subscription.models import Subscription
from stringkeeper.standalone_logging import *

# class SearchSubscriptionView(ListView):
#     template_name = 'subscription/list.html'

#     def get_queryset(self, *args, **kwargs):
#         request = self.request
#         return Subscription.objects.filter(title__contains('Data mining'))




class SearchSubscriptionView(ListView):
    template_name = 'search/view.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SearchSubscriptionView, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        eventlog(query)
        #SearchQuery.objects.create(query=query)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        query = method_dict.get('q', None) # method_dict['q']
        if query is not None:
            eventlog(query)
            return Subscription.objects.search(query)
        return Subscription.objects.featured()