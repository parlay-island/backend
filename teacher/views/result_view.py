"""
result_view.py

Authors: Jake Derry, Holly Ansel, Jessica Su

Contains views that interact with teacher.models.Result and teacher.models.Response.
These resources are not well-separated in the current API.

When posting a result, a result with a list of questions is given. The questions produce
Response objects, but the other fields create a Result object.

When getting a result, for endpoints in this file, the result objects are returned, but
in player_view.py, the Response object is returned.
"""

import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

from teacher.models import Result, Level, Question, Response
from teacher.serializer import ResultSerializer
from teacher.views import get_paginated_results, LEVEL, method_not_allowed, ok, created, not_found, must_define
from teacher.views.view_config import PAGE_SIZE, DISTANCE, AWARD_LIST, QUESTIONS, ACCURACY, QUESTION_ID, CHOICE_ID, \
    GET, PAGE, RESULTS


@api_view()
def results_controller(request):
    if request.method == GET:
        return get_all_results(request)
    return method_not_allowed()


def get_all_results(request):
    results = Result.objects.order_by('-%s' % DISTANCE).all()
    page_number = request.GET.get(PAGE)
    results_serialized = list(
        map(lambda result: ResultSerializer.serialize(result), results))
    if page_number is not None:
        results_serialized = get_paginated_results(
            results_serialized, PAGE_SIZE, page_number)
    return ok({RESULTS: results_serialized})


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
        return created({RESULTS: result_serialized})
    except ObjectDoesNotExist:
        return not_found(LEVEL, payload[LEVEL])
    except KeyError as e:
        return must_define(str(e))


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
    response, _ = Response.objects.get_or_create(player=player, question=question, choice=choice)
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


