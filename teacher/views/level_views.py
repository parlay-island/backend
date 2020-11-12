import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

from teacher.models import Result, Level, ParlayUser, Teacher, Player
from teacher.serializer import ResultSerializer, LevelSerializer
from teacher.views import get_paginated_results

PAGE_SIZE = 10
LEVEL = 'level'


@api_view(['GET', 'POST'])
def levels_controller(request):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'You are not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        return get_levels(request, user)
    if request.method == 'POST':
        return post_level(request, user)
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def level_controller(request, level_id):
    if request.method == 'GET':
        return get_level(request, level_id)
    if request.method == 'DELETE':
        return delete_level(request, level_id)
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view()
def level_results_controller(request, level):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'You are not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        return get_results_by_level(request, level, user)
    return JsonResponse({'error': 'Method Not Allowed'}, safe=False, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_results_by_level(request, level, user):
    results = Result.objects.filter(level=Level.objects.get(id=level),
                                    assigned_class=user.get_assigned_class())\
        .order_by('-distance') if len(Level.objects.filter(id=level)) > 0 else []
    page_number = request.GET.get('page')
    results_serialized = list(map(lambda result: ResultSerializer.serialize(result), results))
    if page_number is not None:
        results_serialized = get_paginated_results(results_serialized, PAGE_SIZE, page_number)
    return JsonResponse({'results': results_serialized}, safe=False, status=status.HTTP_200_OK)


def get_levels(request, user):
    levels = Level.objects.filter(assigned_class=user.get_assigned_class())
    levels_serialized = list(map(lambda level: LevelSerializer.serialize(level), levels))
    return JsonResponse({'levels': levels_serialized}, safe=False, status=status.HTTP_200_OK)


def post_level(request, user):
    payload = json.loads(request.body)
    try:
        level = Level.objects.create(name=payload['name'], assigned_class=user.get_assigned_class())
        print(level)
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
