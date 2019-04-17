from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Coupon(models.Model):
    # 쿠폰 사용시 입력할 코드
    code = models.CharField(max_length=50, unique=True)
    # 쿠폰 사용 기간
    use_from = models.DateTimeField()
    use_to = models.DateTimeField()
    # 할인 금액(값은 0 ~ 100000 사이로만 설정할 수 있도록 제약 조건 설정)
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100000)])
    active = models.BooleanField()

    def __str__(self):
        return self.code