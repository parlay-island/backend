from django.http import JsonResponse
from rest_framework import status

from teacher.models import Result, Level
from teacher.serializer import ResultSerializer, LevelSerializer
from teacher.views import get_paginated_results

PAGE_SIZE = 10


def levels_controller(request):
    if request.method == 'GET':
        return get_levels(request)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def level_results_controller(request, level):
    if request.method == 'GET':
        return get_results_by_level(request, level)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def units_controller(request):
    return JsonResponse({"units": ["Economics",
                                   "Income & Education",
                                   "Money & Credit Management",
                                   "Financial Planning",
                                   "Critical Consumerism"]
                         }, safe=False, status=status.HTTP_200_OK)


def get_results_by_level(request, level):
    results = Result.objects.filter(level=Level.objects.get(id=level)).order_by('-distance') \
        if len(Level.objects.filter(id=level)) > 0 else []
    page_number = request.GET.get('page')
    results_serialized = list(map(lambda result: ResultSerializer.serialize(result), results))
    if page_number is not None:
        results_serialized = get_paginated_results(results_serialized, PAGE_SIZE, page_number)
    return JsonResponse({'results': results_serialized}, safe=False, status=status.HTTP_200_OK)


def get_levels(request):
    levels = Level.objects.all()
    levels_serialized = list(map(lambda level: LevelSerializer.serialize(level), levels))
    return JsonResponse({'levels': levels_serialized}, safe=False, status=status.HTTP_200_OK)
