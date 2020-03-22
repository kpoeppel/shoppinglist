import os
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from .models import User, ShoppingList, Store, MediaFile, TimeSlot, ShoppingListState, Delivery
from .settings import TIMESLOTS
from .forms import ProfileForm, UserRegistrationForm, ShoppingForm, SelectForm
import datetime
from django.contrib import messages
from django_registration.backends.activation.views import RegistrationView
from django.utils.translation import gettext as _
from django import forms
import docupy
import json
import re

def index_view(request):
    return render(request, "index.html")

def about_view(request):
    try:
        with open("../KoopKauf_Concept.md") as f:
            desc_text = f.read()
            desc_text = re.sub(r"(?<!\n)\n(?![\n-])", " ", desc_text)
            desc_text = re.sub(r"  ", " ", desc_text)
            desc = docupy.markdown_to_html(desc_text.replace("\r", ""), MediaFile.media_lookup())
    except IOError:
        desc = ""
    return render(request, "about.html", {"description": desc})

def impressum_view(request):
    try:
        with open("shoppinglist/static/texts/Impressum.md") as f:
            desc_text = f.read()
            desc_text = re.sub(r"(?<!\n)\n(?![\n-])", " ", desc_text)
            desc_text = re.sub(r"  ", " ", desc_text)
            desc = docupy.markdown_to_html(desc_text.replace("\r", ""), MediaFile.media_lookup())
    except IOError:
        desc = ""
    return render(request, "impressum.html", {"description": desc})

def rules_view(request):
    try:
        with open("shoppinglist/static/texts/Rules.md") as f:
            desc_text = f.read()
            desc_text = re.sub(r"(?<!\n)\n(?![\n-])", " ", desc_text)
            desc_text = re.sub(r"  ", " ", desc_text)
            desc = docupy.markdown_to_html(desc_text.replace("\r", ""), MediaFile.media_lookup())
    except IOError:
        desc = ""
    return render(request, "rules.html", {"description": desc})

def privacy_view(request):
    try:
        with open("shoppinglist/static/texts/Privacy.md") as f:
            desc_text = f.read()
            desc_text = re.sub(r"(?<!\n)\n(?![\n-])", " ", desc_text)
            desc_text = re.sub(r"  ", " ", desc_text)
            desc = docupy.markdown_to_html(desc_text.replace("\r", ""), MediaFile.media_lookup())
    except IOError:
        desc = ""
    return render(request, "privacy.html", {"description": desc})


def shoppinglist_view(request):
    stores = Store.objects.all()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ShoppingForm(data=request.POST)
        # check whether it's valid:
        if form.is_valid():
            shopping = form.save(commit=False)
            shopping.submit_date = datetime.datetime.now()
            shopping.state = ShoppingListState.Creation
            shopping.save()
            return HttpResponseRedirect('/order-' + str(shopping.id))
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

def work_view(request):
    if request.method == 'POST':
        print(request.POST['choice_field'])
        store_id = request.POST['choice_field']
        return HttpResponseRedirect('/pickup-store-'+store_id)
    else:
        stores = Store.objects.all()
        form = SelectForm()
        print(form.__dict__)
        form.fields["choice_field"].choices = [(store.id, store.name) for store in stores]
        return render(request, "work.html", {'form': form})

def pickup_store_view(request, store_id):
    if request.method == 'POST':
        id = int(request.POST.get("id", ""))
        print("ID", id, request.POST)
        shoppinglist = get_object_or_404(ShoppingList, id=int(id))
        print(shoppinglist)
        shopping_items = json.loads(shoppinglist.items)
        for its in shopping_items:
            if its['store_id'] == store_id:
                its['picked'] = True
        all_picked = True
        for its in shopping_items:
            if 'picked' not in its or its['picked'] == False:
                all_picked = False
        if all_picked == True:
            shoppinglist.state = ShoppingListState.Picked
        shoppinglist.items = json.dumps(shopping_items)
        shoppinglist.save()
        return HttpResponseRedirect('')
    else:
        store = get_object_or_404(Store, id=store_id)
        shoppinglists = ShoppingList.objects.all()
        shop_items = []
        for shoppinglist in shoppinglists:
            shopping_list_parts = json.loads(shoppinglist.items)
            for shopping_list_part in shopping_list_parts:
                if shopping_list_part['store_id'] == store_id:
                    if 'picked' not in shopping_list_part or shopping_list_part['picked'] == False:
                        shop_items.append({"id": shoppinglist.id, "items": shopping_list_part['items']})
        return render(request, "pickupstore.html", {'store': store, 'shop_items': shop_items})

