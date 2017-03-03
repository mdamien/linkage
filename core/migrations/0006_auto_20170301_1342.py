# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-01 13:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20170301_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='graph',
            name='links',
        ),
        migrations.RemoveField(
            model_name='processingresult',
            name='clusters',
        ),
        migrations.RemoveField(
            model_name='processingresult',
            name='topics',
        ),
        migrations.RemoveField(
            model_name='processingresult',
            name='topics_terms',
        ),
        migrations.AddField(
            model_name='graph',
            name='dictionnary',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='graph',
            name='edges',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='graph',
            name='labels',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='graph',
            name='tdm',
            field=models.TextField(blank=True, default=''),
        ),
    ]