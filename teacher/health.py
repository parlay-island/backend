from django.http import JsonResponse
from rest_framework import status


def health_check(request):
    return JsonResponse({}, status=status.HTTP_200_OK)
