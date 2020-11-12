from django.http import JsonResponse
from rest_framework import status


def not_found(_type, _id):
    return JsonResponse({'error': 'No [%s] found with id [%d]' % (_type, _id)}, safe=False,
                        status=status.HTTP_404_NOT_FOUND)


def must_define(parameter):
    return JsonResponse({'error': 'Must define %s' % str(parameter)},
                        safe=False, status=status.HTTP_400_BAD_REQUEST)


def ok(data):
    return JsonResponse(data, safe=False, status=status.HTTP_200_OK)


def method_not_allowed():
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def not_authenticated():
    return JsonResponse({'error': 'You are not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
