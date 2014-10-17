from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


#  Create your models here.
class Continent(models.Model):
    contName = models.TextField(db_column='cont_name', max_length=30, unique=True, verbose_name='Continent', null=False)


class Country(models.Model):
    countrytName = models.CharField(db_column='country_name', max_length=50, verbose_name='Country', null=False)
    contId = models.ForeignKey('Continent', on_delete=models.PROTECT)


class Location(models.Model):
    """
    A geographic location for another object, which could be a factory,
    a bar, even a person's address.
    """
    locName = models.CharField(db_column='location_name', max_length=50, verbose_name='Location', null=False)
    locDescr = models.CharField(db_column='location_description', max_length=500, verbose_name='Loc. Description')
    contId = models.ForeignKey('Continent', on_delete=models.PROTECT)
    countryId = models.ForeignKey('Country', on_delete=models.PROTECT)


class City(models.Model):
    """ A specific city, which will be positioned from the beer location information. """
    cityName = models.CharField(db_column='city_name', max_length=100, verbose_name='City',
                                null=False)
    contId = models.ForeignKey('Continent', on_delete=models.PROTECT)
    countryId = models.ForeignKey('Country', on_delete=models.PROTECT)
    locId = models.ForeignKey('Location', on_delete=models.PROTECT)


class Brewery(models.Model):
    """
    A brewery is a company that brews beers. One brewery can have many
    beers, and possibly many locations.
    """
    BREW_TYPES = (
        ("Brewpub/Brewery", "Brewpub/Brewery"),
        ("Microbrewery", "Microbrewery"),
        ("Contract Brewer", "Contract Brewer"),
        ("Client Brewer", "Client Brewer"),
        ("Brewpub", "Brewpub"),
        ("Commercial Brewery", "Commercial Brewery"),
    )

    brewName = models.CharField(db_column='brewery_name', max_length=100, verbose_name='Brewery',
                                null=False)
    brewType = models.CharField(db_column='brewery_type', max_length=30,
                                verbose_name='Brewery type', null=False, choices=BREW_TYPES)
    nBeers = models.PositiveIntegerField(db_column='number_beers', default=0, verbose_name='# Beers', null=False)
    contId = models.ForeignKey('Continent', on_delete=models.PROTECT)
    countryId = models.ForeignKey('Country', on_delete=models.PROTECT)
    locId = models.ForeignKey('Location', on_delete=models.PROTECT)


class Style(models.Model):
    """
    Beer styles are a taxonomy for how beers are prepared.
    """
    styleName = models.CharField(db_column='style_name', max_length=50, verbose_name='Beer Style',
                                 null=False, unique=True)


class Beer(models.Model):
    """
    A beer is a beer is a beer.
    """
    beerName = models.CharField(db_column='beer_name', max_length=100, verbose_name='Beer',
                                null=False)
    beerABV = models.FloatField(db_column='beer_abv', null=True, blank=True, verbose_name='ABV%',
                                help_text='Alcohol by volume',
                                validators=[MinValueValidator(0, "ABV can't be negative"),
                                            MaxValueValidator(100, "ABV can't be above 100")])
    cityId = models.ForeignKey('City', on_delete=models.PROTECT)
    styleId = models.ForeignKey('Style', on_delete=models.PROTECT)
