from django.contrib import admin
from BeerNav.models import Country, Location, Brewery, Beer, Style

#  Register your models here.

admin.site.register([Country, Location, Brewery, Beer, Style])
