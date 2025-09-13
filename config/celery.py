import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-quest-status': {
        'task': 'api.tasks.update_quest_status',
        'schedule': timedelta(hours=1),  # Run every hour
    },
    'send-daily-digest': {
        'task': 'api.tasks.send_daily_digest',
        'schedule': crontab(hour=8, minute=0),  # Run daily at 8 AM
    },
    'cleanup-expired-sessions': {
        'task': 'django.contrib.sessions.clearsessions',
        'schedule': crontab(hour=3, minute=0),  # Run daily at 3 AM
    },
}

# Set up error emails for task failures
app.conf.worker_send_task_events = True
app.conf.worker_hijack_root_logger = False

# Configure task timeouts and retries
app.conf.task_time_limit = 30 * 60  # 30 minutes
app.conf.task_soft_time_limit = 25 * 60  # 25 minutes
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_track_started = True

# Configure result backend
app.conf.result_backend = settings.CELERY_RESULT_BACKEND
app.conf.result_expires = timedelta(days=1)

# Configure broker connection retry settings
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_max_retries = 10

# Add custom task error handling
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery is working."""
    print(f'Request: {self.request!r}')
