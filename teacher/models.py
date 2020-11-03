from django.db import models
from django.contrib.postgres.fields import ArrayField


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, default="")


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=400, default="")
    accuracy = models.FloatField(default=100.0)


class Result(models.Model):
    id = models.AutoField(primary_key=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    distance = models.FloatField(default=0.0)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)

    def get_player_name(self):
        return self.player.name


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.CharField(max_length=500, default="")
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    tags = ArrayField(models.CharField(max_length=500), size=8, default=list)
    answer = ArrayField(models.IntegerField(), size=8, default=list)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True)
 
    def get_choices(self):
        return Choice.objects.filter(question=self.id)

 
class Choice(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.CharField(max_length=500, default="")
    times_chosen = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class Response(models.Model):
    class Meta:
        index_together = ["player", "question",
                          "choice"]

    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    choice = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    
    def get_is_correct(self):
        return len(Question.objects.filter(id=self.question.id, answer__contains=[self.choice])) > 0

