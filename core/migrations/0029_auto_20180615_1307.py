# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-15 13:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_graph_job_current_step'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graph',
            name='cluster_to_cluster_cutoff',
            field=models.FloatField(default=1e-08),
        ),
    ]
