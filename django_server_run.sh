#!/bin/bash
cd ~/Downloads/raspberrypi_recipe || exit
source venv/bin/activate
python manage.py runserver
