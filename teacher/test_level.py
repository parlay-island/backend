import json

from django.test import TestCase, RequestFactory
from hamcrest import *
from teacher.models import Level, ParlayUser, Class
from teacher.serializer import LevelSerializer
from django.test import Client

from teacher.views import levels_controller


class LevelTestCase(TestCase):
    code = '123456789'
    client: Client = None
    level1: Level = None
    request_factory: RequestFactory = RequestFactory()

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.assigned_class = Class.objects.create(name='class', code=self.code)
        self.level1 = Level.objects.create(name='Level 1', assigned_class=self.assigned_class)
        self.user = ParlayUser.objects.create_user(
            username='Player',
            password='#WordOfPass1',
            is_teacher=False,
            class_code=self.code
        )
        self.client.force_login(self.user)

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

    def test_get_specific_level(self):
        res = json.loads(self.client.get('/levels/%d/' % self.level1.id).content)
        assert_that(res, has_entries(LevelSerializer.serialize(self.level1)))

    def test_delete_level_not_found(self):
        assert_that(self.client.delete('/levels/15/').status_code, is_(404))

    def test_get_level_not_found(self):
        assert_that(self.client.delete('/levels/15/').status_code, is_(404))

    def test_level_method_not_supported(self):
        assert_that(self.client.patch('/levels/15/').status_code, is_(405))

    def test_levels_method_not_supported(self):
        assert_that(self.client.patch('/levels/').status_code, is_(405))
