import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruiting_agent.settings.base')
application = get_wsgi_application()
