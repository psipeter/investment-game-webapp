# Generated by Django 3.1.5 on 2021-02-05 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_auto_20210113_1815'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RemoveField(
            model_name='agent',
            name='learner',
        ),
        migrations.RemoveField(
            model_name='game',
            name='agentScore',
        ),
        migrations.RemoveField(
            model_name='game',
            name='userScore',
        ),
        migrations.AddField(
            model_name='game',
            name='agentRewards',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='agentStates',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='userRewards',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='agentGives',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='agentKeeps',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='userGives',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='userKeeps',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='userTimes',
            field=models.CharField(blank=True, default=str, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='completionCode',
            field=models.CharField(default='lQDkrjdZ6CkE1D3yhw8XNVz27jzyqP4o', help_text='MTurk Confirmation Code', max_length=32),
        ),
    ]
