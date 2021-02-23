# Generated by Django 3.1.7 on 2021-02-23 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0024_auto_20210222_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='doneHIT',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='code',
            field=models.CharField(default='K6EuKfyiibYzkxK73lqk63Y5Romd0bJt', help_text='MTurk Confirmation Code', max_length=300),
        ),
    ]
