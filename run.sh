#!/usr/bin/env bash

source env/bin/activate
export DJANGO_DEVELOPMENT=true
python3 manage.py runserver
deactivate
