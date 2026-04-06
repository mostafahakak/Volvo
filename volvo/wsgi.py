"""
WSGI config for volvo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volvo.settings')

application = get_wsgi_application()

from volvo.deployment_banner import print_deployment_banner  # noqa: E402

print_deployment_banner("WSGI")
