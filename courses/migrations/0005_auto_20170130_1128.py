# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-30 13:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20170130_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='day',
            field=models.IntegerField(choices=[(1, 'Sábado'), (2, 'Domingo')], null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='duration',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='time',
            field=models.TimeField(null=True),
        ),
    ]
