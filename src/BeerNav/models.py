from __future__ import unicode_literals

from django.core.validators import MinValueValidator, MaxValueValidator, \
    MinLengthValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import BeerNav.skModels as skModels
import numpy as np


#  Create your models here.
@python_2_unicode_compatible
class Continent(models.Model):
    """ A continent is a large mass of land with one or more countries in it."""
    class Meta:
        ordering = ['name']

    name = models.TextField(db_column='cont_name', max_length=30, unique=True,
                            verbose_name='Continent', default='',
                            validators=[MinLengthValidator(1)])

    def __str__(self):
        return '{}'.format(self.name)


@python_2_unicode_compatible
class Country(models.Model):
    class Meta:
        order_with_respect_to = 'continent'
        ordering = ['name']

    name = models.CharField(db_column='country_name', max_length=50, verbose_name='Country',
                            default='', validators=[MinLengthValidator(1)])
    continent = models.ForeignKey('Continent', on_delete=models.PROTECT, default=0)

    def __str__(self):
        return '{}'.format(self.name)


@python_2_unicode_compatible
class Location(models.Model):
    """
    A geographic location for another object, which could be a factory,
    a bar, even a person's address.
    """
    class Meta:
        order_with_respect_to = 'country'
        ordering = ['name']

    name = models.CharField(db_column='location_name', max_length=50, verbose_name='Location',
                            default='', validators=[MinLengthValidator(1)])
    descr = models.CharField(db_column='location_description', max_length=500,
                             null=True, blank=True, verbose_name='Loc. Description')
    continent = models.ForeignKey('Continent', on_delete=models.PROTECT, default=0)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, default=0)

    def __str__(self):
        return '{}'.format(self.name)


@python_2_unicode_compatible
class City(models.Model):
    """ A specific city, which will be positioned from the beer location information. """
    class Meta:
        order_with_respect_to = 'country'
        ordering = ['name']

    name = models.CharField(db_column='city_name', max_length=100, verbose_name='City',
                            default='', validators=[MinLengthValidator(1)])
    continent = models.ForeignKey('Continent', on_delete=models.PROTECT, default=0)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, default=0)
    location = models.ForeignKey('Location', on_delete=models.PROTECT, default=0)

    def __str__(self):
        return '{}'.format(self.name)


@python_2_unicode_compatible
class Brewery(models.Model):
    """
    A brewery is a company that brews beers. One brewery can have many
    beers, and possibly many locations.
    """

    class Meta:
        order_with_respect_to = 'country'
        ordering = ['name']
    BREW_TYPES = (
        ("Brewpub/Brewery", "Brewpub/Brewery"),
        ("Microbrewery", "Microbrewery"),
        ("Contract Brewer", "Contract Brewer"),
        ("Client Brewer", "Client Brewer"),
        ("Brewpub", "Brewpub"),
        ("Commercial Brewery", "Commercial Brewery"),
    )

    name = models.CharField(db_column='brewery_name', max_length=100, verbose_name='Brewery',
                            default='', validators=[MinLengthValidator(1)])
    type = models.CharField(db_column='brewery_type', max_length=30,
                            verbose_name='Brewery type', choices=BREW_TYPES,
                            default='', validators=[MinLengthValidator(1)])
    nBeers = models.PositiveIntegerField(db_column='number_beers', default=0,
                                         verbose_name='# Beers')
    yearEstablished = models.PositiveSmallIntegerField(db_column='year_established',
                                                       null=True, blank=True,
                                                       verbose_name='Year Established')
    continent = models.ForeignKey('Continent', on_delete=models.PROTECT, default=0)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, default=0)
    location = models.ForeignKey('Location', on_delete=models.PROTECT, default=0)

    def __str__(self):
        return '{} ({})'.format(self.name, self.type)


@python_2_unicode_compatible
class Style(models.Model):
    """
    Beer styles are a taxonomy for how beers are prepared.
    """
    class Meta:
        ordering = ['name']

    name = models.CharField(db_column='style_name', max_length=50, verbose_name='Beer Style',
                            unique=True, default='', validators=[MinLengthValidator(1)])

    def __str__(self):
        return '{}) {}'.format(self.id, self.name)


