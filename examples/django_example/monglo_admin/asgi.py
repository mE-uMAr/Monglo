
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monglo_admin.settings')

django_asgi_app = get_asgi_application()

from monglo_admin.urls import initialize
import asyncio
asyncio.create_task(initialize())

application = django_asgi_app
