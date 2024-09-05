from celery.schedules import crontab
from django.conf import settings
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'usaid.settings')

app = Celery('usaid')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'scheduler_transaction_retry': {
        'task': 'apps.transaction.tasks.scheduler_transaction_retry',
        'schedule': crontab(minute="0", hour="*/3"),
    },
    'scheduler_transaction_sitb_retry': {
        'task': 'apps.transaction.tasks.scheduler_transaction_sitb_retry',
        'schedule': crontab(minute="0", hour="*/3"),
    },
}

app.conf.update(
    BROKER_TRANSPORT_OPTIONS={
        'visibility_timeout': 604800
    }
)

app.conf.task_routes = [

]


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
