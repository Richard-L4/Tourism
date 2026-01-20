from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Contact


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Enter your password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(
                attrs={'placeholder': 'Enter your username'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'message']
        labels = {
            'name': 'Full Name',
            'email': 'Email',
            'phone': 'Phone',
            'message': 'Message',
        }

        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(
                attrs={'placeholder': 'Enter your email address'}),
            'phone': forms.TextInput(
                attrs={'placeholder': 'Enter your phone number'}),
            'message': forms.Textarea(
                attrs={'placeholder': 'Enter your message'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