class BeerManager(models.Manager):

    def get_nearest(self, userPos, nBeers=10):
        """ Returns the nBeers nearest to the userPos set of coordinates.
        :param userPos: The set of coordinates on the PCA space that the user chose.
        :type userPos: dict
        :param nBeers: The number of nearest beers to be returned
        :type nBeers: int """
        userPCA = np.ones(20)
        for k, v in userPos.iteritems():
            userPCA[int(k[1:]) - 1] = float(v)
        _, theBeers = skModels.knn.kneighbors(userPCA, nBeers)
        return list(skModels.dfBeerData[theBeers][0])


@python_2_unicode_compatible
class Beer(models.Model):
    """
    A beer is a beer is a beer.
    """
    class Meta:
        order_with_respect_to = 'brewery'
        ordering = ['style', 'name']
    SEASONAL_TYPES = (
        ("Summer", "Summer"),
        ("Special", "Special"),
        ("None", "None"),
        ("Spring", "Spring"),
        ("Autumn", "Autumn"),
        ("Winter", "Winter"),
        ("Series", "Series")
    )

    objects = BeerManager()
    name = models.CharField(db_column='beer_name', max_length=100, verbose_name='Beer',
                            blank=False, default='', validators=[MinLengthValidator(1)])
    ABV = models.FloatField(db_column='beer_abv', null=True, blank=True, verbose_name='ABV%',
                            help_text='Alcohol By Volume',
                            validators=[MinValueValidator(0),
                                        MaxValueValidator(100)])
    IBU = models.FloatField(db_column='beer_ibu', null=True, blank=True, verbose_name='IBU',
                            help_text='International Bitterness Units',
                            validators=[MinValueValidator(0)])
    calories = models.FloatField(db_column='beer_calories', null=True, blank=True,
                                 verbose_name='Calories', help_text='Calories',
                                 validators=[MinValueValidator(0)])
    availBottle = models.NullBooleanField(db_column='beer_avail_bottle', null=True, blank=True,
                                          verbose_name='Available in bottle')
    availTap = models.NullBooleanField(db_column='beer_avail_tap', null=True, blank=True,
                                       verbose_name='Available in tap')
    seasonal = models.CharField(db_column='beer_seasonal', max_length=30, verbose_name='Seasonal',
                                null=True, blank=True,
                                choices=SEASONAL_TYPES)
    overallRating = models.FloatField(db_column='beer_overall_rating', verbose_name='Overall Rating',
                                      editable=False, null=True,
                                      help_text='Bayesian average of scores')
    avgRating = models.FloatField(db_column='beer_avg_rating', verbose_name='Avg Rating',
                                  editable=False, null=True,
                                  help_text='Common average of scores')
    styleRating = models.FloatField(db_column='beer_style_rating', verbose_name='Style Rating',
                                    editable=False, null=True,
                                    help_text='Rating compared to other beers in the same style')
    nRatings = models.PositiveIntegerField(db_column='beer_nratings', default=0, verbose_name='# Ratings',
                                           editable=False, null=True,
                                           help_text='Number of ratings for the beer in the database')
    distribution = models.CharField(db_column='beer_distribution', max_length=50,
                                    verbose_name='Distribution', help_text='Distribution scope',
                                    null=True, blank=True)
    continent = models.ForeignKey('Continent', on_delete=models.PROTECT, default=0)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, default=0)
    location = models.ForeignKey('Location', on_delete=models.PROTECT, default=0)
    brewery = models.ForeignKey('Brewery', on_delete=models.PROTECT, default=0)
    city = models.ForeignKey('City', on_delete=models.PROTECT, null=True)
    style = models.ForeignKey('Style', on_delete=models.PROTECT, default=0)

    def __str__(self):
        return '{}) {} (from {})'.format(self.id, self.name, self.brewery.name)
