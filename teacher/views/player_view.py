from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Player
from teacher.views import post_result


def player_results_controller(request, playerId):
    if request.method == 'POST':
        try:
            player = Player.objects.get(id=playerId)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Player %s not found' % playerId}, status=status.HTTP_404_NOT_FOUND)
        return post_result(request, player)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
