import io
import json
import mock
from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict, HttpRequest
from django.test import TestCase
from hamcrest import *
from teacher.models import Result, Level, Player, Question, Response, ParlayUser, Class, Teacher, Choice
from teacher.serializer import ResultSerializer
from teacher.views import DISTANCE, LEVEL, level_views
from django.test import Client


class ResultTestCase(TestCase):
    mock_request = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'wsgi.input': io.StringIO(),
        })
    code = "code234123"
    username = "username"
    teacher_username = "teacher-username"
    password = "J#5eI9qwpp"
    player = None
    client: Client = None
    level1: Level = None
    level2: Level = None
    question: Question = None
    result1_level1: Result = None
    result2_level1: Result = None
    result1_level2: Result = None
    result2_level2: Result = None
    id = None
    choice = None

    def setUp(self):
        self.client = Client()
        self.teacher_user = ParlayUser.objects.create_user(
            username=self.teacher_username,
            password=self.password,
            is_teacher=True
        )
        self.assigned_class = Teacher.objects.get(user=self.teacher_user).assigned_class
        self.code = self.assigned_class.code
        self.player_user = ParlayUser.objects.create_user(
            username=self.username,
            password=self.password,
            is_teacher=False,
            class_code=self.code
        )
        self.player = Player.objects.get(user=self.player_user)
        self.level1 = Level.objects.create(
            name="Level 1"
        )
        self.level2 = Level.objects.create(
            name="Level 2"
        )
        self.question = Question.objects.create(
            body='This is a question',
            level=self.level1,
            answer=[0]
        )
        self.choice = Choice.objects.create(body='Choice 1', question=self.question)

        self.question2 = Question.objects.create(
            body='This is a question2',
            level=self.level1,
            answer=[1]
        )
        self.result1_level1 = Result.objects.create(
            level=self.level1,
            distance=100.0,
            player=self.player,
            assigned_class=self.assigned_class
        )
        self.result2_level1 = Result.objects.create(
            level=self.level1,
            distance=200.0,
            player=self.player,
            assigned_class=self.assigned_class
        )
        self.result1_level2 = Result.objects.create(
            level=self.level2,
            distance=300.0,
            player=self.player,
            assigned_class=self.assigned_class
        )
        self.result2_level2 = Result.objects.create(
            level=self.level2,
            distance=150.0,
            player=self.player,
            assigned_class=self.assigned_class
        )

    def tearDown(self):
        self.player_user.delete()

    def result_post_request(self, choice, distance, player, question_id):
        assert_that(self.client.post('/players/%d/results/' % player.id,
                    data={'distance': distance,
                          'level': self.level1.id,
                          'questions': [
                                   {
                                       'question_id': question_id,
                                       'choice_id': choice
                                   }
                               ]},
                         content_type='application/json').status_code, is_(201))

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
        res = json.loads(level_views.get_results_by_level(self.mock_request, self.level1.id,
                                                          self.teacher_user).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result2_level1)))
        assert_that(res[1], has_entries(ResultSerializer.serialize(self.result1_level1)))
        assert_that(res, has_length(2))

    @mock.patch("teacher.views.level_views.PAGE_SIZE", 1)
    def test_get_results_by_level_paginated(self):
        mock_request_with_page = HttpRequest()
        mock_request_with_page.GET.__setitem__('page', 1)
        res = json.loads(level_views.get_results_by_level(mock_request_with_page, self.level1.id,
                                                          self.teacher_user).content)['results']
        assert_that(res[0], has_entries(ResultSerializer.serialize(self.result2_level1)))
        assert_that(res, has_length(1))

    @mock.patch("teacher.views.level_views.PAGE_SIZE", 2)
    def test_paginated_results_same_as_non_paginated_for_level(self):
        mock_request_with_page = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'wsgi.input': io.StringIO(),
            'page': 1
        })
        res_paginated = json.loads(level_views.get_results_by_level(mock_request_with_page, self.level1.id,
                                                                    self.teacher_user).content)['results']
        res_non_paginated = json.loads(level_views.get_results_by_level(self.mock_request, self.level1.id,
                                                                        self.teacher_user).content)['results']
        assert_that(res_paginated, equal_to(res_non_paginated))

    # negative path test
    def test_get_result_by_level_when_doesnt_include_level(self):
        assert_that(json.loads(level_views.get_results_by_level(self.mock_request, 17,
                                                                self.teacher_user).content)['results'],
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
    
    def test_post_result_without_question_specific_data(self):
        player = Player.objects.create(name="Player2")
        distance = 500.0
        self.client.post('/players/%d/results/' % player.id,
                         data={'distance': distance, 'level': self.level1.id},
                         content_type='application/json')
        result_posted = Result.objects.get(player=player.id)
        result_serialized = ResultSerializer.serialize(result_posted)
        assert_that(result_posted, instance_of(Result))
        assert_that(result_serialized[DISTANCE], is_(distance))
        assert_that(result_serialized[LEVEL], is_(self.level1.id))

    def test_post_result_with_question_specific_data(self):
        player = Player.objects.create(name="Player2")
        distance = 500.0
        choice = 1
        self.result_post_request(choice, distance, player, self.question.id)
        responses = Response.objects.filter(question=self.question)
        assert_that(responses, has_length(1))
        assert_that(responses[0].choice, is_(choice))
        assert_that(responses[0].count, is_(1))

    def test_times_chosen_updates_on_result_post(self):
        player = Player.objects.create(name="Player4")
        initial_times_answered = self.question.times_answered
        initial_times_correct = self.question.times_correct
        choice = 0 # correct choice
        distance = 500.0
        self.result_post_request(choice, distance, player, self.question.id)
        question = Question.objects.get(id=self.question.id)
        # test that times_answered is updated
        updated_times_answered = question.times_answered
        assert_that(initial_times_answered, is_(0))
        assert_that(updated_times_answered, is_(1))
        # test that times_correct is updated
        updated_times_correct = question.times_correct
        assert_that(initial_times_correct, is_(0))
        assert_that(updated_times_correct, is_(1))
        # test that choice times_chosen is updated
        choice = Choice.objects.get(question=self.question.id)
        assert_that(choice.times_chosen, is_(1))
    
    def test_accuracy_updates_on_result_post(self):
        player = Player.objects.create(name="Player3")
        initial_accuracy = player.accuracy
        distance = 500.0
        choice = 1
        self.result_post_request(choice, distance, player, self.question.id)
        updated_accuracy = Player.objects.get(id=player.id).accuracy
        assert_that(initial_accuracy, is_(100))
        assert_that(updated_accuracy, is_(0))
        self.result_post_request(choice, distance, player, self.question2.id)
        updated_accuracy = Player.objects.get(id=player.id).accuracy
        assert_that(updated_accuracy, is_(50))
        self.result_post_request(0, distance, player, self.question.id)
        updated_accuracy = Player.objects.get(id=player.id).accuracy
        assert_that(updated_accuracy, is_((2/3) * 100))

    def test_404_for_post_result(self):
        assert_that(self.client.post('/players/%d/results/' % self.player.id,
                                     data={'distance': 300, 'level': 7},
                                     content_type='application/json').status_code, is_(404))

    def test_404_for_post_result_when_player_not_present(self):
        assert_that(self.client.post('/players/%d/results/' % 315,
                                     data={'distance': 300, 'level': self.level1.id},
                                     content_type='application/json').status_code, is_(404))

    def test_get_results_by_level(self):
        Response.objects.create(question=self.question, choice=0, player=self.player)
        res = json.loads(self.client.get('/players/%d/results/?level=%d' % (self.player.id, self.level1.id))
                         .content)['results']
        assert_that(res[0]['question'], is_(self.question.id))

    def test_get_results_by_level_with_wrong_level(self):
        Response.objects.create(question=self.question, choice=0, player=self.player)
        res = json.loads(self.client.get('/players/%d/results/?level=%d' % (self.player.id, 3))
                         .content)['results']
        assert_that(res, has_length(0))

    def test_404_for_player_not_present_on_get_results_by_level(self):
        assert_that(self.client.get('/players/%d/results/?level=%d' % (958, 3)).status_code, is_(404))
