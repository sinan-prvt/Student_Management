from django import forms
from django.contrib.auth.models import User
from .models import Student 

class StudentSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=4)  # basic password validation
    profile_pic = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile_pic', 'bio']

    def save(self, commit=True):
        # Save user
        user = User(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email')
        )
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
            # Create student profile
            Student.objects.create(
                user=user,
                profile_pic=self.cleaned_data.get('profile_pic'),
                bio=self.cleaned_data.get('bio')
            )
        return user

class StudentProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Student
        fields = ['bio', 'profile_pic']  # Student model fields
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

