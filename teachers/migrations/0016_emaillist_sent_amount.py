# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-30 03:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0015_auto_20170827_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaillist',
            name='sent_amount',
            field=models.IntegerField(default=0),
        ),
    ]
