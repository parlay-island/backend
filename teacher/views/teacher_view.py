"""
teacher_view.py

Contains views that interact with teacher.models.Teacher.
"""

from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from teacher.models import Teacher
from teacher.serializer import TeacherSerializer
from teacher.views import method_not_allowed, not_authenticated, ok, GET, ERROR


@api_view()
def me_controller(request):
    if request.method == GET:
        return serialize_me(request)
    return method_not_allowed()


def serialize_me(request):
    user = request.user
    if not user.is_authenticated:
        return not_authenticated()
    try:
        teacher = Teacher.objects.get(user=user)
        return ok(TeacherSerializer.serialize(teacher))
    except ObjectDoesNotExist as e:
        return JsonResponse({ERROR: 'You do not have an associated teacher account'},
                            status=status.HTTP_401_UNAUTHORIZED)