def deliverfrom_store_view(request, store_id):
    if request.method == 'POST':
        id = request.POST.get("id", "")
        print("ID", id)
        if 'back-' in id:
            id = int(id[5:])
            shoppinglist = get_object_or_404(ShoppingList, id=int(id))
            shopping_items = json.loads(shoppinglist.items)
            for its in shopping_items:
                if its['store_id'] == store_id:
                    its['picked'] = False
            shoppinglist.state = ShoppingListState.Ordered
            shoppinglist.items = json.dumps(shopping_items)
            shoppinglist.save()
        else:
            id = int(id)
            shoppinglist = get_object_or_404(ShoppingList, id=int(id))
            shopping_items = json.loads(shoppinglist.items)
            for its in shopping_items:
                if its['store_id'] == store_id:
                    its['delivering'] = True
            shoppinglist.state = ShoppingListState.Delivering
            shoppinglist.items = json.dumps(shopping_items)
            shoppinglist.save()
        return HttpResponseRedirect('')
    else:
        store = get_object_or_404(Store, id=store_id)
        shoppinglists = ShoppingList.objects.filter()
        shop_items = []
        for shoppinglist in shoppinglists:
            shopping_list_parts = json.loads(shoppinglist.items)
            for shopping_list_part in shopping_list_parts:
                if shopping_list_part['store_id'] == store_id:
                    if 'picked' in shopping_list_part and shopping_list_part['picked'] == True \
                        and ('delivering' not in shopping_list_part or shopping_list_part['delivering'] == False):
                        shop_items.append({"id": shoppinglist.id, "items": shopping_list_part['items']})
        return render(request, "deliverfromstore.html", {'store': store, 'shop_items': shop_items})

