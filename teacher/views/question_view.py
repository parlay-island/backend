import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from teacher.models import Question, Choice, Level, ParlayUser
from teacher.serializer import QuestionSerializer, ChoiceSerializer
from teacher.views import TAG, TIMES_CHOSEN, BODY, TIMES_ANSWERED, TIMES_CORRECT, TAGS, ANSWER, LEVEL, \
    method_not_allowed, ok, not_found, must_define, not_authenticated
from teacher.views.view_responses import created, requires_parlay_user


def question_not_found(question_id):
    return not_found('question', question_id)


def requires_question_exists(func):
    def wrapper(*args, **kwargs):
        questionId = kwargs['questionId']
        user = kwargs['user']
        if not Question.objects.filter(id=questionId).exists() \
                or Question.objects.get(id=questionId).assigned_class != user.get_assigned_class():
            return question_not_found(questionId)
        return func(*args, **kwargs)
    return wrapper


@api_view(['GET', 'POST'])
@requires_parlay_user
def questions_controller(request, user):
    if request.method == 'GET':
        if TAG in request.GET:
            return get_questions_by_tag(request, request.GET.get(TAG), user)
        elif LEVEL in request.GET:
            return get_questions_by_level(request, request.GET.get(LEVEL), user)
        return get_all_questions(request, user)
    elif request.method == 'POST':
        return post_question(request, user)
    return method_not_allowed()


@api_view(['GET', 'PUT', 'DELETE'])
@requires_parlay_user
@requires_question_exists
def question_controller(request, questionId, user):
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
    question = Question.objects.get(pk=questionId)
    return ok(QuestionSerializer.serialize(question))


def post_question(request, user):
    payload = json.loads(request.body)
    try:
        (question_map, question) = add_question(payload, user)
        full_question_map = add_choices(question_map, question, payload['choices'])
        return created({'questions': full_question_map})
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


def add_question(question_map, user):
    question = Question.objects.create(
        body=question_map[BODY],
        times_answered=question_map[TIMES_ANSWERED] if TIMES_ANSWERED in question_map else 0,
        times_correct=question_map[TIMES_CORRECT] if TIMES_CORRECT in question_map else 0,
        tags=question_map[TAGS] if TAGS in question_map else list(),
        answer=question_map[ANSWER],
        level=Level.objects.get(id=question_map[LEVEL]) if len(Level.objects.filter(id=question_map[LEVEL])) > 0
                                                        else None,
        assigned_class=user.get_assigned_class()
    )
    question_serialized = QuestionSerializer.serialize(question)
    return question_serialized, question


def delete_question(request, questionId):
    question = Question.objects.get(pk=questionId)
    question_serialized = QuestionSerializer.serialize(question)
    question.delete()
    return ok(question_serialized)


def put_question(request, questionId):
    question_fields_to_update = json.loads(request.body)
    question = Question.objects.get(pk=questionId)
    for field, value in get_validated_update_items(question_fields_to_update):
        setattr(question, field, value)
    if 'choices' in question_fields_to_update:
        update_question_choices(question_fields_to_update['choices'])
    question.save()
    return ok(QuestionSerializer.serialize(question))


def update_question_choices(updatedChoiceList):
    for updatedChoice in updatedChoiceList:
        try:
            choiceID = updatedChoice['id']
            choice = Choice.objects.get(id=choiceID)
            for field, value in updatedChoice.items():
                setattr(choice, field, value)
            choice.save()
        except KeyError:
            return must_define('id in choices')


def get_validated_update_items(question_fields_to_update):
    if 'level' in question_fields_to_update:
        question_fields_to_update['level'] = Level.objects.get(id=question_fields_to_update['level'])
    return question_fields_to_update.items()
