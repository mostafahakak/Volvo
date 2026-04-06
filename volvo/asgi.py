"""
ASGI config for volvo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volvo.settings')

application = get_asgi_application()

from volvo.deployment_banner import print_deployment_banner  # noqa: E402

print_deployment_banner("ASGI")
