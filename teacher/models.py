import random
import string

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.postgres.fields import ArrayField


class ParlayUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self, username, email=None, password=None, **extra_fields
    ):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, is_teacher=extra_fields.get("is_teacher"))
        user.set_password(password)
        user.save(using=self._db)
        if user.is_teacher:
            class_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(10))
            teacher_class = Class.objects.create(name=user.username, code=class_code)
            teacher = Teacher.objects.create(user=user, name=user.username, assigned_class=teacher_class)
        else:
            if not extra_fields.get("class_code"):
                raise ValueError("The class code was not set on creation of a player")
            try:
                assigned_class = Class.objects.get(code=extra_fields.get("class_code"))
            except ObjectDoesNotExist:
                raise ValueError("The class code used does not have an associated class")
            player = Player.objects.create(user=user, name=user.username,
                                           assigned_class=assigned_class)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class Class(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, default="")
    code = models.CharField(max_length=10)


class ParlayUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    is_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class_code = models.CharField(max_length=500, default="")

    objects = ParlayUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "is_teacher", "class_code"]


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, default="")


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(ParlayUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=400, default="")
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(ParlayUser, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=400, default="")
    accuracy = models.FloatField(default=100.0)
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)


class Result(models.Model):
    id = models.AutoField(primary_key=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    distance = models.FloatField(default=0.0)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)

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
        return Choice.objects.filter(question=self.id).order_by('id')

 
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
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    
    def get_is_correct(self):
        return len(Question.objects.filter(id=self.question.id, answer__contains=[self.choice])) > 0

