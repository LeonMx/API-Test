# Generated by Django 2.2.5 on 2019-09-11 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearning', '0003_auto_20190911_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='lession',
            name='approval_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='lession',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
