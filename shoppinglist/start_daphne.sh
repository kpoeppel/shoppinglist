#!/bin/bash
yes "yes" | python manage.py collectstatic
cp shoppinglist/settings_deploy.py shoppinglist/settings.py
daphne shoppinglist.asgi:application --bind 0.0.0.0 --port 9000 --verbosity 1
