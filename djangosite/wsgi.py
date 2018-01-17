<<<<<<< HEAD
"""
WSGI config for djangosite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangosite.settings")

application = get_wsgi_application()
=======
"""
WSGI config for djangosite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangosite.settings")

application = get_wsgi_application()
>>>>>>> 64d5b50a23ee4bd33e7ebc3854e494618345a6e9
