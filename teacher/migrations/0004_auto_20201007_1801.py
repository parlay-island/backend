# Generated by Django 3.1.2 on 2020-10-07 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0003_auto_20201007_1745'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='choices',
            new_name='answer',
        ),
    ]