def deliver_view(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            id = request.POST.get("id", "")
            if 'back-' in id:
                id = int(id[5:])
                shoppinglist = get_object_or_404(ShoppingList, id=int(id))
                shoppinglist.state = ShoppingListState.Picked
                shoppinglist.save()
            else:
                id = int(id)
                shoppinglist = get_object_or_404(ShoppingList, id=int(id))
                shoppinglist.state = ShoppingListState.Delivering
                Delivery(user=user, shoppinglist=shoppinglist).save()
                shoppinglist.save()
            return HttpResponseRedirect('')
        else:
            shoppinglists = ShoppingList.objects.filter(state="ShoppingListState.Picked")
            shoppinglists = [{"id": shoppinglist.id,           \
                                   "name": shoppinglist.name,          \
                                   "number": shoppinglist.number,       \
                                   "address": shoppinglist.address,     \
                                   "shops": json.dumps(shoppinglist.items)}    \
                                  for shoppinglist in shoppinglists]
            return render(request, "deliver.html", {'user': user, 'shoppinglists': shoppinglists})
    else:
        return render(request, "deliver.html", {'user': user})

def delivering_view(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            id = request.POST.get("id", "")
            if 'back-' in id:
                id = int(id[5:])
                shoppinglist = get_object_or_404(ShoppingList, id=int(id))
                shoppinglist.state = ShoppingListState.Picked
                shoppinglist.save()
                deliveries = Delivery.objects.all()
                delivery = [delivery for delivery in deliveries if delivery.shoppinglist.id == id]
                if delivery:
                    print("Delivery delete")
                    delivery[0].delete()
            else:
                id = int(id)
                shoppinglist = get_object_or_404(ShoppingList, id=int(id))
                shoppinglist.state = ShoppingListState.Delivered
                Delivery(user=user, shoppinglist=shoppinglist).save()
                shoppinglist.save()
            return HttpResponseRedirect('')
        else:
            deliveries = Delivery.objects.all()
            shoppinglists = set([delivery.shoppinglist for delivery in deliveries if delivery.user.id == user.id and delivery.shoppinglist.state == "ShoppingListState.Delivering"])
            shoppinglists = [{"id": shoppinglist.id,           \
                                   "name": shoppinglist.name,          \
                                   "number": shoppinglist.number,       \
                                   "address": shoppinglist.address,     \
                                   "shops": json.loads(shoppinglist.items)}    \
                                  for shoppinglist in shoppinglists]
            return render(request, "delivering.html", {'user': user, 'shoppinglists': shoppinglists})
    else:
        return render(request, "delivering.html", {'user': user})

def delivered_view(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            id = int(request.POST.get("id", ""))
            shoppinglist = get_object_or_404(ShoppingList, id=int(id))
            shoppinglist.state = ShoppingListState.Delivering
            shoppinglist.save()
            return HttpResponseRedirect('')
        else:
            shoppinglists = ShoppingList.objects.filter(state='ShoppingListState.Delivered')
            shoppinglists = [{"id": shoppinglist.id,           \
                                   "name": shoppinglist.name,          \
                                   "number": shoppinglist.number,       \
                                   "address": shoppinglist.address,     \
                                   "shops": json.loads(shoppinglist.items)}    \
                                  for shoppinglist in shoppinglists]
            return render(request, "delivered.html", {'user': user, 'shoppinglists': shoppinglists})
    else:
        return render(request, "delivered.html", {'user': user})


def order_view(request, order_id):
    order = get_object_or_404(ShoppingList, id=int(order_id))
    if order.state != 'ShoppingListState.Creation':
        return HttpResponseNotFound("Page not found")
    if request.method == 'POST':
        order.state = ShoppingListState.Ordered
        return HttpResponseRedirect('')
    else:
        itemlist = ""
        stores = json.loads(order.items)
        for store in stores:
            itemlist += store['store_name'] + ":\n" + store['items'] + "\n\n"
        return render(request, "order.html", {'shoppinglist': order, 'items': itemlist})

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


def get_timeslots():
    today = datetime.datetime.now().date()
    oneday = datetime.timedelta(days=1)
    timeslots = []
    for j in range(len(TIMESLOTS)):
        day = [TIMESLOTS[j]]
        for i in range(7):
            timeslot = TimeSlot.objects.filter(date=today + i*oneday, slotnum=j)
            if not timeslot:
                timeslot = TimeSlot(date=today + i*oneday, slotnum=j)
            else:
                timeslot = timeslot.latest('created')
            day += [timeslot]
        timeslots += [day]
    return timeslots


def profile_view(request):
    user = request.user
    # if this is a POST request we need to process the form data
    if user.is_authenticated:
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            print(request.POST)
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
            timeslots = get_timeslots()
            weekplan = timeslots
            return render(request,
                          'profile.html',
                          {'form': form,
                           'user': request.user})
    else:
        return render(request,
                      'profile.html',
                      {'user': user})


def helperlist_view(request):
    user = request.user
    if user.is_authenticated:
        helpers = User.objects.all()
        print(helpers)
        return render(request,
                      'helperlist.html',
                      {'user': request.user,
                       'helpers': helpers})
    else:
        return render(request,
                      'helperlist.html',
                      {'user': user})

def plan_view(request):
    user = request.user
    # if this is a POST request we need to process the form data
    if user.is_authenticated:
        weekplan = get_timeslots()
        if request.user_agent.is_mobile:
             # returns True
             return render(request,
                        'plan_mobile.html',
                        {'weekplan': weekplan,
                        'user': request.user})
        elif request.user_agent.is_tablet:
            return render(request,
                       'plan.html',
                       {'weekplan': weekplan,
                       'user': request.user})
        elif request.user_agent.is_pc:
            return render(request,
                       'plan.html',
                       {'weekplan': weekplan,
                       'user': request.user})
    else:
        return render(request,
                      'plan.html',
                      {'user': user})
