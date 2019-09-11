# Generated by Django 2.2.5 on 2019-09-11 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearning', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'student'), (2, 'teacher'), (3, 'admin')], default=3),
        ),
    ]
