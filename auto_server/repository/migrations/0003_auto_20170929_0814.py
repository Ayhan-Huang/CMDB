# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-29 00:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0002_auto_20170927_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='os_platform',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='系统'),
        ),
        migrations.AlterField(
            model_name='server',
            name='os_version',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='系统版本'),
        ),
    ]
