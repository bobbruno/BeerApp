from django.db import models

# Create your models here.


class Country(models.Model):
    txDefaultName = models.CharField(max_length=50, null = False)


class Location(models.Model):
    """
    A geographic location for another object, which could be a factory,
    a bar, even a person's address.
    """
    txLocationName = models.CharField(max_length=50, null=False)
    txLocationDescription = models.CharField(max_length=500)


class Brewery(models.Model):
    """
    A brewery is a company that brews beers. One brewery can have many
    beers, and possibly many locations.
    """


class Style(models.Model):
    """
    Beer styles are a taxonomy for how beers are prepared.
    """


class Beer(models.Model):
    """
    A beer is a beer is a beer.
    """
    