import os

from django.conf import settings


def environment_variables(request):
    return {
        name: os.environ[name]
        for name in settings.TEMPLATE_ENVIRONMENT_VARIABLES
        if name in os.environ
    }
