from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'auth-input', 'placeholder': 'Username or Student ID',
        'autocomplete': 'username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'auth-input', 'placeholder': 'Password',
        'autocomplete': 'current-password',
    }))


class StudentRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'First name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Last name'}))
    student_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Student ID (e.g. UG/0001/22)'}))
    department = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Department'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Username'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Password'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'student_id', 'department', 'username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user
