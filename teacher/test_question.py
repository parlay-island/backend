import json
from django.test import TestCase
from hamcrest import *
from teacher.models import Question, Level, Choice
from teacher.serializer import QuestionSerializer
from django.test import Client


class QuestionTestCase(TestCase):
    tag = 'tag'
    client: Client = None
    question: Question = None
    question_tagged: Question = None
    id = None
    level = None
    choice: Choice = None

    def setUp(self):
        self.client: Client = Client()
        self.level = Level.objects.create(name='Economics')
        self.question = Question.objects.create(
            body='This is a question',
            level=self.level
        )
        self.question_tagged = Question.objects.create(
            body='This is a question',
            tags=[self.tag],
            level=self.level
        )
        self.choice = Choice.objects.create(body='Choice 1', question=self.question)


    def test_get_all_questions(self):
        assert_that(json.loads(self.client.get('/questions/').content)['questions'][0],
                    has_entries(QuestionSerializer.serialize(self.question)))

    def test_post_question(self):
        body = 'New question'
        self.client.post('/questions/', data={'body': body, 'answer': [1], 'level': self.level.id,
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
                        data={'body': body, 'answer': [1], 'level': self.level.id,
                              'choices': [{
                                  'id': self.choice.id,
                                  'body': 'choice'
                              }]}, content_type='application/json')
        assert_that(Question.objects.get(pk=self.question.id).body, is_(body))

    def test_put_questions_with_choices(self):
        updatedChoice = 'correct answer'
        timesChosen = 1
        self.client.put('/questions/%d' % self.question.id,
                        data={'body': 'body', 'answer': [0], 'level': self.level.id,
                              'choices': [
                                {
                                  'id': self.choice.id,
                                  'body': updatedChoice,
                                  'times_chosen': timesChosen
                                },
                              ]}, content_type='application/json')
        question = Question.objects.get(pk=self.question.id)
        for choice in question.get_choices():
            assert_that(choice.body, is_(updatedChoice))
            assert_that(choice.times_chosen, is_(timesChosen))

    def test_delete_question(self):
        self.client.delete('/questions/%d' % self.question.id)
        assert_that(not Question.objects.filter(pk=self.question.id).exists())

    def test_404_for_get_single_question(self):
        assert_that(self.client.get('/questions/%d' % 100).status_code,
                    is_(404))

    def test_404_for_put_question(self):
        assert_that(self.client.put('/questions/%d' % 60,
                                    data={'body': 'body', 'answer': [1], 'level': self.level.id,
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

    def test_get_questions_by_level(self):
        assert_that(json.loads(self.client.get('/questions/?level=%s' % self.level.id).content)['questions'][0],
                    has_entries(QuestionSerializer.serialize(self.question)))