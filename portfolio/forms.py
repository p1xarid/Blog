from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UsernameUpdateForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "New username"}
        ),
    )

    def clean_username(self):
        new_username = self.cleaned_data["username"]
        if User.objects.filter(username=new_username).exists():
            raise forms.ValidationError("This username is already taken.")
        return new_username


class EmailUpdateForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "New email"}
        ),
    )

    def clean_email(self):
        new_email = self.cleaned_data["email"]
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError("This email is already in use.")
        return new_email


class PasswordUpdateForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
        label="Current password",
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
        label="New password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
        label="Confirm password",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Wrong current password")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        if new_password:
            validate_password(new_password, self.user)

        return cleaned_data
