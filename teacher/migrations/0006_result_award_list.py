# Generated by Django 3.1.3 on 2020-11-11 21:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0005_parlayuser_class_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='award_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=400), default=list, size=8),
        ),
    ]
