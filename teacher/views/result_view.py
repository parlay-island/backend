import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from teacher.models import Result, Level, Question, Response, Player, Class
from teacher.serializer import ResultSerializer
from teacher.views import get_paginated_results, LEVEL

PAGE_SIZE = 10
DISTANCE = 'distance'
PLAYER_ID = 'player_id'
QUESTIONS = 'questions'
QUESTION_ID = 'question_id'
CHOICE_ID = 'choice_id'
ACCURACY = 'accuracy'
AWARD_LIST = 'award_list'


@api_view()
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
            level=Level.objects.get(id=payload[LEVEL]),
            assigned_class=player.assigned_class,
            award_list=payload[AWARD_LIST] if AWARD_LIST in payload else []
        )
        update_responses(payload[QUESTIONS], player)
        update_player_accuracy(player)
        result_serialized = ResultSerializer.serialize(result)
        return JsonResponse({'results': result_serialized}, safe=False, status=status.HTTP_201_CREATED)
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
    for response_request in responses_request:
        add_response(response_request, player)


def add_response(response_request, player):
    question = Question.objects.get(id=response_request[QUESTION_ID])
    question.times_answered += 1
    choice = response_request[CHOICE_ID]
    update_choice_times_chosen(question, choice)
    response, created = Response.objects.get_or_create(player=player, question=question, choice=choice)
    response.count += 1
    response.save()

    if response.get_is_correct():
        question.times_correct += 1
    question.save()


def update_choice_times_chosen(question, choiceIndex):
    for index, choice in enumerate(question.get_choices()):
        if index == choiceIndex:
            choice.times_chosen += 1
            choice.save()


