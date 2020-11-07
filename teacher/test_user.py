from django.test import TestCase, Client

from hamcrest import assert_that, has_length, is_

from teacher.models import ParlayUser, Player, Teacher


class UserTestCase(TestCase):
    teacher_class = None
    client = None
    teacher_user = None
    player_user = None
    teacher_username = "teacher_username"
    player_username = "player_username"
    username_2 = "username2"
    password = "2343j;$jfE"

    def setUp(self):
        self.client = Client()
        self.teacher_user = ParlayUser.objects.create_user(username=self.teacher_username, password=self.password,
                                                           is_teacher=True)
        self.teacher_class = Teacher.objects.get(user=self.teacher_user).assigned_class
        self.player_user = ParlayUser.objects.create_user(username=self.player_username, password=self.password,
                                                          is_teacher=False, class_code=self.teacher_class.code)

    def test_create_player_when_is_teacher_false(self):
        ParlayUser.objects.create_user(username=self.username_2, password=self.password,
                                       is_teacher=False, class_code=self.teacher_class.code)
        assert_that(Player.objects.all(), has_length(2))

    def test_create_teacher_when_is_teacher_true(self):
        ParlayUser.objects.create_user(username=self.username_2, password=self.password, is_teacher=True)
        assert_that(Teacher.objects.all(), has_length(2))

    def test_player_me(self):
        self.client.post('/auth/token/login/', {'username': self.player_username,
                                                'password': self.password})
        assert_that(self.client.get('/players/me/').status_code, is_(200))

    def test_teacher_me(self):
        self.client.post('/auth/token/login/', {'username': self.teacher_username,
                                                'password': self.password})
        assert_that(self.client.get('/teachers/me/').status_code, is_(200))

    def test_player_me_without_player_type_account(self):
        self.client.post('/auth/token/login/', {'username': self.teacher_username,
                                                'password': self.password})
        assert_that(self.client.get('/players/me/').status_code, is_(401))

    def test_teacher_me_without_teacher_type_account(self):
        self.client.post('/auth/token/login/', {'username': self.player_username,
                                                'password': self.password})
        assert_that(self.client.get('/teachers/me/').status_code, is_(401))

    def test_player_me_unauthenticated(self):
        assert_that(self.client.get('/players/me/').status_code, is_(401))

    def test_teacher_me_unauthenticated(self):
        assert_that(self.client.get('/teachers/me/').status_code, is_(401))
