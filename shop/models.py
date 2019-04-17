from django.db import models

from django.urls import reverse

# 카테고리 모델
class Category(models.Model):
    # db_index=True : 카테고리 테이블은 이 이름 열을 인덱스 열로 설정합니다.
    name = models.CharField(max_length=200, db_index=True)

    # meta_description : SEO(Search Engine Optimization)을 위해 만드는 필드
    meta_description = models.TextField(blank=True)

    # 카테고리와 상품 모두에 설정되는 필드. 상품명을 이용해서 URL을 만드는 방식입니다.
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True)

    class Meta:
        ordering = ['name']
        # 관리자 페이지에서 보여지는 객체가 단수일 때와 복수일 때 표현하는 값을 달리 설정
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_in_category", args=[self.slug])


# 상품 모델
class Product(models.Model):
    # ForeignKey 필드를 사용해 카테고리 모델과 관계를 만듭니다.
    # models.SET_NULL : 카테고리를 삭제해도 상품은 남아있어야 하기 때문에 이 옵션으로 설정합니다.
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True)

    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)

    # 제품 가격과 재고(필수 값)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    # 상품 노출 여부와 상품 주문 가능 여부
    available_display = models.BooleanField('Display', default=True)
    available_order = models.BooleanField('Order', default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        # 멀티 컬럼 색인 기능입니다. (id와 slug 필드를 묶어서 색인이 가능)
        index_together = [['id','slug']]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.id, self.slug])