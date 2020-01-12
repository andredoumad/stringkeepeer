import random
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import render
from stringkeeper.standalone_tools import *
from django.utils import  timezone


from orders.models import Order

# Create your views here.

class SalesAjaxView(View):
    def get(self, request, *args, **kwargs):
        data = {}
        if request.user.is_staff:
            qs = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=5)
            if request.GET.get('type') == 'week':
                days = 7
                start_date = timezone.now().today() - datetime.timedelta(days=days-1)
                datetime_list = []
                labels = []
                salesItems = []
                for x in range(0, days):
                    new_time = start_date + datetime.timedelta(days=x)
                    datetime_list.append(
                            new_time
                        )
                    labels.append(
                        new_time.strftime("%a") # mon
                    )
                    new_qs = qs.filter(updated__day=new_time.day, updated__month=new_time.month)
                    day_total = new_qs.totals_data()['total__sum'] or 0
                    salesItems.append(
                        day_total
                    )
                #print(datetime_list)

                data['labels'] = labels
                data['data'] = salesItems
            if request.GET.get('type') == '4weeks':
                data['labels'] = ["Four Weeks Ago", "Three Weeks Ago", "Two Weeks Ago", "Last Week", "This Week"]
                current = 5
                data['data'] = []
                for i in range(0, 5):
                    new_qs = qs.by_weeks_range(weeks_ago=current, number_of_weeks=1)
                    sales_total = new_qs.totals_data()['total__sum'] or 0
                    data['data'].append(sales_total)
                    current -= 1
        return JsonResponse(data)



class SalesView(TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        context = {
            'user_ip': get_client_ip(self.request),
            'ascii_art': get_ascii_art()
            }
        if not user.is_staff:
            # return HttpResponse("Staff members need to login before viewing this page.", status=401)
            return render(self.request, "home.html", context )
        return super(SalesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        return super(SalesView, self).get_context_data(*args, **kwargs)