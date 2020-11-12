import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from teacher.models import Question, Choice, Level, ParlayUser
from teacher.serializer import QuestionSerializer, ChoiceSerializer
from teacher.views import TAG, TIMES_CHOSEN, BODY, TIMES_ANSWERED, TIMES_CORRECT, TAGS, ANSWER, LEVEL, \
    method_not_allowed, ok, not_found, must_define, not_authenticated


def question_not_found(question_id):
    return not_found('question', question_id)


@api_view(['GET', 'POST'])
def questions_controller(request):
    try:
        user = ParlayUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return not_authenticated()
    if request.method == 'GET':
        if TAG in request.GET:
            return get_questions_by_tag(request, request.GET.get(TAG), user)
        elif LEVEL in request.GET:
            return get_questions_by_level(request, request.GET.get(LEVEL), user)
        return get_all_questions(request, user)
    elif request.method == 'POST':
        return post_question(request)
    return method_not_allowed()


@api_view(['GET', 'PUT', 'DELETE'])
def question_controller(request, questionId):
    if request.method == 'GET':
        return get_single_question(request, questionId)
    elif request.method == 'PUT':
        return put_question(request, questionId)
    elif request.method == 'DELETE':
        return delete_question(request, questionId)
    return method_not_allowed()


def get_all_questions(request, user):
    questions = Question.objects.filter(assigned_class=user.get_assigned_class())
    questions_serialized = list(map(lambda question: QuestionSerializer.serialize(question), questions))
    return ok({'questions': questions_serialized})


def get_questions_by_tag(request, tag, user):
    questions = Question.objects.filter(tags__contains=[tag], assigned_class=user.get_assigned_class())
    questions_serialized = list(map(lambda question: QuestionSerializer.serialize(question), questions))
    return ok({'questions': questions_serialized})


def get_questions_by_level(request, level, user):
    questions = Question.objects.filter(level=level, assigned_class=user.get_assigned_class())
    questions_serialized = list(map(lambda question: QuestionSerializer.serialize(question), questions))
    return ok({'questions': questions_serialized})


def get_single_question(request, questionId):
    try:
        question = Question.objects.get(pk=questionId)
        return JsonResponse(QuestionSerializer.serialize(question), status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        return question_not_found(questionId)


def post_question(request):
    payload = json.loads(request.body)
    try:
        (question_map, question) = add_question(payload)
        full_question_map = add_choices(question_map, question, payload['choices'])
        return JsonResponse({'questions': full_question_map}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except KeyError as e:
        return must_define(str(e))


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
        answer=question_map[ANSWER],
        level=Level.objects.get(id=question_map[LEVEL]) if len(Level.objects.filter(id=question_map[LEVEL])) > 0
        else None
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
        for field, value in get_validated_update_items(question_fields_to_update):
            setattr(question, field, value)
        if 'choices' in question_fields_to_update:
            update_question_choices(question_fields_to_update['choices'])
        question.save()
        return JsonResponse(QuestionSerializer.serialize(question), safe=False, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return question_not_found(questionId)


def update_question_choices(updatedChoiceList):
    for updatedChoice in updatedChoiceList:
        try:
            choiceID = updatedChoice['id']
            choice = Choice.objects.get(id=choiceID)
            for field, value in updatedChoice.items():
                setattr(choice, field, value)
            choice.save()
        except KeyError:
            return JsonResponse({'error': 'Choices not specified with id'},
                                safe=False, status=status.HTTP_404_NOT_FOUND)


def get_validated_update_items(question_fields_to_update):
    if 'level' in question_fields_to_update:
        question_fields_to_update['level'] = Level.objects.get(id=question_fields_to_update['level'])
    return question_fields_to_update.items()
