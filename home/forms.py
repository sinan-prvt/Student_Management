from django import forms
from django.contrib.auth.models import User
from .models import Student

class StudentSignupForm(forms.ModelForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )
    password = forms.CharField(
        required=True,
        min_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us something about yourself...'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile_pic', 'bio']

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email')
        )
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                profile_pic=self.cleaned_data.get('profile_pic'),
                bio=self.cleaned_data.get('bio')
            )
        return user


class StudentProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = Student
        fields = ['bio', 'profile_pic']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Update your bio...'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
