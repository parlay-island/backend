import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status


from teacher.models import Result, Level, Question, Response, Player
from teacher.serializer import ResultSerializer, ResponseSerializer
from teacher.views import get_paginated_results, LEVEL

PAGE_SIZE = 10
DISTANCE = 'distance'
PLAYER_ID = 'player_id'
QUESTIONS = 'questions'
QUESTION_ID = 'question_id'
CHOICE_ID = 'choice_id'
ACCURACY = 'accuracy'

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
<<<<<<< HEAD

        update_player_accuracy(player)
=======
>>>>>>> added distance and level back to response
        result_serialized = ResultSerializer.serialize(result)
        response_list = update_responses(payload[QUESTIONS], player)
        response_serialized = [ResponseSerializer.serialize(response) for response in response_list]
        return JsonResponse({'distance': result_serialized[DISTANCE], 'level': result_serialized[LEVEL],
                             'question_results': response_serialized}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except KeyError as e:
        return JsonResponse({'error': 'Must define %s' % str(e)}, safe=False, status=status.HTTP_400_BAD_REQUEST)

def update_player_accuracy(player):
    responses = Response.objects.filter(player=player.id)
    num_questions_correct = 0
    total = 0
    for response in responses:
        total += response.count
        if response.get_is_correct():
            num_questions_correct += response.count
    if total is 0:
        accuracy = 100.0
    else:
        accuracy = (num_questions_correct / total) * 100
    setattr(player, ACCURACY, accuracy)
    player.save()

def update_responses(responses_request, player):
    response_list = []
    for response_request in responses_request:
        response_list.append(add_response(response_request, player))
    return response_list


def add_response(response_request, player):
    question = Question.objects.get(id=response_request[QUESTION_ID])
    choice = response_request[CHOICE_ID]
    response, created = Response.objects.get_or_create(player=player, question=question, choice=choice)
    response.count += 1
    response.save()
    return response
