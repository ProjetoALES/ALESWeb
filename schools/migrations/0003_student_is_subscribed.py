# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 20:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0002_auto_20170101_0028'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_subscribed',
            field=models.BooleanField(default=True),
        ),
    ]
