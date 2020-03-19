from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext as _
import json
import datetime

timeslots = ["8 - 10", "10 - 12", "12 - 14", "14 - 16", "16 - 18", "18 - 20"]
defaultplan = [{"date": (datetime.datetime.today()+datetime.timedelta(i)).date().isoformat(),
                "timeslots": [{"timeslot": s} for s in timeslots]} for i in range(7)]

class User(AbstractUser):
    # add additional fields in here
    number = models.CharField(blank=True, default='', max_length=30)
    name = models.CharField(max_length=100)
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    address = models.TextField()
    REQUIRED_FIELDS = ['username', 'number']
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
    submitted = models.BooleanField(default=False)

class WeekPlan(models.Model):
    plan = models.TextField(default=json.dumps(defaultplan))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    editTime = models.DateField()

class MediaFile(models.Model):
    def create_filename(instance, filename):
        extension = "." + filename.split(".")[-1] if "." in filename else ""
        return datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S") + extension

    def media_lookup():
        return {
         media.name: media.mediafile.url for media in MediaFile.objects.all()
        }

    name = models.TextField(primary_key=True)
    mediafile = models.FileField(upload_to=create_filename)

    def __str__(self):
        return "MediaFile ({})".format(self.name)
