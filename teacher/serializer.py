from rest_framework import serializers

from teacher.models import Question, Choice


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'body', 'times_answered', 'times_correct', 'tags', 'answer']

    @staticmethod
    def serialize(question):
        question_map = QuestionSerializer(question).data
        choices = list(map(lambda choice: ChoiceSerializer.serialize(choice), question.get_choices()))
        question_map['choices'] = choices
        return question_map


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'body', 'times_chosen', 'question']

    @staticmethod
    def serialize(choice):
        return ChoiceSerializer(choice).data
