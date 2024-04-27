#!/bin/sh

python manage.py migrate --no-input

gunicorn storage.wsgi:application --bind 0.0.0.0:8000
COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]