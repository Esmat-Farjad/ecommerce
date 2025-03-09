from typing import Any, Mapping
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import CustomUser, Store, Product


class UserCreationForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = (
            'username','first_name','last_name','email','password1','password2'
        )
        # store removed from the list
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class']="form-input"
            visible.field.widget.attrs['placeholder']=visible.field.label
            

class StoreCreationForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(StoreCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'border py-2 border-teal-500 w-full'
            
            
class PurchaseProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        exclude = ['user','total_items','total_package_price', 'item_sale_price']
        
    def __init__(self, *args, **kwargs):
        super(PurchaseProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class']="form-input"
            visible.field.widget.attrs['placeholder']=visible.field.label

class ProductSearchForm(forms.Form):
    query = forms.CharField(
        label="Search", 
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class':'search-input',
            'placeholder':'enter product name...'
            })
        )


class UpdateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'mfd':forms.widgets.DateInput(
                attrs={
                    "type": "date",
                }),
            'expd':forms.widgets.DateInput(
                attrs={
                    "type": "date",
                })
        }
        
    def __init__(self, *args, **kwargs):
        super(UpdateProductForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class']="form-input"
            visible.field.widget.attrs['placeholder']=visible.field.label
