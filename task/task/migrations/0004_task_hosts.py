# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-24 10:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20180424_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='hosts',
            field=models.CharField(max_length=256, null=True),
        ),
    ]