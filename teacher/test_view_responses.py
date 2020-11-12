from django.http import HttpRequest
from django.test import TestCase
from hamcrest import assert_that, is_

from teacher.views import requires_parlay_user, ParlayUser


def mock_function(request):
    pass


class MockUser:
    username = 'Not real user'


class ViewResponsesTestCase(TestCase):
    @staticmethod
    def test_not_authenticated():
        request = HttpRequest()
        request.user = MockUser()
        assert_that(requires_parlay_user(mock_function)(request).status_code, is_(401))
