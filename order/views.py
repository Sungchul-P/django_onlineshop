from django.shortcuts import render, get_object_or_404
from .models import *
from cart.cart import Cart
from .forms import *

# 주문서를 입력받기 위한 뷰
# 실제 결제를 진행하고 나면 해당 정보를 저장하는데 사용됩니다.
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.amount
                order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])

            cart.clear()
            return render(request, 'order/created.html', {'order':order})
    else:
        form = OrderCreateForm()
    return render(request, 'order/create.html', {'cart':cart, 'form':form})


from django.contrib.admin.views.decorators import staff_member_required
# 관리자로 로그인 했을 때만 호출이 가능하도록 데코레이터를 사용합니다,
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/admin/detail.html', {'order':order})

# pdf를 위한 임포트
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint # pdf 생성에 사용하는 모듈

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('order/admin/pdf.html', {'order':order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=order_{}.pdf'.format(order.id)
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(settings.STATICFILES_DIRS[0]+'/css/pdf.css')])
    return response


# ajax로 결제 후에 보여줄 결제 완료 화면
def order_complete(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id)
    return render(request,'order/created.html',{'order':order})

# 결제를 위한 임포트
from django.views.generic.base import View
from django.http import JsonResponse


# 사용자가 입력한 주문 정보를 서버에 저장하고 장바구니를 비웁니다. 
# 또한, 장바구니에 담겨 있던 제품들을 OrderItem 객체들로 저장하는 역할을 수행합니다.
class OrderCreateAjaxView(View):
    def post(self, request, *args, **kwargs):
        # 인증되지 않은 사용자인 경우, 403 오류 전송
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        cart = Cart(request)
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.amount
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            data = {
                "order_id": order.id
            }
            print(data)
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)

# 실제 결제 전에 결제 정보 생성
# 여기서 생성한 merchant_order_id를 반환받아서 다음 절차에 사용합니다.
class OrderCheckoutAjaxView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        amount = request.POST.get('amount')

        try:
            merchant_order_id = OrderTransaction.objects.create_new(
                order=order,
                amount=amount
            )
        except:
            merchant_order_id = None

        print("try_except: ", merchant_order_id)
        if merchant_order_id is not None:
            data = {
                "works": True,
                "merchant_id": merchant_order_id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)

# 실제 결제가 이뤄진 것이 있는지 확인
class OrderImpAjaxView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        merchant_id = request.POST.get('merchant_id')
        imp_id = request.POST.get('imp_id')
        amount = request.POST.get('amount')

        try:
            trans = OrderTransaction.objects.get(
                order=order,
                merchant_order_id=merchant_id,
                amount=amount
            )
        except:
            trans = None

        print(trans)
        if trans is not None:
            trans.transaction_id = imp_id
            trans.success = True
            trans.save()
            order.paid = True
            order.save()

            data = {
                "works": True
            }

            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)