# Generated by Django 3.1.2 on 2020-10-14 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0005_choice'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('level', models.IntegerField(default=0)),
                ('distance', models.FloatField(default=0.0)),
                ('player_id', models.IntegerField(default=0)),
            ],
        ),
    ]
