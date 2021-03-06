# Generated by Django 3.1.4 on 2021-01-04 19:41

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('age', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(18), django.core.validators.MaxValueValidator(120)])),
                ('gender', models.CharField(blank=True, choices=[('', '---'), ('m', 'Male'), ('f', 'Female'), ('o', 'Non-Binary')], max_length=300, null=True)),
                ('income', models.FloatField(blank=True, null=True)),
                ('education', models.CharField(blank=True, choices=[('', '---'), ('1', 'Primary (middle) school'), ('2', 'Secondary (high) school'), ('3', 'Undergraduate degree'), ('4', 'Graduate degree'), ('6', 'Other')], max_length=300, null=True)),
                ('veteran', models.BooleanField(blank=True, null=True)),
                ('empathy', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('risk', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('altruism', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('completionCode', models.CharField(default='XAmfJQdElk0sC3UF5kDb2RTS3JiTJuso', help_text='MTurk Confirmation Code', max_length=32)),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='Unique agent ID', primary_key=True, serialize=False)),
                ('agentType', models.CharField(blank=True, default=str, max_length=100, null=True)),
                ('agentBlob', models.BinaryField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updateDB', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='Unique game ID', primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('userMove', models.IntegerField(blank=True, null=True)),
                ('agentMove', models.IntegerField(blank=True, null=True)),
                ('userMoves', models.CharField(blank=True, default=str, max_length=300, null=True)),
                ('userTimes', models.CharField(blank=True, default=str, max_length=300, null=True)),
                ('agentMoves', models.CharField(blank=True, default=str, max_length=300, null=True)),
                ('userRole', models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B')], max_length=1, null=True)),
                ('agentRole', models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B')], max_length=1, null=True)),
                ('userScore', models.IntegerField(blank=True, default=0, null=True)),
                ('agentScore', models.IntegerField(blank=True, default=0, null=True)),
                ('complete', models.BooleanField(default=False)),
                ('nIter', models.IntegerField(default=5)),
                ('capital', models.IntegerField(default=10)),
                ('matchFactor', models.FloatField(default=3)),
                ('seed', models.IntegerField(default=0)),
                ('agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='game.agent')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='currentGame',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='currentGame', to='game.game'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
