from rest_framework import serializers

from teacher.models import Question, Choice


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'body', 'times_answered', 'times_correct', 'tags', 'answer']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'body', 'times_chosen', 'question']
