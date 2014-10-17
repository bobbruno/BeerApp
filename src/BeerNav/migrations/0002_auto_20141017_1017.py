# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('BeerNav', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100, verbose_name=b'City', db_column=b'city_name', validators=[django.core.validators.MinLengthValidator(1)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Name', models.TextField(db_column=b'cont_name', default=b'', max_length=30, validators=[django.core.validators.MinLengthValidator(1)], unique=True, verbose_name=b'Continent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='city',
            name='continent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Continent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Country'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='city',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Location'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='country',
            name='txDefaultName',
        ),
        migrations.RemoveField(
            model_name='location',
            name='txLocationDescription',
        ),
        migrations.RemoveField(
            model_name='location',
            name='txLocationName',
        ),
        migrations.AddField(
            model_name='beer',
            name='ABV',
            field=models.FloatField(db_column=b'beer_abv', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], blank=True, help_text=b'Alcohol By Volume', null=True, verbose_name=b'ABV%'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='IBU',
            field=models.FloatField(db_column=b'beer_ibu', validators=[django.core.validators.MinValueValidator(0)], blank=True, help_text=b'International Bitterness Units', null=True, verbose_name=b'IBU'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='availBottle',
            field=models.NullBooleanField(verbose_name=b'Available in bottle', db_column=b'beer_avail_bottle'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='availTap',
            field=models.NullBooleanField(verbose_name=b'Available in tap', db_column=b'beer_avail_tap'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='avgRating',
            field=models.FloatField(help_text=b'Common average of scores', verbose_name=b'Avg Rating', null=True, editable=False, db_column=b'beer_avg_rating'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='calories',
            field=models.FloatField(db_column=b'beer_calories', validators=[django.core.validators.MinValueValidator(0)], blank=True, help_text=b'Calories', null=True, verbose_name=b'Calories'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BeerNav.City', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='continent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Continent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Country'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='distribution',
            field=models.CharField(db_column=b'beer_distribution', max_length=50, blank=True, help_text=b'Distribution scope', null=True, verbose_name=b'Distribution'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='nRatings',
            field=models.PositiveIntegerField(db_column=b'beer_nratings', default=0, editable=False, help_text=b'Number of ratings for the beer in the database', null=True, verbose_name=b'# Ratings'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='name',
            field=models.CharField(default=b'', max_length=100, verbose_name=b'Beer', db_column=b'beer_name', validators=[django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='overallRating',
            field=models.FloatField(help_text=b'Bayesian average of scores', verbose_name=b'Overall Rating', null=True, editable=False, db_column=b'beer_overall_rating'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='seasonal',
            field=models.CharField(db_column=b'beer_seasonal', choices=[(b'Summer', b'Summer'), (b'Special', b'Special'), (b'None', b'None'), (b'Spring', b'Spring'), (b'Autumn', b'Autumn'), (b'Winter', b'Winter'), (b'Series', b'Series')], max_length=30, blank=True, null=True, verbose_name=b'Seasonal'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Style'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='styleRating',
            field=models.FloatField(help_text=b'Rating compared to other beers in the same style', verbose_name=b'Style Rating', null=True, editable=False, db_column=b'beer_style_rating'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brewery',
            name='continent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Continent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brewery',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Country'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brewery',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brewery',
            name='nBeers',
            field=models.PositiveIntegerField(default=0, verbose_name=b'# Beers', db_column=b'number_beers'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brewery',
            name='name',
            field=models.CharField(default=b'', max_length=100, verbose_name=b'Brewery', db_column=b'brewery_name', validators=[django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brewery',
            name='type',
            field=models.CharField(db_column=b'brewery_type', default=b'', choices=[(b'Brewpub/Brewery', b'Brewpub/Brewery'), (b'Microbrewery', b'Microbrewery'), (b'Contract Brewer', b'Contract Brewer'), (b'Client Brewer', b'Client Brewer'), (b'Brewpub', b'Brewpub'), (b'Commercial Brewery', b'Commercial Brewery')], max_length=30, validators=[django.core.validators.MinLengthValidator(1)], verbose_name=b'Brewery type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='continent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Continent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='name',
            field=models.CharField(default=b'', max_length=50, verbose_name=b'Country', db_column=b'country_name', validators=[django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='continent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Continent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=0, to='BeerNav.Country'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='descr',
            field=models.CharField(max_length=500, null=True, verbose_name=b'Loc. Description', db_column=b'location_description', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='name',
            field=models.CharField(default=b'', max_length=50, verbose_name=b'Location', db_column=b'location_name', validators=[django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='style',
            name='name',
            field=models.CharField(db_column=b'style_name', default=b'', max_length=50, validators=[django.core.validators.MinLengthValidator(1)], unique=True, verbose_name=b'Beer Style'),
            preserve_default=True,
        ),
    ]
