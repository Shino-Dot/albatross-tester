#!/bin/sh

# Gunicornで、Djangoアプリを起動するだけ！
gunicorn albatross.wsgi --bind 0.0.0.0:8000