import os
from django.core.mail import send_mail
from celery import Celery

from storage.settings import EMAIL_HOST_USER, USE_CELERY

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
# redis_path = "redis://127.0.0.1:6379" if os.name == 'nt' else "redis://redis:6379/0"
app = Celery("notification")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task
def ceo_notification(data, email):
    print('sending email')
    if 'pk' in data:
        send_mail('contract reserve status',
                  f"switched reserve status of contract {data['pk']}",
                  'storage-site@yandex.ru',
                  [email],
                  fail_silently=False)


def notify_tasker(data, /, *, email=EMAIL_HOST_USER, fail_silently=True):
    if fail_silently:
        try:
            if USE_CELERY:
                print('using_celery')
                ceo_notification.delay(data, email)
            else:
                ceo_notification(data, 'maasania@gmail.com')
        except:
            pass
    else:
        if USE_CELERY:
            ceo_notification.delay(data, email)
        else:
            ceo_notification(data, 'maasania@gmail.com')
