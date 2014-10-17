from django.contrib import admin
from BeerNav.models import Continent, Country, Location, Brewery, Style, City, Beer

#  Register your models here.

admin.site.register([Continent, Country, Location, City, Brewery, Beer, Style])
