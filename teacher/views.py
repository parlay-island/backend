import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Question, Choice
from teacher.serializer import QuestionSerializer, ChoiceSerializer


def questions_controller(request):
    if request.method == 'GET':
        return get_all_questions(request)
    elif request.method == 'POST':
        return post_question(request)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def question_controller(request, questionId):
    if request.method == 'GET':
        return Question.objects.get(pk=questionId)
    elif request.method == 'PUT':
        return put_question(request, questionId)
    elif request.method == 'DELETE':
        return delete_question(request, questionId)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_all_questions(request):
    books = Question.objects.all()
    serializer = QuestionSerializer(books, many=True)
    return JsonResponse({'questions': serializer.data}, safe=False, status=status.HTTP_200_OK)


def post_question(request):
    payload = json.loads(request.body)
    try:
        (question_map, question) = add_question(payload)
        full_question_map = add_choices(question_map, question, payload['choices'])
        return JsonResponse({'questions': full_question_map}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)


def add_choices(question_map, question, choices_list):
    choices = list(map(lambda choice: ChoiceSerializer(choice).data,
                       map(lambda choice_map: Choice.objects.create(
                           body=choice_map['body'],
                           times_chosen=choice_map['times_chosen'],
                           question=question
                       ), choices_list)))
    question_map['choices'] = choices
    return question_map


def add_question(question_map):
    question = Question.objects.create(
        body=question_map['body'],
        times_answered=question_map['times_answered'],
        times_correct=question_map['times_correct'],
        tags=question_map['tags'],
        answer=question_map['answer']
    )
    serializer = QuestionSerializer(question)
    return serializer.data, question


def delete_question(request, questionId):
    if not Question.objects.filter(id=questionId).exists():
        return JsonResponse({}, safe=False, status=status.HTTP_404_NOT_FOUND)

    question = Question.objects.get(pk=questionId)
    question_serialized = QuestionSerializer.serialize(question)
    question.delete()
    return JsonResponse(question_serialized, safe=False, status=status.HTTP_200_OK)


def put_question(request, questionId):
    question_fields_to_update = json.loads(request.body)
    question = Question.objects.get(pk=questionId)
    for field, value in question_fields_to_update.items():
        setattr(question, field, value)
    return JsonResponse(QuestionSerializer.serialize(question), safe=False, status=status.HTTP_200_OK)
