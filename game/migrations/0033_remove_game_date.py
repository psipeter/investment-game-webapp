# Generated by Django 3.1.7 on 2021-03-23 01:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0032_auto_20210322_2023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='date',
        ),
    ]
