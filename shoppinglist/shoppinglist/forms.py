from django import forms
from .models import User, ShoppingList, ShoppingListState, Delivery
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django_registration.forms import RegistrationForm

class SelectForm(forms.Form):
    choice_field = forms.ChoiceField(label="Laden: ", choices=())

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'number')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'number']
        field_classes = {'username': UsernameField}

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')


class UserRegistrationForm(RegistrationForm):

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'number']

class ShoppingForm(forms.ModelForm):

    class Meta:
        model = ShoppingList
        fields = ['name', 'address', 'number', 'email', 'items']
