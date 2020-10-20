import json
from django.test import TestCase
from hamcrest import *
from teacher.models import Question, Level
from teacher.serializer import QuestionSerializer, LevelSerializer
from django.test import Client


class LevelTestCase(TestCase):
    client: Client = None
    level1: Level = None

    def setUp(self):
        self.client = Client()
        self.level1 = Level.objects.create(name="Level 1")

    def test_get_all_levels(self):
        res = json.loads(self.client.get('/levels/').content)['levels']
        assert_that(res[0], has_entries(LevelSerializer.serialize(self.level1)))
