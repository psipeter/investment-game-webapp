# Generated by Django 3.1.4 on 2021-01-06 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20210105_1743'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='agentMoves',
            new_name='agentGives',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='userMoves',
            new_name='agentKeeps',
        ),
        migrations.RemoveField(
            model_name='game',
            name='agentMove',
        ),
        migrations.RemoveField(
            model_name='game',
            name='userMove',
        ),
        migrations.AddField(
            model_name='game',
            name='userGives',
            field=models.CharField(blank=True, default=str, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='userKeeps',
            field=models.CharField(blank=True, default=str, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='completionCode',
            field=models.CharField(default='eixiX6ITEuxLYfPgUxOQsF3OYCTXmh1O', help_text='MTurk Confirmation Code', max_length=32),
        ),
    ]
