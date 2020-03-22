"""shoppinglist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url
from . import views


urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"", views.about_view),
    path(r"shoppinglist", views.shoppinglist_view),
    path(r"order-<str:order_id>", views.order_view),
    path(r"accounts/register/", views.register_view.as_view()),
    url(r'^accounts/', include('django_registration.backends.activation.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    path(r'accounts/profile/', views.profile_view),
    path(r'plan', views.plan_view),
    path(r'helperlist', views.helperlist_view),
    path(r'work', views.work_view),
    path(r'pickup-store-<str:store_id>', views.pickup_store_view),
    path(r'deliverfrom-store-<str:store_id>', views.deliverfrom_store_view),
    path(r'deliver', views.deliver_view),
    path(r'delivering', views.delivering_view),
    path(r'delivered', views.delivered_view),
    path(r"impressum", views.impressum_view),
    path(r"rules", views.rules_view),
    path(r"privacy", views.privacy_view),

]
