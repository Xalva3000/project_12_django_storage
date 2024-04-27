import os
from django.core.mail import send_mail
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
# redis_path = "redis://127.0.0.1:6379" if os.name == 'nt' else "redis://redis:6379/0"
app = Celery("notification")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task
def ceo_notification(data):
    print('sending email')
    if 'pk' in data:
        send_mail('contract reserve status',
                  f"switched reserve status of contract {data['pk']}",
                  'storage-site@yandex.ru',
                  ['maasania@gmail.com'],
                  fail_silently=False)
