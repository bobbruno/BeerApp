from django.contrib import admin
from BeerNav.models import Continent, Country, Location, Brewery, Style, City, Beer

#  Register your models here.


class ContinentAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('name',)


class CountryAdmin(admin.ModelAdmin):
    fields = ['name', 'continent']
    list_display = ('name', 'continent')


class CityAdmin(admin.ModelAdmin):
    fields = ['name', 'country', 'location']
    list_display = ('name', 'location', 'country')


class LocationAdmin(admin.ModelAdmin):
    fields = ['name', 'country']
    list_display = ('name', 'country')


class BreweryAdmin(admin.ModelAdmin):
    fields = ['name', 'country', 'type', 'nBeers', 'yearEstablished']
    list_display = ('name', 'country', 'type', 'nBeers', 'yearEstablished')
    search_fields = ('name', 'type')


class BeerAdmin(admin.ModelAdmin):
    fields = ['name', 'ABV', 'IBU', 'calories', 'availBottle', 'availTap', 'seasonal',
              'distribution', 'country', 'location', 'city', 'brewery', 'style']
    list_display = ('name', 'style', 'brewery', 'city', 'location', 'overallRating', 'nRatings')
    search_fields = ('name', 'brewery', 'location', 'country')
    list_filter = ('availBottle', 'availTap', 'seasonal', 'style')


admin.site.register(Continent, ContinentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Brewery, BreweryAdmin)
admin.site.register(Beer, BeerAdmin)
admin.site.register([Style])
