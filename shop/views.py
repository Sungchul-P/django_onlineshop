from django.shortcuts import render, get_object_or_404

from .models import *
from cart.forms import AddProductForm

# 카테고리 페이지
def product_in_category(request, category_slug=None):
    current_category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available_display=True)

    # URL로부터 category_slug를 찾아서 현재 어느 카테고리를 보여주는 것인지 판단합니다.
    # 선택한 카테고리가 없을 경우 전체 상품 목록을 노출하면 됩니다.
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    return render(request, 'shop/list.html', 
        {'current_category': current_category, 'categories': categories, 'products': products})


# 제품 상세 뷰
def product_detail(request, id, product_slug=None):
    # URL로부터 슬러그 값을 읽어와서 해당 제품을 찾습니다. 그리고 그 제품을 노출합니다.
    # 없는 경우 404 페이지를 출력합니다.
    product = get_object_or_404(Product, id=id, slug=product_slug)

    add_to_cart = AddProductForm(initial={'quantity':1})

    return render(request, 'shop/detail.html', {'product': product, 'add_to_cart': add_to_cart})