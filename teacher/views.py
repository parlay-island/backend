import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Question, Choice, Result
from teacher.serializer import QuestionSerializer, ChoiceSerializer, ResultSerializer

BODY = 'body'
TIMES_ANSWERED = 'times_answered'
TIMES_CORRECT = 'times_correct'
TIMES_CHOSEN = 'times_chosen'
TAGS = 'tags'
ANSWER = 'answer'
TAG = 'tag'
PAGE_SIZE = 10

class BadRequestException(Exception):
    pass


def questions_controller(request):
    if request.method == 'GET':
        if TAG in request.GET:
            return get_questions_by_tag(request, request.GET.get(TAG))
        return get_all_questions(request)
    elif request.method == 'POST':
        return post_question(request)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def question_controller(request, questionId):
    if request.method == 'GET':
        return get_single_question(request, questionId)
    elif request.method == 'PUT':
        return put_question(request, questionId)
    elif request.method == 'DELETE':
        return delete_question(request, questionId)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_all_questions(request):
    questions = Question.objects.all()
    questions_serialized = list(map(lambda question: QuestionSerializer.serialize(question), questions))
    return JsonResponse({'questions': questions_serialized}, safe=False, status=status.HTTP_200_OK)


def get_questions_by_tag(request, tag):
    questions = Question.objects.filter(tags__contains=[tag])
    questions_serialized = list(map(lambda question: QuestionSerializer.serialize(question), questions))
    return JsonResponse({'questions': questions_serialized}, safe=False, status=status.HTTP_200_OK)


def get_single_question(request, questionId):
    try:
        question = Question.objects.get(pk=questionId)
        return JsonResponse(QuestionSerializer.serialize(question), status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': 'No question found with id [%d]' % questionId},
                            safe=False, status=status.HTTP_404_NOT_FOUND)


def post_question(request):
    payload = json.loads(request.body)
    try:
        (question_map, question) = add_question(payload)
        full_question_map = add_choices(question_map, question, payload['choices'])
        return JsonResponse({'questions': full_question_map}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except KeyError as e:
        return JsonResponse({'error': 'Must define %s' % str(e)}, safe=False, status=status.HTTP_400_BAD_REQUEST)


def add_choices(question_map, question, choices_list):
    choices = list(map(lambda choice: ChoiceSerializer(choice).data,
                       map(lambda choice_map: Choice.objects.create(
                           body=choice_map['body'],
                           times_chosen=choice_map[TIMES_CHOSEN] if TIMES_CHOSEN in choice_map else 0,
                           question=question
                       ), choices_list)))
    question_map['choices'] = choices
    return question_map


def add_question(question_map):
    question = Question.objects.create(
        body=question_map[BODY],
        times_answered=question_map[TIMES_ANSWERED] if TIMES_ANSWERED in question_map else 0,
        times_correct=question_map[TIMES_CORRECT] if TIMES_CORRECT in question_map else 0,
        tags=question_map[TAGS] if TAGS in question_map else list(),
        answer=question_map[ANSWER]
    )
    question_serialized = QuestionSerializer.serialize(question)
    return question_serialized, question


def delete_question(request, questionId):
    if not Question.objects.filter(id=questionId).exists():
        return JsonResponse({}, safe=False, status=status.HTTP_404_NOT_FOUND)

    question = Question.objects.get(pk=questionId)
    question_serialized = QuestionSerializer.serialize(question)
    question.delete()
    return JsonResponse(question_serialized, safe=False, status=status.HTTP_200_OK)


def put_question(request, questionId):
    try:
        question_fields_to_update = json.loads(request.body)
        question = Question.objects.get(pk=questionId)
        for field, value in question_fields_to_update.items():
            setattr(question, field, value)
        question.save()
        return JsonResponse(QuestionSerializer.serialize(question), safe=False, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'No question found with id [%d]' % questionId},
                            safe=False, status=status.HTTP_404_NOT_FOUND)


def units_controller(request):
    return JsonResponse({"units": ["Economics",
                                   "Income & Education",
                                   "Money & Credit Management",
                                   "Financial Planning",
                                   "Critical Consumerism"]
                         }, safe=False, status=status.HTTP_200_OK)

def results_controller(request):
    if request.method == 'GET':
        return get_all_results(request)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def level_results_controller(request, level):
    if request.method == 'GET':
        return get_results_by_level(request, level)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def get_paginated_results(results, num_items_per_page, page_number=1):
    paginator = Paginator(results, num_items_per_page)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page.object_list

def get_all_results(request):
    results = Result.objects.order_by('-distance').all()
    page_number = request.GET.get('page')
    results_serialized = list(map(lambda result: ResultSerializer.serialize(result), results))
    if page_number is not None: 
        results_serialized = get_paginated_results(results_serialized, PAGE_SIZE, page_number)
    return JsonResponse({'results': results_serialized}, safe=False, status=status.HTTP_200_OK)

def get_results_by_level(request, level):
    results = Result.objects.filter(level=level).order_by('-distance')
    page_number = request.GET.get('page')
    results_serialized = list(map(lambda result: ResultSerializer.serialize(result), results))
    if page_number is not None: 
        results_serialized = get_paginated_results(results_serialized, PAGE_SIZE, page_number)
    return JsonResponse({'results': results_serialized}, safe=False, status=status.HTTP_200_OK)
