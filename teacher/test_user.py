from django.test import TestCase

from hamcrest import assert_that, has_length

from teacher.models import ParlayUser, Player, Teacher


class UserTestCase(TestCase):

    def test_create_player_when_is_teacher_false(self):
        ParlayUser.objects.create_user(username="username", password="2j5l$j2k4", is_teacher=False)
        assert_that(Player.objects.all(), has_length(1))

    def test_create_teacher_when_is_teacher_true(self):
        ParlayUser.objects.create_user(username="username", password="2j5l$j2k4", is_teacher=True)
        assert_that(Teacher.objects.all(), has_length(1))
