# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-02 15:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0016_auto_20180502_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='login',
            field=models.BooleanField(default=True),
        ),
    ]
