# pages/views.py

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
# project
from .models import Product, Order, OrderLine
from .forms import CheckoutForm


class HomeView(ListView):
    model = Product
    template_name = "pages/home.html"


class ProductView(DetailView):
    model = Product
    template_name = "pages/product.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'pages/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("/")


def about(request):
    return HttpResponse('Projekt grupowy z Inżynierii Oprogramowania.')


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_item, created = OrderLine.objects.get_or_create(
        product=item,
        customer=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(customer=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.products.filter(product__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added quantity to Product")
            return redirect("pages:order-summary")
        else:
            order.products.add(order_item)
            messages.info(request, "Product added to your cart")
            return redirect("pages:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(customer=request.user, orderDate=ordered_date)
        order.products.add(order_item)
        messages.info(request, "Product added to your cart")
        return redirect("pages:order-summary")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(
        customer=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__pk=item.pk).exists():
            order_item = OrderLine.objects.filter(
                product=item,
                customer=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Item \"" + order_item.product.name + "\" remove from your cart")
            return redirect("pages:order-summary")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("pages:product", pk=pk)
    else:
        messages.info(request, "You do not have an Order")
        return redirect("pages:product", pk=pk)


@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(customer=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__pk=item.pk).exists():
            order_item = OrderLine.objects.filter(product=item, customer=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Product quantity was updated")
            return redirect("pages:order-summary")
        else:
            messages.info(request, "This Product not in your cart")
            return redirect("pages:order-summary")
    else:
        messages.info(request, "You do not have an Order")
        return redirect("pages:order-summary")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionaly for these fields
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                checkout_address = CheckoutAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                checkout_address.save()
                order.checkout_address = checkout_address
                order.save()

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid Payment option")
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("core:order-summary")