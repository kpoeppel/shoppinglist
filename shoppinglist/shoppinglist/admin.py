from django.contrib import admin
from . import models
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ProfileForm, CustomUserCreationForm
from .models import User, ShoppingList

admin.site.register(models.Store)
admin.site.register(models.ShoppingList)
admin.site.register(models.TimeSlot)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = ProfileForm
    model = User
    list_display = ['email', 'username', ]

admin.site.register(User, CustomUserAdmin)
