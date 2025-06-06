import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')

# Create the Celery app
app = Celery('projet')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django app configs
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'scrape-emploidakar-every-30-minutes': {
        'task': 'scrap_emploi.tasks.scrape_emploidakar_periodic',
        'schedule': 30 * 60,  # 30 minutes in seconds
    },
    'scrape-emploisenegal-every-30-minutes': {
        'task': 'scrap_emploi.tasks.scrape_emploisenegal_periodic',
        'schedule': 30 * 60,  # 30 minutes in seconds
    },
} 