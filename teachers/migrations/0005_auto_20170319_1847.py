# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-19 21:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0004_auto_20170319_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emaillist',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teachers.Teacher'),
        ),
    ]
