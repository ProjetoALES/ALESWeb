# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 22:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='s_subscribed',
            field=models.BooleanField(default=True),
        ),
    ]
