from django.db import models
from django.contrib.postgres.fields import ArrayField


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, default="")


class Result(models.Model):
    id = models.AutoField(primary_key=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    distance = models.FloatField(default=0.0)
    # this will later be foreign key to player table
    player_id = models.IntegerField(default=0)

    # later have this access the name from the Player Object
    def get_player_name(self):
        return str(self.player_id)


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
