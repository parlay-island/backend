"""
health.py

Provides a health check endpoint which some cloud deployment services
require including Elastic Beanstalk.
"""
from django.http import JsonResponse
from rest_framework import status


def health_check(request):
    return JsonResponse({}, status=status.HTTP_200_OK)
