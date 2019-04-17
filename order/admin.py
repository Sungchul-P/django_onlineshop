from django.contrib import admin

import csv
import datetime
from django.http import HttpResponse

# 주문 목록을 csv로 저장하는 함수입니다.
def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    # HttpResponse 객체로 응답을 받을 때 attachment 형식으로 설정하면 브라우저는 파일로 다운로드 받습니다.
    response['Content-Disposition'] = 'attachment;filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]

    # csv 파일 컬럼 타이틀 줄
    writer.writerow([field.verbose_name for field in fields])

    # 실제 데이터 출력
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%Y-%m-%d")
            data_row.append(value)
        writer.writerow(data_row)
    return response

# 관리자 페이지에 명령으로 추가할 때 어떤 이름을 사용할 것인지 결정하는 속성
export_to_csv.short_description = 'Export to CSV'


from django.urls import reverse
from django.utils.safestring import mark_safe

# 주문 목록에 열 데이터로 출력되는 값을 만들어 냅니다.
# 뷰를 호출하는 데 이 뷰들이 각각 주문의 상세 정보와 pdf 보기입니다.
def order_detail(obj):
    # 목록에 HTML를 출력하고 싶을 때는 mark_safe 함수를 사용해야만 합니다.
    return mark_safe('<a href="{}">Detail</a>'.format(reverse('orders:admin_order_detail', args=[obj.id])))

order_detail.short_description = 'Detail'


def order_pdf(obj):
    return mark_safe('<a href="{}">PDF</a>'.format(reverse('orders:admin_order_pdf', args=[obj.id])))

order_pdf.short_description = 'PDF'


from .models import OrderItem, Order

# 각 주문 정보의 아래쪽에 주문한 제품 목록을 출력할 수 있습니다.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    # list_display = ['id','first_name','last_name','email','address','postal_code','city','paid',order_detail,order_pdf,'created','updated']
    list_display = ['id','first_name','last_name','email','address','postal_code','city','paid',order_detail,'created','updated']
    list_filter = ['paid','created','updated']

    inlines = [OrderItemInline]
    actions = [export_to_csv]

admin.site.register(Order, OrderAdmin)