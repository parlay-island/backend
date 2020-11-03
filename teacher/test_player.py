import json
from unittest import TestCase

from django.test import Client
from hamcrest import *

from teacher.models import Player, Question, Level, Response
from teacher.views import ACCURACY, NAME
from teacher.serializer import PlayerSerializer


class PlayerTestCase(TestCase):
    player: Player = None
    client: Client = None
    question: Question = None
    response: Response = None
    answer = 1

    def setUp(self):
        self.client: Client = Client()
        self.level = Level.objects.create(name='Economics')
        self.question = Question.objects.create(
            body='This is a question',
            level=self.level,
            answer=[self.answer]
        )
        self.player = Player.objects.create(
            name='Player'
        )

    def test_posting_a_player(self):
        name = 'Name'
        self.client.post('/players/', data={'name': name},
                         content_type='application/json')
        assert_that(Player.objects.get(name__exact=name).name, is_(name))

    def test_get_all_players(self):
        player_fetched = json.loads(self.client.get('/players/').content)['players'][0]
        assert_that(player_fetched,
                    has_entries(PlayerSerializer.serialize(self.player)))
        assert_that(player_fetched[ACCURACY], is_(100.0))
        assert_that(player_fetched[NAME], is_('Player'))

    def test_non_implemented_method(self):
        assert_that(self.client.put('/players/').status_code, is_(405))