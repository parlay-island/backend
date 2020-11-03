import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Player, Response
from teacher.serializer import ResponseSerializer, PlayerSerializer
from teacher.views import post_result

LEVEL = 'level'
NAME = 'name'


def players_controller(request):
    if request.method == 'POST':
        return post_player(request)
    return JsonResponse({'error': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def player_controller(request):
    return JsonResponse({'error': 'Not implemented'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def player_results_controller(request, playerId):
    try:
        player = Player.objects.get(id=playerId)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Player %s not found' % playerId}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        return post_result(request, player)
    elif request.method == 'GET':
        return get_results(request, player)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_results(request, player):
    responses = Response.objects.filter(player=player)
    response_list = [ResponseSerializer.serialize(response=response) for response in responses]
    return JsonResponse({'results': response_list}, status=status.HTTP_200_OK)


def post_player(request):
    payload = json.loads(request.body)
    player = Player.objects.create(name=payload[NAME])
    return JsonResponse(PlayerSerializer.serialize(player), status=status.HTTP_201_CREATED)
