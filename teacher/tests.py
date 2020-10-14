import json
import mock
from django.test import TestCase
from hamcrest import *
from teacher.models import Question, Result
from teacher.serializer import QuestionSerializer, ResultSerializer
from django.test import Client

class QuestionTestCase(TestCase):
    tag = 'tag'
    client: Client = None
    question: Question = None
    question_tagged: Question = None
    id = None

    def setUp(self):
        self.client: Client = Client()
        self.question = Question.objects.create(
            body='This is a question'
        )
        self.question_tagged = Question.objects.create(
            body='This is a question',
            tags=[self.tag]
        )

    def test_get_all_questions(self):
        assert_that(json.loads(self.client.get('/questions/').content)['questions'][0],
                    has_entries(QuestionSerializer.serialize(self.question)))

    def test_post_question(self):
        body = 'New question'
        self.client.post('/questions/', data={'body': body, 'answer': [1],
                                              'choices': [{
                                                  'body': 'correct answer'
                                              }]}, content_type='application/json')
        assert_that(Question.objects.get(body=body), instance_of(Question))

    def test_get_single_question(self):
        assert_that(json.loads(self.client.get('/questions/%d' % self.question.id).content),
                    has_entries(QuestionSerializer.serialize(self.question)))

    def test_put_question(self):
        body = 'Changed question'
        self.client.put('/questions/%d' % self.question.id,
                        data={'body': body, 'answer': [1],
                              'choices': [{
                                  'body': 'correct answer'
                              }]}, content_type='application/json')
        assert_that(Question.objects.get(pk=self.question.id).body, is_(body))

    def test_delete_question(self):
        self.client.delete('/questions/%d' % self.question.id)
        assert_that(not Question.objects.filter(pk=self.question.id).exists())

    def test_404_for_get_single_question(self):
        assert_that(self.client.get('/questions/%d' % 100).status_code,
                    is_(404))

    def test_404_for_put_question(self):
        assert_that(self.client.put('/questions/%d' % 60,
                                    data={'body': 'body', 'answer': [1],
                                          'choices': [{
                                              'body': 'correct answer'
                                          }]}, content_type='application/json').status_code,
                    is_(404))

    def test_404_for_delete_question(self):
        assert_that(self.client.delete('/questions/%d' % 60).status_code,
                    is_(404))

    def test_get_questions_by_tag(self):
        assert_that(json.loads(self.client.get('/questions/?tag=%s' % self.tag).content)['questions'][0],
                    has_entries(QuestionSerializer.serialize(self.question_tagged)))

    def test_get_questions_by_tag_doesnt_include_untagged(self):
        assert_that(json.loads(self.client.get('/questions/?tag=%s' % 'bad tag').content)['questions'],
                    has_length(0))

class ResultTestCase(TestCase):
    client: Client = None
    result1_level1: Result = None
    result2_level1: Result = None
    result1_level2: Result = None
    result2_level2: Result = None
    id = None

    def setUp(self):
        self.client: Client = Client()
        self.result1_level1 = Result.objects.create(
            level=1,
            distance=100.0,
            player_id=0
        )
        self.result2_level1 = Result.objects.create(
            level=1,
            distance=200.0,
            player_id=1
        )
        self.result1_level2 = Result.objects.create(
            level=2,
            distance=300.0,
            player_id=1
        )
        self.result2_level2 = Result.objects.create(
            level=2,
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
    
    @mock.patch("teacher.views.PAGE_SIZE", 2)
    def test_get_all_results_paginated(self):
        res = json.loads(self.client.get('/results/summary/?page=%d' % 1).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level2)))
        assert_that(res[1], has_entries(ResultSerializer.serialize(self.result2_level1)))
        assert_that(res, has_length(2)) 


    @mock.patch("teacher.views.PAGE_SIZE", 4)
    def test_paginated_results_same_as_non_paginated_for_all(self):
        res_paginated = json.loads(self.client.get('/results/summary/?page=%d' % 1).content)['results']
        res_non_paginated = json.loads(self.client.get('/results/summary/').content)['results']
        assert_that(res_paginated, equal_to(res_non_paginated))
    

    def test_get_results_by_level_non_paginated(self):
        res = json.loads(self.client.get('/levels/2/results/').content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level2)))
        assert_that(res[1], has_entries(ResultSerializer.serialize(self.result2_level2)))
        assert_that(res, has_length(2)) 

    @mock.patch("teacher.views.PAGE_SIZE", 1)
    def test_get_results_by_level_paginated(self):
        res = json.loads(self.client.get('/levels/2/results/?page=%d' % 1).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level2)))
        assert_that(res, has_length(1)) 

    @mock.patch("teacher.views.PAGE_SIZE", 2)
    def test_paginated_results_same_as_non_paginated_for_level(self):
        res_paginated = json.loads(self.client.get('/levels/2/results/?page=%d' % 1).content)['results']
        res_non_paginated = json.loads(self.client.get('/levels/2/results/').content)['results']
        assert_that(res_paginated, equal_to(res_non_paginated))

    # negative path test
    def test_get_result_by_level_when_doesnt_include_level(self):
        assert_that(json.loads(self.client.get('/levels/3/results/').content)['results'],
                    has_length(0))

    # negative path test
    def test_get_result_by_level_no_level(self):
        assert_that(self.client.get('/levels/results/').status_code, is_(404))

    # negative path test
    @mock.patch("teacher.views.PAGE_SIZE", 1)
    def test_paginated_page_not_number(self):
        res = json.loads(self.client.get('/results/summary/?page=%s' % 'test').content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level2)))
        assert_that(res, has_length(1)) 
        
    # negative path test
    @mock.patch("teacher.views.PAGE_SIZE", 1)
    def test_paginated_page_not_present(self):
        res = json.loads(self.client.get('/results/summary/?page=%d' % 20).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result1_level1)))
        assert_that(res, has_length(1)) 

    