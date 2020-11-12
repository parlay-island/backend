"""
serializer.py

Contains serializers for all models which turn a map into an object.
"""
from rest_framework import serializers

from teacher.models import Question, Choice, Result, Level, Response, Player, Teacher


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'body', 'times_answered', 'times_correct', 'tags', 'answer', 'level']

    @staticmethod
    def serialize(question):
        question_map = QuestionSerializer(question).data
        choices = list(map(lambda choice: ChoiceSerializer.serialize(choice), question.get_choices()))
        question_map['choices'] = choices
        question_map['level'] = question.level.id if question.level is not None else None
        return question_map


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'body', 'times_chosen', 'question']

    @staticmethod
    def serialize(choice):
        return ChoiceSerializer(choice).data


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'level', 'distance', 'player_id', 'award_list']

    @staticmethod
    def serialize(result):
        result_map = ResultSerializer(result).data
        level_id = LevelSerializer.serialize(result.level)['id']
        result_map['player_name'] = result.get_player_name()
        result_map['level'] = level_id
        return result_map


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name']

    @staticmethod
    def serialize(level):
        return LevelSerializer(level).data


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['question', 'player', 'choice', 'count']

    @staticmethod
    def serialize(response):
        response_map = ResponseSerializer(response).data
        response_map['is_correct'] = response.get_is_correct()
        return response_map


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'accuracy']

    @staticmethod
    def serialize(player):
        return PlayerSerializer(player).data


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name']

    @staticmethod
    def serialize(teacher):
        teacher_serialized = TeacherSerializer(teacher).data
        teacher_serialized['class_code'] = teacher.assigned_class.code
        return teacher_serialized
