from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.postgres.fields import ArrayField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self, username, email=None, password=None, **extra_fields
    ):
        if not username:
            raise ValueError("The given custom_username must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(custom_username=username, custom_email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=150)
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

