from django.shortcuts import render
from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
# Create your views here.
from django.utils.http import is_safe_url
from .models import Address
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from billing.models import BillingProfile
from .forms import AddressForm
from django.views.generic import ListView, UpdateView, CreateView




class AddressListView(LoginRequiredMixin, ListView):
    template_name = 'addresses/list.html'

    def get_queryset(self):
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        return Address.objects.filter(billing_profile=billing_profile)



class AddressUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'addresses/update.html'
    form_class = AddressForm
    success_url = '/addresses'
    
    def get_queryset(self):
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        return Address.objects.filter(billing_profile=billing_profile)


class AddressCreateView(LoginRequiredMixin, CreateView):
    template_name = 'addresses/update.html'
    form_class = AddressForm
    success_url = '/addresses'

    def form_valid(self, form):
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        instance = form.save(commit=False)
        instance.billing_profile = billing_profile
        instance.save()
        return super(AddressCreateView, self).form_valid(form)

    # def get_queryset(self):
        
    #     return Address.objects.filter(billing_profile=billing_profile)





def checkout_address_create_view(request):
    eventlog('LOGIN_PAGE -- ACCOUNTS')
    ascii_art = get_ascii_art()
    form = AddressForm(request.POST or None)
    context = {
        'form': form,
        'ascii_art': ascii_art
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None

    if form.is_valid():
        eventlog(str(request.POST))
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

        if billing_profile is not None:
            # instance.billing_profile = billing_profile
            address_type = request.POST.get('address_type', 'billing')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()
            request.session[address_type + '_address_id'] = instance.id
            eventlog(str(address_type + '_address_id'))
            # billing_address_id = request.session.get('billing_address_id', None)
        else:
            eventlog('error here address wasnt saved')
            if is_safe_url(redirect_path, request.get_host()):
                eventlog('safe url')
                return redirect(redirect_path)
            else:
                eventlog('not safe url')
                return redirect('cart:checkout')
    return redirect('cart:checkout')


def checkout_address_reuse_view(request):
    if request.user.is_authenticated:
        eventlog('LOGIN_PAGE -- ACCOUNTS')
        ascii_art = get_ascii_art()
        form = AddressForm(request.POST or None)
        context = {
            'ascii_art': ascii_art
        }
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == 'POST':
            eventlog(str(request.POST))
            billing_address = request.POST.get('billing_address', None)
            address_type = request.POST.get('address_type', 'billing')
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            if billing_address is not None:
                qs = Address.objects.filter(billing_profile=billing_profile, id=billing_address)
                if qs.exists():
                    request.session[address_type + '_address_id'] = billing_address

                if is_safe_url(redirect_path, request.get_host()):
                    eventlog('safe url')
                    return redirect(redirect_path)
    return redirect('cart:checkout')