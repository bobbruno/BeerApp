# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BeerNav', '0002_auto_20141017_1017'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='beer',
            options={'ordering': ['style', 'name']},
        ),
        migrations.AlterModelOptions(
            name='brewery',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='city',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='continent',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='style',
            options={'ordering': ['name']},
        ),
        migrations.RenameField(
            model_name='continent',
            old_name='Name',
            new_name='name',
        ),
        migrations.AddField(
            model_name='beer',
            name='brewery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Brewery'),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='beer',
            order_with_respect_to='brewery',
        ),
        migrations.AlterOrderWithRespectTo(
            name='brewery',
            order_with_respect_to='country',
        ),
        migrations.AlterOrderWithRespectTo(
            name='city',
            order_with_respect_to='country',
        ),
        migrations.AlterOrderWithRespectTo(
            name='country',
            order_with_respect_to='continent',
        ),
        migrations.AlterOrderWithRespectTo(
            name='location',
            order_with_respect_to='country',
        ),
    ]
