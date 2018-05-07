from django import forms
from django.core.exceptions import ValidationError

class UserForm(forms.Form):
    user = forms.CharField(required=True,min_length=3,error_messages={'required':'用户名不能为空',"min_lenth":"用户名长度不能小于3"})
    passwd = forms.CharField(required=True, min_length=8,error_messages={
        'min_length':'密码长度不能小于8','required':'密码不能为空'})