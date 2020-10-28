import json

from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from teacher.models import Result, Level
from teacher.serializer import ResultSerializer, LevelSerializer
from teacher.views import get_paginated_results

PAGE_SIZE = 10
LEVEL = 'level'


def levels_controller(request):
    if request.method == 'GET':
        return get_levels(request)
    if request.method == 'POST':
        return post_level(request)
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def level_controller(request, level_id):
    if request.method == 'GET':
        return get_level(request, level_id)
    if request.method == 'DELETE':
        return delete_level(request, level_id)
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def level_results_controller(request, level):
    if request.method == 'GET':
        return get_results_by_level(request, level)
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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


def post_level(request):
    payload = json.loads(request.body)
    try:
        level = Level.objects.create(name=payload['name'])
        return JsonResponse(LevelSerializer.serialize(level), safe=False, status=status.HTTP_200_OK)
    except KeyError as e:
        return JsonResponse({'error': 'Must define %s' % str(e)}, safe=False, status=status.HTTP_400_BAD_REQUEST)


def delete_level(request, level_id):
    if not Level.objects.filter(id=level_id).exists():
        return JsonResponse({'error': 'No question found with id [%d]' % level_id}, safe=False, status=status.HTTP_404_NOT_FOUND)

    level = Level.objects.get(pk=level_id)
    level_serialized = LevelSerializer.serialize(level)
    level.delete()
    return JsonResponse(level_serialized, safe=False, status=status.HTTP_200_OK)


def get_level(request, level_id):
    try:
        question = Level.objects.get(pk=level_id)
        return JsonResponse(LevelSerializer.serialize(question), status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'No question found with id [%d]' % level_id},
                            safe=False, status=status.HTTP_404_NOT_FOUND)
