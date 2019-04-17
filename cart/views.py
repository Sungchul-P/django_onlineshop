from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from shop.models import Product
from .forms import AddProductForm
from .cart import Cart
from coupon.forms import AddCouponForm


@require_POST
def add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # 제품의 정보는 상세 페이지 혹은 장바구니 페이지로부터 전달되며
    # AddProductForm을 통해 만들어진 데이터 입니다.
    form = AddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        # 제품 정보를 전달 받으면 카트 객체에 제품 객체를 추가합니다.
        cart.add(product=product, quantity=cd['quantity'], is_update=cd['is_update'])

    return redirect('cart:detail')


def remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # 카트에서 제품을 삭제합니다.
    cart.remove(product)
    return redirect('cart:detail')


def detail(request):
    cart = Cart(request)
    add_coupon = AddCouponForm() # 장바구니 페이지에 쿠폰 폼을 출력합니다.

    for product in cart:
        # 제품 수량 수정을 위해서 제품마다 폼을 하나씩 추가해 줍니다.
        # 수량은 수정하는 대로 반영해야 하기 때문에 is_update 값을 True로 설정했습니다.
        product['quantity_form'] = AddProductForm(initial={'quantity':product['quantity'], 'is_update':True})

    return render(request, 'cart/detail.html', {'cart':cart, 'add_coupon':add_coupon})