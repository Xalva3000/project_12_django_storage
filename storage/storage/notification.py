import os

from django.core.mail import send_mail, EmailMessage
from celery import Celery

from storage.settings import EMAIL_HOST_USER, USE_CELERY, BASE_DIR

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
# redis_path = "redis://127.0.0.1:6379" if os.name == 'nt' else "redis://redis:6379/0"
app = Celery("notification")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task
def ceo_notification(data, email=EMAIL_HOST_USER):
    if 'pk' in data:
        print('sending email')
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

@app.task
def send_db_file():
    print('db_send')
    email = EmailMessage(
        'Database Backup',
        'Please find the database backup attached.',
        'storage-site@yandex.ru',
        ['maasania@gmail.com', 'storage-site@yandex.ru'],
    )
    email.attach_file(BASE_DIR / 'db.sqlite3')
    email.send()

