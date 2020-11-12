"""
view_responses.py

Contains utility functions and decorator functions for more readable
and declarative view methods.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpRequest
from rest_framework import status

from teacher.models import ParlayUser


def requires_parlay_user(func):
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[0]
        try:
            user = ParlayUser.objects.get(username=request.user.username)
        except ObjectDoesNotExist:
            return not_authenticated()
        return func(*args, **kwargs, user=user)
    return wrapper


def not_found(_type, _id):
    return JsonResponse({'error': 'No [%s] found with id [%d]' % (_type, _id)}, safe=False,
                        status=status.HTTP_404_NOT_FOUND)


def must_define(parameter):
    return JsonResponse({'error': 'Must define %s' % str(parameter)},
                        safe=False, status=status.HTTP_400_BAD_REQUEST)


def ok(data):
    return JsonResponse(data, safe=False, status=status.HTTP_200_OK)


def created(data):
    return JsonResponse(data, safe=False, status=status.HTTP_201_CREATED)


def method_not_allowed():
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def not_authenticated():
    return JsonResponse({'error': 'You are not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
