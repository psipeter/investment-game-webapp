# Generated by Django 3.1.5 on 2021-02-10 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0014_auto_20210209_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='completionCode',
            field=models.CharField(default='9nEAr9no3tpnnfetxzNedRNiiX8GlYnN', help_text='MTurk Confirmation Code', max_length=32),
        ),
    ]
