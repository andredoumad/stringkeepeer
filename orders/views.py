from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import View, ListView, DetailView
from django.shortcuts import render

# Create your views here.

from billing.models import BillingProfile
from .models import Order

class OrderListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        my_profile = BillingProfile.objects.new_or_get(self.request)
        return Order.objects.by_request(self.request)


class OrderDetailView(LoginRequiredMixin, DetailView):

    def get_object(self):
        # return Order.objects.get(id=self.kwargs.get('id'))
        # return Order.objects.get(slug=self.kwargs.get('slug'))
        qs = Order.objects.by_request(
            self.request
            ).filter(order_id = self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        return Http404


    # def get_queryset(self):
    #     my_profile = BillingProfile.objects.new_or_get(self.request)
    #     return Order.objects.by_request(self.request)



class LibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'
    def get_queryset(self):
        return ProductPurchase.objects.products_by_request(self.request) #.by_request(self.request).digital()

class VerifyOwnership(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            data = request.GET 
            product_id = request.GET.get('product_id', None)
            if product_id is not None:
                product_id = int(product_id)
                ownership_ids = ProductPurchase.objects.products_by_id(request)
                if product_id in ownership_ids:
                    return JsonResponse({'owner': True})
            return JsonResponse({'owner': False})
        raise Http404
