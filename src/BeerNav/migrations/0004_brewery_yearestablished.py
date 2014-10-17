# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BeerNav', '0003_auto_20141017_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='brewery',
            name='yearEstablished',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Year Established', db_column='year_established', blank=True),
            preserve_default=True,
        ),
    ]
