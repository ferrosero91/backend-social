import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruiting_agent.settings.base')

app = Celery('recruiting_agent')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
