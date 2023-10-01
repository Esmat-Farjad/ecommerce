from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Store, Product


class UserCreationForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = (
            'first_name','last_name','email','username','password1','password2','store'
        )
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus':False})
        self.fields['first_name'].widget.attrs['class'] ='border py-2 border-teal-500 w-full'
        self.fields['last_name'].widget.attrs['class'] ='border py-2 border-teal-500 w-full'
        self.fields['email'].widget.attrs['class'] ='border py-2 border-teal-500 w-full'
        self.fields['username'].widget.attrs['class'] ='border py-2 border-teal-500 w-full'
        self.fields['password1'].widget.attrs['class'] ='border py-2 border-teal-500 w-full'
        self.fields['password2'].widget.attrs['class'] ='border py-2 border-teal-500 w-full'
        self.fields['store'].widget.attrs['class'] ='border py-2 border-teal-500 w-full'
            

class StoreCreationForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(StoreCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'border py-2 border-teal-500 w-full'
            
    
