import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Question
from teacher.serializer import QuestionSerializer


def questions_controller(request):
    if request.method == 'GET':
        return get_all_questions(request)
    elif request.method == 'POST':
        return post_question(request)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def question_controller(request, questionId):
    if request.method == 'GET':
        return Question.objects.get(pk=questionId)
    elif request.method == 'DELETE':
        return delete_question(request, questionId)


def get_all_questions(request):
    books = Question.objects.all()
    serializer = QuestionSerializer(books, many=True)
    return JsonResponse({'questions': serializer.data}, safe=False, status=status.HTTP_200_OK)


def post_question(request):
    payload = json.loads(request.body)
    try:
        question = Question.objects.create(
            body=payload['body'],
            times_answered=payload['times_answered'],
            times_correct=payload['times_correct'],
            tags=payload['tags'],
            answer=payload['answer']
        )
        serializer = QuestionSerializer(question)
        return JsonResponse({'questions': serializer.data}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)


def delete_question(request, questionId):
    if not Question.objects.filter(id=questionId).exists():
        return JsonResponse({}, safe=False, status=status.HTTP_404_NOT_FOUND)

    question = Question.objects.get(pk=questionId)
    serializer = QuestionSerializer(question)
    question.delete()
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)