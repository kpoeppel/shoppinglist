#!/bin/bash
daphne shoppinglist.asgi:application --bind 0.0.0.0 --port 9000 --verbosity 1
