# Generated by Django 3.1.7 on 2021-03-04 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0029_auto_20210302_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='mturk',
            field=models.CharField(blank=True, max_length=33, null=True),
        ),
    ]
