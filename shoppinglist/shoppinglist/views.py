import os
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from .models import User, ShoppingList, Store, MediaFile
from .forms import ProfileForm, UserRegistrationForm, ShoppingForm
import datetime
from django.contrib import messages
from django_registration.backends.activation.views import RegistrationView
from django.utils.translation import gettext as _
import docupy
import re

def index_view(request):
    return render(request, "index.html")

def about_view(request):
    try:
        with open("../ShoppingList_Concept.md") as f:
            desc_text = f.read()
            desc_text = re.sub(r"(?<!\n)\n(?![\n-])", " ", desc_text)
            desc_text = re.sub(r"  ", " ", desc_text)
            desc = docupy.markdown_to_html(desc_text.replace("\r", ""), MediaFile.media_lookup())
    except IOError:
        desc = ""
    return render(request, "about.html", {"description": desc})

def shoppinglist_view(request):
    stores = Store.objects.all()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ShoppingForm(data=request.POST)
        print(form)
        # check whether it's valid:
        if form.is_valid():
            shopping = form.save(commit=False)
            shopping.submit_date = datetime.datetime.now()
            shopping.save()
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 _('Bitte korrekt ausfuellen.'))
        return HttpResponseRedirect('')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ShoppingForm()
        # print(form.fields)
        return render(request, "shoppinglist.html", {'form': form, 'stores': stores})

def media_view(request):
    if request.method == "POST":
        if "delete" in request.POST:
            media = MediaFile.objects.get(name=request.POST["name"])
            try:
                os.remove(media.mediafile.path)
            except FileNotFoundError: pass
            media.delete()
            return HttpResponseRedirect("/media/")
        try:
            MediaFile.objects.create(
             name=request.POST["name"], mediafile=request.FILES["file"]
            )
        except IntegrityError:
            return render(request, "media.html", {
             "error": "There is already media with that name",
             "media": MediaFile.objects.all()
            })
        return HttpResponseRedirect("/media/")
    else:
        return render(request, "media.html", {
        "media": MediaFile.objects.all()
        })




class register_view(RegistrationView):
    # if this is a POST request we need to process the form data
    template_name = 'django_registration/registration_form.html'
    form_class = UserRegistrationForm

    def post(self, request, *args, **kwargs):
        # create a form instance and populate it with data from the request:
        form = self.form_class(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            self.create_inactive_user(form)
            return HttpResponseRedirect('complete')
        return render(request, self.template_name, {'form': form})

    # if a GET (or any other method) we'll create a blank form
    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm()
        # print(form.fields)
        return render(request, self.template_name, {'form': form})



def profile_view(request):
    user = request.user
    # if this is a POST request we need to process the form data
    if user.is_authenticated:
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = ProfileForm(data=request.POST, instance=request.user)
            # check whether it's valid:
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #print(form)
            #print(form.errors)

            if form.is_valid():
                newuser = form.save(commit=False)
                print(User.objects.filter(email=newuser.email), user.email)
                if user.email == newuser.email or not User.objects.filter(email=newuser.email):
                    newuser.save()
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         _('Email already used.'))
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     _('Bad input.'))
            return HttpResponseRedirect('')

        # if a GET (or any other method) we'll create a blank form
        else:
            form = ProfileForm(instance=request.user)
            return render(request,
                          'profile.html',
                          {'form': form,
                           'user': request.user})
    else:
        return render(request,
                      'profile.html',
                      {'user': user})
