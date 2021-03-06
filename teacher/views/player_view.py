import json

from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Player, Response, Level, Question, Teacher, ParlayUser
from teacher.serializer import ResponseSerializer, PlayerSerializer
from teacher.views import post_result, requires_parlay_user

LEVEL = 'level'
NAME = 'name'


@api_view()
def me_controller(request):
    if request.method == 'GET':
        return serialize_me(request)
    return JsonResponse({'error': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view()
def players_controller(request):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Invalid authentication'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_teacher:
        return JsonResponse({'error': 'You do not have an associated teacher account'},
                            status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        return get_all_players(request, user)
    return JsonResponse({'error': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def player_controller(request, playerId):
    if request.method == 'GET':
        return get_single_player(request, playerId)
    return JsonResponse({'error': 'Not implemented'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def player_results_controller(request, playerId):
    try:
        player = Player.objects.get(id=playerId)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Player %s not found' % playerId}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        return post_result(request, player)
    elif request.method == 'GET':
        if request.GET.get(LEVEL):
            return get_results_by_level(request, player)
        return get_results(request, player)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_single_player(request, playerId):
    try:
        player = Player.objects.get(id=playerId)
        return JsonResponse(PlayerSerializer.serialize(player), status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': 'No player found with id [%d]' % playerId},
                            safe=False, status=status.HTTP_404_NOT_FOUND)


def get_all_players(request, user):
    teacher = Teacher.objects.get(user__username=user.username)
    players = Player.objects.order_by('name').filter(assigned_class=teacher.assigned_class)
    players_serialized = list(
        map(lambda player: PlayerSerializer.serialize(player), players))
    return JsonResponse({'players': players_serialized}, safe=False, status=status.HTTP_200_OK)


def get_results(request, player):
    responses = Response.objects.filter(player=player)
    response_list = [ResponseSerializer.serialize(response=response) for response in responses]
    return JsonResponse({'results': response_list}, status=status.HTTP_200_OK)


def get_results_by_level(request, player):
    responses = Response.objects.filter(
        question__in=Question.objects.filter(level__id=request.GET.get(LEVEL),),
        player=player)
    response_list = [ResponseSerializer.serialize(response=response) for response in responses]
    return JsonResponse({'results': response_list}, status=status.HTTP_200_OK)


def serialize_me(request):
    user = request.user
    try:
        if not user.is_authenticated:
            return JsonResponse({'error': 'You are not logged in'}, status=status.HTTP_401_UNAUTHORIZED)
        player = Player.objects.get(user=user)
        return JsonResponse(PlayerSerializer.serialize(player), status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': 'You do not have an associated player account'},
                            status=status.HTTP_401_UNAUTHORIZED)
