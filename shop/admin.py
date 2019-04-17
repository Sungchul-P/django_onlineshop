from django.contrib import admin

from .models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','slug']
    # prepopulated_fields : slug 필드는 name 필드의 값에 따라 자동으로 설정된다.
    prepopulated_fields = {'slug':('name',)}


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','slug','category','price','stock','available_display','available_order',
                    'created','updated']
    list_filter = ['available_display','created','updated','category']
    prepopulated_fields = {'slug': ('name',)}
    # 목록에서도 주요 값들은 바로바로 변경할 수 있도록 한다.
    list_editable = ['price','stock','available_display','available_order']

admin.site.register(Product, ProductAdmin)