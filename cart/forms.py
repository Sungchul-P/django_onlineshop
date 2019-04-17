from django import forms

class AddProductForm(forms.Form):
    # quantity : 제품의 수량
    quantity = forms.IntegerField()
    
    # is_update : 상세 페이지에서 추가할 때와 장바구니에서 수량을 바꿀 때 동작하는 방식을 달리하기 위한 변수
    is_update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)