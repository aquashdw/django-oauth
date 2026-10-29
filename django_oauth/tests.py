import os
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings

from django_oauth.context_processors import environment_variables


class EnvironmentVariablesContextProcessorTests(SimpleTestCase):
    @override_settings(TEMPLATE_ENVIRONMENT_VARIABLES=('PUBLIC_VALUE', 'MISSING_VALUE'))
    @patch.dict(os.environ, {'PUBLIC_VALUE': 'available', 'UNLISTED_VALUE': 'hidden'})
    def test_only_configured_present_variables_are_added_to_context(self):
        context = environment_variables(RequestFactory().get('/'))

        self.assertEqual(context, {'PUBLIC_VALUE': 'available'})
