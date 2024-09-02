"""
Forms for user authentication and registration.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    """
    Login form with username and password fields.
    Attributes:
        username (CharField): Username field.
        password (CharField): Password field.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    """
    Registration form for new users.
    Attributes:
        password (CharField): Password field.
        password2 (CharField): Repeat password field.
    """
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput
    )

    class Meta:
        """
        Configuration for User model form.
        Attributes:
            model (User): Model to use.
            fields (list): Fields to include in the form.
        """
        model = get_user_model()
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        """
        Validate password and repeat password match.
        Returns:
            str: Cleaned password value.
        """
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']

    def clean_email(self):
        """
        Validate email is unique.
        Returns:
            str: Cleaned email value.
        """
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data


class UserEditForm(forms.ModelForm):
    """
    Form for editing existing user information.
    Attributes:
        fields (list): Fields to include in the form.
    """
    class Meta:
        """
        Configuration for User model form.

        Attributes:
            model (User): Model to use.
            fields (list): Fields to include in the form.
        """

        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        """
        Validate email is unique.
        Returns:
            str: Cleaned email value.
        """
        data = self.cleaned_data['email']
        qs = User.objects.exclude(
            id=self.instance.id
        ).filter(
            email=data
        )
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data


class ProfileEditForm(forms.ModelForm):
    """
    Form for editing user profile information.
    Attributes:
        fields (list): Fields to include in the form.
    """
    class Meta:
        """
        Configuration for Profile model form.
        Attributes:
            model (Profile): Model to use.
            fields (list): Fields to include in the form.
        """
        model = Profile
        fields = ['date_of_birth', 'photo']
