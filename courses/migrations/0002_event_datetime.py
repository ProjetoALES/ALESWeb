# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-08 06:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(1972, 1, 1, 0, 0)),
        ),
    ]
