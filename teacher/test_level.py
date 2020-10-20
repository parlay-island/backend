import json
from django.test import TestCase
from hamcrest import *
from teacher.models import Level
from teacher.serializer import LevelSerializer
from django.test import Client


class LevelTestCase(TestCase):
    client: Client = None
    level1: Level = None

    def setUp(self):
        self.client = Client()
        self.level1 = Level.objects.create(name='Level 1')

    def test_get_all_levels(self):
        res = json.loads(self.client.get('/levels/').content)['levels']
        assert_that(res[0], has_entries(LevelSerializer.serialize(self.level1)))

    def test_post_new_level(self):
        self.client.post('/levels/', data={'name': 'Level 2'}, content_type='application/json')
        assert_that(Level.objects.filter(name='Level 2'), has_length(1))

    def test_delete_level(self):
        level_id = self.level1.id
        self.client.delete('/levels/%d/' % level_id)
        assert_that(Level.objects.filter(id=level_id), has_length(0))
