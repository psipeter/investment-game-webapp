# Generated by Django 3.1.5 on 2021-02-10 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0015_auto_20210210_0104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='completionCode',
            field=models.CharField(default='tEbXL1MM5cTENQTuvjMpZgh5iVgMLO6e', help_text='MTurk Confirmation Code', max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='education',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='income',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='veteran',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
