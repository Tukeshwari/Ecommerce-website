from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from . utils import cookieCart, cartData


# Create your views here.
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']



    products = Product.objects.all()
    context = {'products': products,'cartItems': cartItems}
    return render(request, 'Eshop/store.html', context)




def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'Eshop/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'Eshop/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('ProductId:', productId)
    print('Action:', action)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was found', safe=False)


def processOrder(request):
    print('Data:', request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # total = float(data['form']['total'])
        # order.transaction_id = transaction_id
        # if total == float(order.get_cart_total):
        #     order.complete = True
        # order.save()
        # ShippingAddress.objects.create(
        #         customer=customer,
        #         order=order,
        #         address=(data['shipping']['address']),
        #         city=(data['shipping']['city']),
        #         state=(data['shipping']['state']),
        #         zipcode=(data['shipping']['zipcode']),
        #         country=(data['shipping']['country']),
        #     )
    else:
        print("User is not logged in")
        print("COOKIES:", request.COOKIES)
        name = data['form']['name']
        email = data['form']['email']

        cookieData = cookieCart(request)
        items = cookieData['items']
        customer, created = Customer.objects.get_or_create(email=email,)
        customer.name = name
        customer.save()
        order = Order.objects.create(customer=customer, complete=False,)

        for item in items:
            product = Product.objects.get(id=item['product']['id'])
            orderItem = OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity'],
             )
            # orderItem.save()

    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()
    ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=(data['shipping']['address']),
            city=(data['shipping']['city']),
            state=(data['shipping']['state']),
            zipcode=(data['shipping']['zipcode']),
            country=(data['shipping']['country']),

    )


    return JsonResponse('payment submitted', safe=False)



