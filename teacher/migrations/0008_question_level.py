# Generated by Django 3.1.2 on 2020-10-20 23:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0007_auto_20201019_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.level'),
        ),
    ]