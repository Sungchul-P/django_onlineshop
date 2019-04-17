from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Coupon
from .forms import AddCouponForm

@require_POST
def add_coupon(request):
    now = timezone.now()
    form = AddCouponForm(request.POST)

    if form.is_valid():
        code = form.cleaned_data['code']
        # 입력한 쿠폰 코드를 이용해 쿠폰을 조회합니다.
        try:
            # iexact : 대소문자 구분없이 일치하는 코드
            # use_from__lte=now : 현재 시간보다 이전
            # use_to__gte=now : 현재 시간보다 이후
            coupon = Coupon.objects.get(code__iexact=code, use_from__lte=now, use_to__gte=now, active=True)

            # 입력한 쿠폰이 존재하면 쿠폰의 id 값을 세션에 저장
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None

    # 장바구니로 돌아갑니다.
    return redirect('cart:detail')