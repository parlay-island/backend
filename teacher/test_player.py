import json
from unittest import TestCase

from django.test import Client
from hamcrest import *

from teacher.models import Player, Question, Level, Response, ParlayUser, Teacher
from teacher.views import ACCURACY, NAME
from teacher.serializer import PlayerSerializer


class PlayerTestCase(TestCase):
    teacher_username = 'teacher_username'
    password = '#IEic3ASj'
    header = None
    teacher_user = None
    teacher: Teacher = None
    player: Player = None
    player2: Player = None
    client: Client = None
    question: Question = None
    response: Response = None
    answer = 1

    def setUp(self):
        self.client: Client = Client()
        self.teacher_user = ParlayUser.objects.create_user(
            username=self.teacher_username,
            password=self.password,
            is_teacher=True
        )
        self.teacher = Teacher.objects.get(user=self.teacher_user)
        class_code = self.teacher.assigned_class.code
        self.level = Level.objects.create(name='Economics')
        self.question = Question.objects.create(
            body='This is a question',
            level=self.level,
            answer=[self.answer]
        )
        self.player = ParlayUser.objects.create_user(
            username='Player',
            password=self.password,
            is_teacher=False,
            class_code=class_code
        )
        self.player2 = ParlayUser.objects.create_user(
            username='Player2',
            password=self.password,
            is_teacher=False,
            class_code=class_code
        )
        token = json.loads(self.client.post('/auth/token/login', data={
            'username': self.teacher.user.username,
            'password': self.password
        }).content)['auth_token']
        self.header = {'Authorization': 'Token ' + token}

    def tearDown(self):
        self.teacher.delete()
        self.teacher_user.delete()
        self.player.delete()
        self.player2.delete()

    def test_get_all_players(self):
        player_fetched = json.loads(self.client.get('/players/', **self.header).content)['players']
        assert_that(player_fetched,
                    has_item(PlayerSerializer.serialize(self.player)))
        assert_that(player_fetched,
                    has_item(PlayerSerializer.serialize(self.player2)))            
        assert_that(player_fetched[0][ACCURACY], is_(100.0))
        assert_that(player_fetched[0][NAME], is_('Player'))

    def test_get_single_player(self):
        assert_that(json.loads(self.client.get('/players/%d/' % Player.objects.get(user=self.player).id).content),
                    has_entries(PlayerSerializer.serialize(Player.objects.get(user=self.player))))

    def test_non_implemented_method(self):
        assert_that(self.client.put('/players/').status_code, is_(405))

    def test_404_for_single_player(self):
        assert_that(self.client.get('/players/%d/' % 100).status_code, is_(404))
