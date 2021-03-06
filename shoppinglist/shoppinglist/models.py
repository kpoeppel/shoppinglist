from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext as _
import json
import datetime
from enum import Enum


timeslots = ["8 - 10", "10 - 12", "12 - 14", "14 - 16", "16 - 18", "18 - 20"]
defaultplan = [{"date": (datetime.datetime.today()+datetime.timedelta(i)).date().isoformat(),
                "timeslots": [{"timeslot": s} for s in timeslots]} for i in range(7)]

class ShoppingListState(Enum):   # A subclass of Enum
    Creation = "Creation"
    Ordered = "Ordered"
    Picked = "Picked"
    Delivering = "Delivering"
    Delivered = "Delivered"
    Paid = "Paid?"

class User(AbstractUser):
    # add additional fields in here
    username = models.CharField(_('Nutzername'), max_length=100)
    number = models.CharField(_('Telefonnummer'), blank=True, default='', max_length=30)
    first_name = models.CharField(_('Vorname'), max_length=100)
    last_name = models.CharField(_('Nachname'), max_length=100)
    email = models.EmailField(_('Email-Adresse'), unique=True)
    address = models.TextField(_('Adresse'), max_length=100)
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'number']
    USERNAME_FIELD = 'email'
    def __str__(self):
        return self.email


class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    # image = models.CharField(max_length=128)
    def __str__(self):
        return "{}".format(self.name)

class ShoppingList(models.Model):
    submit_date = models.DateField()
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    number = models.CharField(blank=True, default='', max_length=30)
    email = models.EmailField(blank=True, default='')
    items = models.TextField()
    state = models.CharField(
      max_length=10,
      default = ShoppingListState.Creation,
      choices=[(tag, tag.value) for tag in ShoppingListState]  # Choices is a list of Tuple
    )

class Delivery(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    shoppinglist = models.ForeignKey(ShoppingList,
                                     on_delete=models.CASCADE)

class TimeSlot(models.Model):
    date = models.DateField()
    slotnum = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, blank=True)
    changedby = models.IntegerField(default=0)
    entry = models.TextField(blank=True, default='')

    def __str__(self):
        return "{},{}:\n{}\n({},{})".format(self.date, self.slotnum, self.entry, self.created, self.changedby)

class MediaFile(models.Model):
    def create_filename(instance, filename):
        extension = "." + filename.split(".")[-1] if "." in filename else ""
        return datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d-%H%M%S") + extension
    def media_lookup():
        return {
         media.name: media.mediafile.url for media in MediaFile.objects.all()
        }

    name = models.TextField(primary_key=True)
    mediafile = models.FileField(upload_to=create_filename)

    def __str__(self):
        return "MediaFile ({})".format(self.name)
