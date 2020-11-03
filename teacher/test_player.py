from unittest import TestCase

from django.test import Client

from teacher.models import Player, Question, Level, Response


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
