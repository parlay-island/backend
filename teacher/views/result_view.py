import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Result, Level
from teacher.serializer import ResultSerializer
from teacher.views import get_paginated_results, LEVEL

PAGE_SIZE = 10
DISTANCE = 'distance'
PLAYER_ID = 'player_id'


def results_controller(request):
    if request.method == 'GET':
        return get_all_results(request)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_all_results(request):
    results = Result.objects.order_by('-distance').all()
    page_number = request.GET.get('page')
    results_serialized = list(
        map(lambda result: ResultSerializer.serialize(result), results))
    if page_number is not None:
        results_serialized = get_paginated_results(
            results_serialized, PAGE_SIZE, page_number)
    return JsonResponse({'results': results_serialized}, safe=False, status=status.HTTP_200_OK)


def post_result(request, player):
    payload = json.loads(request.body)
    try:
        result = Result.objects.create(
            distance=payload[DISTANCE],
            player=player,
            level=Level.objects.get(id=payload[LEVEL]) 
        )
        result_serialized = ResultSerializer.serialize(result)
        return JsonResponse({'results': result_serialized}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except KeyError as e:
        return JsonResponse({'error': 'Must define %s' % str(e)}, safe=False, status=status.HTTP_400_BAD_REQUEST)
