from unittest import TestCase

from django.test import Client
from hamcrest import assert_that, is_


class HealthTestCase(TestCase):
    client = Client()

    def test_health_check(self):
        assert_that(self.client.get('/').status_code, is_(200))
