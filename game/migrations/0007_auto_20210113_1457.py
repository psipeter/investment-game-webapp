# Generated by Django 3.1.4 on 2021-01-13 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20210112_1850'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='requiredGames',
            new_name='gamesPlayed',
        ),
        migrations.RemoveField(
            model_name='user',
            name='bonusGames',
        ),
        migrations.AlterField(
            model_name='user',
            name='completionCode',
            field=models.CharField(default='QqdKABdDJxCNbfl6MQLBayPUW4kxySEh', help_text='MTurk Confirmation Code', max_length=32),
        ),
    ]
