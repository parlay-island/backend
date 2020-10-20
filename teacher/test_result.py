import json
import mock
from django.test import TestCase
from hamcrest import *
from teacher.models import Result, Level
from teacher.serializer import ResultSerializer
from django.test import Client


class ResultTestCase(TestCase):
    client: Client = None
    level1: Level = None
    level2: Level = None
    result1_level1: Result = None
    result2_level1: Result = None
    result1_level2: Result = None
    result2_level2: Result = None
    id = None

    def setUp(self):
        self.client: Client = Client()
        self.level1 = Level.objects.create(
            name="Level 1"
        )
        self.level2 = Level.objects.create(
            name="Level 2"
        )
        self.result1_level1 = Result.objects.create(
            level=self.level1,
            distance=100.0,
            player_id=0
        )
        self.result2_level1 = Result.objects.create(
            level=self.level1,
            distance=200.0,
            player_id=1
        )
        self.result1_level2 = Result.objects.create(
            level=self.level2,
            distance=300.0,
            player_id=1
        )
        self.result2_level2 = Result.objects.create(
            level=self.level2,
            distance=150.0,
            player_id=0
        )

    def test_get_all_results_non_paginated(self):
        res = json.loads(self.client.get('/results/summary/').content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level2)))
        assert_that(res[1], has_entries(ResultSerializer.serialize(self.result2_level1)))
        assert_that(res[2], has_entries(ResultSerializer.serialize(self.result2_level2)))
        assert_that(res[3], has_entries(ResultSerializer.serialize(self.result1_level1)))
        assert_that(res, has_length(4))

    @mock.patch("teacher.views.result_view.PAGE_SIZE", 2)
    def test_get_all_results_paginated(self):
        res = json.loads(self.client.get('/results/summary/?page=%d' % 1).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level2)))
        assert_that(res[1], has_entries(ResultSerializer.serialize(self.result2_level1)))
        assert_that(res, has_length(2))

    @mock.patch("teacher.views.result_view.PAGE_SIZE", 4)
    def test_paginated_results_same_as_non_paginated_for_all(self):
        res_paginated = json.loads(self.client.get('/results/summary/?page=%d' % 1).content)['results']
        res_non_paginated = json.loads(self.client.get('/results/summary/').content)['results']
        assert_that(res_paginated, equal_to(res_non_paginated))

    def test_get_results_by_level_non_paginated(self):
        res = json.loads(self.client.get('/levels/%d/results/' % self.level1.id).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result2_level1)))
        assert_that(res[1], has_entries(ResultSerializer.serialize(self.result1_level1)))
        assert_that(res, has_length(2))

    @mock.patch("teacher.views.level_views.PAGE_SIZE", 1)
    def test_get_results_by_level_paginated(self):
        res = json.loads(self.client.get('/levels/%d/results/?page=%d' % (self.level1.id, 1)).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result2_level1)))
        assert_that(res, has_length(1))

    @mock.patch("teacher.views.level_views.PAGE_SIZE", 2)
    def test_paginated_results_same_as_non_paginated_for_level(self):
        res_paginated = json.loads(self.client.get('/levels/%d/results/?page=%d' %
                                                   (self.level1.id, 1)).content)['results']
        res_non_paginated = json.loads(self.client.get('/levels/%d/results/' % self.level1.id).content)['results']
        assert_that(res_paginated, equal_to(res_non_paginated))

    # negative path test
    def test_get_result_by_level_when_doesnt_include_level(self):
        assert_that(json.loads(self.client.get('/levels/3/results/').content)['results'],
                    has_length(0))

    # negative path test
    def test_get_result_by_level_no_level(self):
        assert_that(self.client.get('/levels/results/').status_code, is_(404))

    # negative path test
    @mock.patch("teacher.views.result_view.PAGE_SIZE", 1)
    def test_paginated_page_not_number(self):
        res = json.loads(self.client.get('/results/summary/?page=%s' % 'test').content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level2)))
        assert_that(res, has_length(1))

        # negative path test

    @mock.patch("teacher.views.result_view.PAGE_SIZE", 1)
    def test_paginated_page_not_present(self):
        res = json.loads(self.client.get('/results/summary/?page=%d' % 20).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level1)))
        assert_that(res, has_length(1))
