from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class UserForm(forms.Form):
    username = forms.CharField(label='Username')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='First password field')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Second password field')
    
    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError("Both passwords must match")
        return self.cleaned_data
    
    def clean_username(self):
        username_available = False
        try:
            user = User.objects.get(username=self.cleaned_data.get('username'))
        except ObjectDoesNotExist:
            username_available = True
        
        if not username_available:
            raise forms.ValidationError("Username already exists")
        return self.cleaned_data.get('username')
    
class UserLogin(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput,label="Password")

class UpdateProfile(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, label='First password field',required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Second password field',required=False)
    email = forms.EmailField(label='Email',required=False)