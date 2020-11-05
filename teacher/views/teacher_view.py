from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Teacher
from teacher.serializer import TeacherSerializer


def me_controller(request):
    if request.method == 'GET':
        return serialize_me(request)
    return JsonResponse({'error', 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def serialize_me(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'You are not logged in'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        teacher = Teacher.objects.get(user=user)
        return JsonResponse(TeacherSerializer.serialize(teacher), status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': 'You do not have an associated player account'},
                            status=status.HTTP_401_UNAUTHORIZED)
