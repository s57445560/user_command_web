# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-28 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0010_groups_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='hosts',
            name='v_or_s',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
