# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-15 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20170302_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='processingresult',
            name='crit',
            field=models.FloatField(default=0),
        ),
    ]
