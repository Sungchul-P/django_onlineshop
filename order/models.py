from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from coupon.models import Coupon
from shop.models import Product

import hashlib
from .iamport import payments_prepare, find_transaction

# 주문 정보를 저장하기 위한 모델(주문자와 주소 정보 저장)
class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # 결제 여부
    paid = models.BooleanField(default=False)

    # 쿠폰 및 할인 정보
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name='order_coupon', null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_product(self):
        return sum(item.get_item_price() for item in self.items.all())

    def get_total_price(self):
        total_product = self.get_total_product()
        return total_product - self.discount

# 주문에 포함된 제품 정보를 담기 위해 만드는 모델
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_item_price(self):
        return self.price * self.quantity


# OrderTransaction 모델의 매니저 클래스
# 결제 정보를 생성할 때 해시 함수를 사용해 merchant_order_id를 만들어 냅니다.
# 결제 이후에 결제 정보를 조회하는데도 사용됩니다.
class OrderTransactionManager(models.Manager):
    def create_new(self,order,amount,success=None,transaction_status=None):
        if not order:
            raise ValueError("주문 오류")

        order_hash = hashlib.sha1(str(order.id).encode('utf-8')).hexdigest()
        email_hash = str(order.email).split("@")[0]
        final_hash = hashlib.sha1((order_hash  + email_hash).encode('utf-8')).hexdigest()[:10]
        merchant_order_id = "%s"%(final_hash)

        payments_prepare(merchant_order_id,amount)

        tranasction = self.model(
            order=order,
            merchant_order_id=merchant_order_id,
            amount=amount
        )

        if success is not None:
            tranasction.success = success
            tranasction.transaction_status = transaction_status

        try:
            tranasction.save()
        except Exception as e:
            print("save error",e)

        return tranasction.merchant_order_id

    def get_transaction(self,merchant_order_id):
        result = find_transaction(merchant_order_id)
        if result['status'] == 'paid':
            return result
        else:
            return None

# 결제 정보를 저장에 사용하는 모델
class OrderTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    merchant_order_id = models.CharField(max_length=120, null=True, blank=True)
    transaction_id = models.CharField(max_length=120, null=True,blank=True)
    amount = models.PositiveIntegerField(default=0)
    transaction_status = models.CharField(max_length=220, null=True,blank=True)
    type = models.CharField(max_length=120,blank=True)
    created = models.DateTimeField(auto_now_add=True,auto_now=False)

    objects = OrderTransactionManager()

    def __str__(self):
        return str(self.order.id)

    class Meta:
        ordering = ['-created']

# 시그널을 활용한 결제 검증 함수
# 시그널이란 특정 기능이 수행되었음을 장고 애플리케이션 전체에 알리는 용도입니다.
# OrderTransaction 모델의 객체가 추가되면 그 후에 결제 검증을 하는 함수를 호출하도록 연결했습니다.
def order_payment_validation(sender, instance, created, *args, **kwargs):
    if instance.transaction_id:
        import_transaction = OrderTransaction.objects.get_transaction(merchant_order_id=instance.merchant_order_id)

        merchant_order_id = import_transaction['merchant_order_id']
        imp_id = import_transaction['imp_id']
        amount = import_transaction['amount']

        local_transaction = OrderTransaction.objects.filter(merchant_order_id=merchant_order_id, 
            transaction_id=imp_id, amount=amount).exists()

        if not import_transaction or not local_transaction:
            raise ValueError("비정상 거래입니다.")


# 결제 정보가 생성된 후에 호출할 함수를 연결해줍니다.
from django.db.models.signals import post_save
post_save.connect(order_payment_validation, sender=OrderTransaction)