from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self, username, email=None, password=None, **extra_fields
    ):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if user.is_teacher:
            teacher = Teacher.objects.create(user=user)
        else:
            player = Player.objects.create(user=user, name=user.username)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    is_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "is_teacher"]


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, default="")


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
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

