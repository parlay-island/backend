import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

from teacher.models import Result, Level, ParlayUser
from teacher.serializer import ResultSerializer, LevelSerializer
from teacher.views import get_paginated_results
from teacher.views.view_responses import not_found, must_define, ok, method_not_allowed, not_authenticated

PAGE_SIZE = 10
LEVEL = 'level'


def level_not_found(level_id):
    return not_found(LEVEL, level_id)


@api_view(['GET', 'POST'])
def levels_controller(request):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return not_authenticated()
    if request.method == 'GET':
        return get_levels(request, user)
    if request.method == 'POST':
        return post_level(request, user)
    return method_not_allowed()


@api_view(['GET', 'DELETE'])
def level_controller(request, level_id):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return not_authenticated()
    if request.method == 'GET':
        return get_level(request, level_id, user)
    if request.method == 'DELETE':
        return delete_level(request, level_id, user)
    return method_not_allowed()


@api_view()
def level_results_controller(request, level):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return not_authenticated()
    if request.method == 'GET':
        return get_results_by_level(request, level, user)
    return method_not_allowed()


def get_results_by_level(request, level, user):
    results = Result.objects.filter(level=Level.objects.get(id=level),
                                    assigned_class=user.get_assigned_class()) \
        .order_by('-distance') if len(Level.objects.filter(id=level)) > 0 else []
    page_number = request.GET.get('page')
    results_serialized = list(map(lambda result: ResultSerializer.serialize(result), results))
    if page_number is not None:
        results_serialized = get_paginated_results(results_serialized, PAGE_SIZE, page_number)
    return ok({'results': results_serialized})


def get_levels(request, user):
    levels = Level.objects.filter(assigned_class=user.get_assigned_class())
    levels_serialized = list(map(lambda level: LevelSerializer.serialize(level), levels))
    return ok({'levels': levels_serialized})


def post_level(request, user):
    payload = json.loads(request.body)
    try:
        level = Level.objects.create(name=payload['name'], assigned_class=user.get_assigned_class())
        print(level)
        return ok(LevelSerializer.serialize(level))
    except KeyError as e:
        return must_define(e)


def delete_level(request, level_id, user):
    if not Level.objects.filter(id=level_id).exists() \
            or Level.objects.get(id=level_id).assigned_class != user.get_assigned_class():
        return level_not_found(level_id)

    level = Level.objects.get(pk=level_id)
    level_serialized = LevelSerializer.serialize(level)
    level.delete()
    return ok(level_serialized)


def get_level(request, level_id, user):
    if not Level.objects.filter(id=level_id).exists() \
            or Level.objects.get(id=level_id).assigned_class != user.get_assigned_class():
        return level_not_found(level_id)

    question = Level.objects.get(id=level_id)
    return ok(LevelSerializer.serialize(question))

