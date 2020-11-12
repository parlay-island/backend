"""
player_view.py

Contains views that interact with teacher.models.Player.

Authors: Jake Derry, Holly Ansel

WARNING: GET `players/results/` will return Response objects rather than the expected
Result object.
"""

from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Player, Response, Question, Teacher, ParlayUser
from teacher.serializer import ResponseSerializer, PlayerSerializer
from teacher.views import post_result, method_not_allowed, not_authenticated, not_found, ok
from teacher.views.view_config import PLAYER, LEVEL, NAME, PLAYERS, RESULTS, GET, POST, ERROR


def player_not_found(player_id):
    return not_found(PLAYER, player_id)


@api_view()
def me_controller(request):
    if request.method == GET:
        return serialize_me(request)
    return method_not_allowed()


@api_view()
def players_controller(request):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return not_authenticated()
    if not user.is_teacher:
        return JsonResponse({ERROR: 'You do not have an associated teacher account'},
                            status=status.HTTP_401_UNAUTHORIZED)
    if request.method == GET:
        return get_all_players(request, user)
    return method_not_allowed()


@api_view()
def player_controller(request, player_id):
    if request.method == GET:
        return get_single_player(request, player_id)
    return method_not_allowed()


@api_view([GET, POST])
def player_results_controller(request, player_id):
    try:
        player = Player.objects.get(id=player_id)
    except ObjectDoesNotExist:
        return player_not_found(player_id)
    if request.method == POST:
        return post_result(request, player)
    elif request.method == GET:
        if request.GET.get(LEVEL):
            return get_player_results_by_level(request, player)
        return get_results_by_player(request, player)
    return method_not_allowed()


def get_single_player(request, player_id):
    try:
        player = Player.objects.get(id=player_id)
        return JsonResponse(PlayerSerializer.serialize(player), status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        return not_found(PLAYER, player_id)


def get_all_players(request, user):
    teacher = Teacher.objects.get(user__username=user.username)
    players = Player.objects.order_by(NAME).filter(assigned_class=teacher.assigned_class)
    players_serialized = list(
        map(lambda player: PlayerSerializer.serialize(player), players))
    return ok({PLAYERS: players_serialized})


def get_results_by_player(request, player):
    responses = Response.objects.filter(player=player)
    response_list = [ResponseSerializer.serialize(response=response) for response in responses]
    return ok({RESULTS: response_list})


def get_player_results_by_level(request, player):
    responses = Response.objects.filter(
        question__in=Question.objects.filter(level__id=request.GET.get(LEVEL)),
        player=player)
    response_list = [ResponseSerializer.serialize(response=response) for response in responses]
    return ok({RESULTS: response_list})


def serialize_me(request):
    user = request.user
    try:
        if not user.is_authenticated:
            return not_authenticated()
        player = Player.objects.get(user=user)
        return ok(PlayerSerializer.serialize(player))
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'You do not have an associated player account'},
                            status=status.HTTP_401_UNAUTHORIZED)
