import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'send_reminder_every_day_at_8_am': {
        'task': 'okr.tasks.check_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'process-notification-queue': {
        'task': 'notifications.tasks.process_notification_queue',
        'schedule': crontab(minute='*/1'),
    },
}
app.autodiscover_tasks()
