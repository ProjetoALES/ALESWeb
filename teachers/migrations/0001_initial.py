# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-05 20:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=200)),
                ('nickname', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_subscribed', models.BooleanField(default=True)),
                ('phone', models.CharField(max_length=20, unique=True)),
                ('emailmanager', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Email_Manager')),
                ('schools', models.ManyToManyField(related_name='teachers', to='schools.School')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
