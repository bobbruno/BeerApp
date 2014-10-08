'''
Created on 18/09/2014

@author: bobbruno
'''

import bs4
import csv
import datetime
import itertools


class WrongBeer(Exception):
    """
     Exception that occurs when a beer Id being supplied that is inconsistent to the beer that was expected
    """
    def __init__(self, beerId, wrongId):
        """
        Defines the exception values.
        :param beerId: the expected beer Id
        :type beerId: int
        :param wrongId: the beer Id supplied
        :type wrongId: int
        """
        self.beerId = beerId
        self.wrongId = wrongId

    def __str__(self):
        return 'Expected {}, got {}'.format(self.beerId, self.wrongId)


class BeerGlass(object):
    def __init__(self, glassId, glassName):
        self.id = glassId
        self.name = glassName


glassCollection = {}


class City(object):
    nCities = 0
    def __init__(self, city, cityName):
        """
        Initializes the city object.
        :param city: Unique id of the city
        :type city: int
        :param cityName: name of the city
        :type cityName: str
        """
        self.id = City.nCities
        City.nCities += 1
        self.URL = city
        self.name = cityName

    def __str__(self, *args, **kwargs):
        return u'{cId},"{cName}"'.format(cId=self.id, cName=self.name)


cityCollection = {}


class Beer(object):
    """
    Placeholder class for beer information. Has the following fields
               0: Beer name
                1: Beer id
                2: beer URL
                3: abv
                4: avg
                5: overall
                6: style rating
                7: # of ratings
    """
    def __init__(self, beerId, beerName, brewer, URL, styleId, styleName, abv, IBU,
                 calories, glasses, avgRate, overPerf, stylePerf, nRatings,
                 city, availBottle='unknown',
                 seasonality=None, availTap='unknown', distribScope='unknown'):
        """
        Initializes the beer object
        :param beerId: Unique identifier of the beer
        :type beerId: int
        :param beerName: Name of the beer
        :type beerName: str
        :param brewer: Brewery that crafts the beer.
        :type brewer: Brewer
        :param URL: URL for the beer details' landing page
        :type URL: str
        :param styleId: Id for the beer style
        :type styleId: int
        :param styleName: Name of the beer style
        :type styleName: str
        :param abv:
        :type abv: float
        :param IBU:
        :type IBU: int
        :param calories:
        :type calories: int
        :param glasses:
        :type glasses: list
        :param avgRate:
        :type avgRate: float
        :param overPerf:
        :type overPerf: float
        :param stylePerf:
        :type stylePerf: float
        :param nRatings:
        :type nRatings: int
        :param city:
        :type city: City
        :param availBottle:
        :type availBottle: str
        :param  seasonality:
        :type  seasonality: str
        :param availTap:
        :type availTap: str
        :param distribScope:
        :type distribScope: str
        """
        self.id = beerId
        self.name = beerName.replace('"', '""').replace("'", "''")
        self.brewer = brewer
        self.URL = URL
        self.styleId = styleId
        self.styleName = styleName
        if city is not None:
            if city.id not in cityCollection:
                cityCollection[city.id] = city
        self.city = city
        self.abv = abv if abv != 'None' else None
        self.IBU = IBU if IBU != 'None' else None
        self.calories = calories if calories != 'None' else None
        for g in glasses:
            if g.id not in glassCollection:
                glassCollection[g.id] = g
        self.glasses = glasses
        if availBottle == 'unknown':
            self.availBottle = None
        elif availBottle in set(['available', 'common', 'True']):
            self.availBottle = True
        else:
            self.availBottle = False
        if availTap == 'unknown':
            self.availTap = None
        elif availTap in set(['available', 'common', 'True']):
            self.availTap = True
        else:
            self.availTap = False
        self.seasonality = seasonality
        self.avgRate = avgRate
        self.overPerf = overPerf
        self.stylePerf = stylePerf
        self.nRatings = nRatings
        self.distrScope = distribScope
        self.ratings = []

    def __str__(self):
        return (u'{cont},{count},{loc},{brew},{bId},"{bName}",{bStyle},"{bStyleName}",{city},'
                u'{bAbv},{bIBU},{bNCals},{bavBot},{bavTap},{season},{bOvrlRt},{bAvg},'
                u'{bStyleRt},{bNRatings},"{bDistrScope}"').format(
                    cont=self.brewer.location.country.continent.id,
                    count=self.brewer.location.country.id,
                    bStyleName=self.styleName,
                    loc=self.brewer.location.id, brew=self.brewer.id,
                    bId=self.id, bName=self.name, bAbv=self.abv,
                    bAvg=self.avgRate, bOvrlRt=self.overPerf,
                    bStyleRt=self.stylePerf, bIBU=self.IBU,
                    bavBot=self.availBottle, bavTap=self.availTap,
                    bNRatings=self.nRatings, bNCals=self.calories,
                    city='None,None' if self.city is None else self.city,
                    season=self.seasonality, bStyle=self.styleId, bDistrScope=self.distrScope)

    def __repr__(self):
        return u'{bId}'.format(self.id)

    @staticmethod
    def fileHead():
        return (u'Continent,Country,Location,Brewery,BeerId,BeerName,BeerStyle,"Style Name",CityId,CityName,'
                u'ABV,IBU,NCals,AvailBottle,AvailTap,Seasonal,OveralllRating,BayesianAvg,'
                u'StyleRating,NRatings,"Distr. Scope"')

    def getRatings(self):
        for r in self.ratings:
            yield r

    def getGlasses(self):
        for g in self.glasses:
            yield g

    def addRating(self, rating):
        """
        Adds a rating object to the dictionary of ratings.
        :param rating: the rating.
        :type rating: UserRating
        """
        if rating.beer is None:
            rating.beerId = self.id
        elif rating.beer != self:
            raise WrongBeer(self.id, rating.beerId)
        self.ratings.append(rating)
        #  TODO: Check for uniqueness. Key would be userid, beerid, date

    def rate(self, userId, userName, final, aroma, appearance, taste, palate, overall, location, date, notes):
        """float
        Creates a user rating for the beer based on the raw information passed.
        :param userId: Id# of the user
        :type userId: int
        :param userName: Text identifier of the user
        :type userName: str
        :param final: Aggregate score for the user, between 0 and 5.
        :type final: float
        :param aroma: user rating for the aroma rating, between 0 and 10.
        :type aroma: int
        :param appearance: user rating for the appearance rating, between 0 and 5.
        :type appearance: int
        :param taste: user rating for the taste rating, between 0 and 10.
        :type taste: int
        :param palate: user rating for the palate rating, between 0 and 5.
        :type palate: int
        :param overall: user rating for the overall rating, between 0 and 20.
        :type overall: int
        :param location: location of the user (or the rating, not sure).
        :type location: undef
        :param date: date of the rating.
        :type date: datetime.date
        :param notes: text notes of the rating.
        :type notes: str
        """
        self.addRating(UserRating(self.id, userId, userName,
                                  final, aroma, appearance, taste,
                                  palate, overall, location, date, notes))


class UserRating(object):
    def __init__(self, beer, userId, userName, compound, aroma, appearance,
                 taste, palate, overall, location, date, notes):
        """
        Creates a record of a user rating for a specific beer
        :param beer: The Beer
        :type beer: Beer
        :param userId: Id# of the user
        :type userId: int
        :param userName: Text identifier of the user
        :type userName: str
        :param final: Aggregate score for the user, between 0 and 5.
        :type final: float
        :param aroma: user rating for the aroma rating, between 0 and 10.
        :type aroma: int
        :param appearance: user rating for the appearance rating, between 0 and 5.
        :type appearance: int
        :param taste: user rating for the taste rating, between 0 and 10.
        :type taste: int
        :param palate: user rating for the palate rating, between 0 and 5.
        :type palate: int
        :param overall: user rating for the overall rating, between 0 and 20.
        :type overall: int
        :param location: location of the user (or the rating, not sure).
        :type location: undef
        :param date: date of the rating.
        :type date: datetime.date
        :param notes: text notes of the rating.
        :type notes: str
        """
        self.beer = beer
        self.id = userId
        self.name = userName
        self.compound = compound
        self.aroma = aroma
        self.appearance = appearance
        self.taste = taste
        self.palate = palate
        self.overall = overall
        self.location = location
        self.date = date
        self.notes = notes.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ').replace('\r', ' ')

    def __str__(self):
        #  TODO: Deal with location formatting. Right now it's probably useless
        #  TODO: Implement notes processing to avoid quote problems
        #  TODO: Format date
        return (u'{beerId},{userId},"{userName}",{compound},'
                u'{aroma},{appearance},{taste},{palate},'
                u'{overall},"{location}","{date}","{notes}"').format(
                    beerId=self.beer.id, userId=self.id, userName=self.name,
                    compound=self.compound, aroma=self.aroma, appearance=self.appearance,
                    taste=self.taste, palate=self.palate, overall=self.overall,
                    location=self.location, date=self.date,
                    notes=self.notes)

    @staticmethod
    def fileHead():
        return (u'beerId,userId,"userName",compound,'
                u'aroma,appearance,taste,palate,'
                u'overall,"location","date","notes"')


class Brewery(object):
    def __init__(self, location, breweryId, breweryName, breweryType=None, NBeers=0, yearEstablish=None, bURL=None):
        """
        Initializes the brewery object.
        :param location: location of the brewery.
        :type location: Location
        :param breweryId: Unique id of the brewery.
        :type breweryId: int
        :param breweryName: Name of the brewery.
        :type breweryName: str
        :param breweryType: type of brewery.
        :type breweryType: str
        :param yearEstablish: Year the brewery was established.
        :type yearEstablish: int
        :param bURL: URL for the brewery
        :type bURL: str
        """
        self.location = location
        self.id = breweryId
        self.name = breweryName
        self.bType = breweryType
        self.nBeers = NBeers
        self.yEstb = yearEstablish
        #  TODO: Get this back to bURL. Did change to reuse cache.
        self.URL = '/brewers/x/{}/'.format(breweryId)
        self.Beers = {}

    def __str__(self):
        return (u'{contId},{cId},{lId},{bId},"{bName}","{bType}",{nBeers},{yEst}').format(
                    contId=self.location.country.continent.id,
                    cId=self.location.country.id,
                    lId=self.location.id,
                    bId=self.id,
                    bName=self.name,
                    bType=self.bType,
                    nBeers=len(self.Beers.keys()),
                    yEst=self.yEstb)

    def __repr__(self):
        return u'{bId}'.format(bId=self.id)

    def getBeers(self):
        for b in self.Beers.itervalues():
            yield b

    def addBeer(self, beer):
        """
        Adds a beer to the brewery.
        :param beer: the beer object.
        :type beer: Beer
        """
        self.Beers[beer.id] = beer
        beer.brewer = self

    @staticmethod
    def fileHead():
        return u'Continent,Country,Location,id,"Brewery","Brewery Type",NBeers,EstYear'


class Location(object):
    def __init__(self, country, locationId, locationName, locationURL):
        """
        Initializes the location object.
        :param country: Country where the location is
        :type country: Country
        :param locationId: Unique id of the location
        :type locationId: int
        :param locationName: Name of the location
        :type locationName: str
        :param locationURL: URL of the location, without the http://www.ratebeer.com/part
        :type locationURL: str
        """
        self.country = country
        self.id = locationId
        self.name = locationName
        self.URL = locationURL
        self.breweries = {}

    def __str__(self):
        return u'{contId},{cId},{lId},"{lName}"'.format(contId=self.country.continent.id,
                                                      cId=self.country.id, lId=self.id,
                                                      lName=self.name)

    def __repr__(self):
        return u'{lId}'.format(lId=self.id)

    def getBreweries(self):
        for b in self.breweries.itervalues():
            yield b

    def addBrewery(self, brewery, bName=None, bType=None, yEstab=None):
        """
        Adds a brewery to the location. If a brewery of the same id already existed, it will be OVERWRITTEN.
        :param brewery: either a Brewery object or an int representing the country id.
        :type brewery: int or Brewery
        :param bName: if a Brewery object is passed, should not be specified. Otherwise, the brewery's name.
        :type bName: str
        :param bType: if a Brewery object is passed, should not be specified. Otherwise, the brewery's type.
        :type bType: str
        :param yEstab: Brewery object is passed, should not be specified. Otherwise, the brewery's 
        :type yEstab: int
        :param country: either a Country object or an int representing the country id.
        :type country: object
        :param countryName: if a country object is passed, should not be specified. Otherwise, it's the country's name.
        :type countryName: str
        """
        if type(brewery) == int:
            if bName is None:
                raise ValueError
            self.breweries[brewery] = Brewery(self, brewery, bName, bType, yEstab)
        else:
            self.breweries[brewery.id] = brewery
            brewery.location = self

    @staticmethod
    def fileHead():
        return (u'Continent,Country,id,"Location"')


class Country(object):
    def __init__(self, continent, countryId, countryName):
        """
        Initializes the country object.
        :param continent: Parent continent
        :type continent: Continent
        :param countryId:
        :type countryId: int
        :param countryName:
        :type countryName: str
        """
        self.continent = continent
        self.id = countryId
        self.name = countryName
        self.locations = {}

    def __str__(self):
        return u'{contId},{cId},"{cName}"'.format(contId=self.continent.id,
                                                cId=self.id, cName=self.name)

    def __repr__(self):
        return u'{cId}'.format(self.id)

    def getLocations(self):
        for l in self.locations.itervalues():
            yield l

    def addLocation(self, location, locationName=None, locationURL=None):
        """
        Adds a location to the country. if a location of the same id already existed, it will be OVERWRITTEN.
        :param location: either a location object or and int representing the location id.
        :type location: object
        :param locationName: if a location object is passed, should not be specified. Otherwise, it's the location's name.
        :type locationName: str
        :param locationURL: the URL to the location's page.
        :type locationURL: str
        """
        if type(location) == int:
            if locationName is None:
                raise ValueError
            self.locations[location] = Location(self, location, locationName, locationURL)
        else:
            self.locations[location.id] = location
            location.country = self

    @staticmethod
    def fileHead():
        return (u'Continent,id,"Country"')


class Continent(object):
    def __init__(self, contId, contName):
        """
        Initializes the continent
        :param contId: unique id of the continent
        :type contId: int
        :param contName: Name of the continent
        :type contName: str
        """
        self.id = contId
        self.name = contName
        self.countries = {}

    def __str__(self):
        return u'{cId},"{cName}"'.format(cId=self.id, cName=self.name)

    def __repr__(self):
        return u'{cId}'.format(cId=self.id)

    def getCountries(self):
        for c in self.countries.itervalues():
            yield c

    def addCountry(self, country, countryName=None):
        """
        Adds a country to the continent. if a country of the same id already existed, it will be OVERWRITTEN.
        :param country: either a Country object or and int representing the country id.
        :type country: int or Country
        :param countryName: if a country object is passed, should not be specified. Otherwise, it's the countrie's name.
        :type countryName: str
        """
        if type(country) == int:
            if countryName is None:
                raise ValueError
            self.countries[country] = Country(self, country, countryName)
        else:
            self.countries[country.id] = country
            country.continent = self

    @staticmethod
    def fileHead():
        return (u'id,"Continent"')


class Parser(object):
    """
    Class for parsing the html data
    """
    def __init__(self, scraper, loc='./', initFiles=True, verbose=False):
        """
        Constructor for the class
        :param scraper: scraper to use to get the site pages
        :type scraper: Scraper
        :param fLocation: location to create the csv files
        :type fLocation: str
        :param initFiles: Should the csv files be initialized ?
        :type initFiles: bool
        :param verbose: Should the progress be printed ?
        :type verbose: bool
        """
        self.fLocation = loc
        self.scraper = scraper
        self.verbose = verbose
        self.beerContinents = {}
        self._currCont = None
        self._currCountry = None
        self._currLocation = None
        self._currBrewery = None
        self._currBeer = None
        self._nConts, self._nCountries, self._nLocs = -1, -1, -1
        self._countriesToRate = set()
        self._continentsToRate = set()
        self._locationsToRate = set()
        if initFiles:
            self.initializeFiles()

    def initializeFiles(self):
        """
        Initializes all the csv files, deleting whatever was there and creating just headers for all of them.
        """
        with open('{}/continents.csv'.format(self.fLocation), 'w') as fConts:
            fConts.write(u'{}\n'.format(Continent.fileHead()))
        with open('{}/countries.csv'.format(self.fLocation), 'w') as fCountries:
            fCountries.write(u'{}\n'.format(Country.fileHead()))
        with open('{}/locations.csv'.format(self.fLocation), 'w') as fLocs:
            fLocs.write(u'{}\n'.format(Location.fileHead()))
        with open('{}/breweries.csv'.format(self.fLocation), 'w') as fBrewers:
            fBrewers.write(u'{}\n'.format(Brewery.fileHead()))
        with open('{}/beers.csv'.format(self.fLocation), 'w') as fBeers:
            fBeers.write(u'{}\n'.format(Beer.fileHead()))
        with open('{}/ratings.csv'.format(self.fLocation), 'w') as fRatings:
            fRatings.write(u'{}\n'.format(UserRating.fileHead()))

    def limitLocations(self, locationSet):
        self._locationsToRate = locationSet

    def limitCountries(self, countrySet):
        self._countriesToRate = countrySet

    def limitContinents(self, continentSet):
        self._continentsToRate = continentSet

    def parseBeerDetails(self, beerURL):
        """
        Parses all the details and ratings for one specific beer.
        :param beerURL: beer's landing page.
        :type beerURL: str
        :rtype Beer
        """
        def getHeader(beerPage):
            """
            Processes the header of the beer page, getting the beer's info.
            :param beerPage: the beer's page contents
            :type beerPage: bs4.Tag
            :rtype Beer
            """
            beerId = int(beerURL.split('/')[-2])
            currTag = beerPage.findChild('div', id='container').contents[3].contents[0].contents[1].contents[2].contents[1]
            beerName = currTag.contents[8].text.strip()
            currTag = beerPage.findChild('div', {'style': 'background-color: #036; width: 100px; height: 100px; border-radius: 130px;z-index: 5;text-align: center; '})
            try:
                currTag2 = currTag.contents[0].contents[2]    #  If there's no overall, this is AttributeError
                overPerf = float(currTag2.text)    #  If overall is n/a, this is ValueError
            except:
                overPerf = None
            currTag = currTag.next_sibling    #  Move to the style score HTML
            try:
                stylePerf = float(currTag.text.replace('style', ''))
            except ValueError:
                stylePerf = None
            currTag = currTag.parent.parent.next_sibling
            currTag2 = currTag.contents[0].findChild('big')    #  Beer style HTML
            currTag2 = currTag2.next_sibling.next_sibling.next_sibling
            style = int(currTag2.attrs['href'].split('/')[-2])
            #  TODO: See what to do with the style names - I'll probably need them for presenting
            styleName = currTag2.text
            currTag2 = currTag2.find_next_sibling('a')    #  City HTML
            if currTag2 is not None:
                city = City(currTag2.attrs['href'], currTag2.text)
            else:
                city = None
            currTag2 = currTag.contents[1]    #  Pouring glass HTML
            glasses = []
            for g in currTag2.findChildren('a'):
                glasses.append(BeerGlass(g.attrs['href'].split('=')[-1], g.text))
            currTag2 = currTag.contents[3].contents[0].contents[1]    #  Availability table HTML
            availBottle = unicode(currTag2.contents[0].contents[2])    #  Hopefully, the beer's availability
            currTag2 = currTag2.next_sibling.next_sibling    #  Move to tap avail HTML
            availTap = unicode(currTag2.contents[0].contents[2])
            currTag2 = currTag2.next_sibling.next_sibling    #  Move to gen distrib HTML
            distrScope = currTag2.contents[0].contents[0].contents[0].text
            currTag = currTag.parent.parent.next_sibling    #  Beer numeric data
            currTag2 = currTag.contents[0].contents[0].next_sibling    #  Number of Ratings
            nRatings = int(currTag2.text)
            #  Check for real average (Mean) and skip it if it's there
            currTag2 = currTag2.next_sibling.next_sibling
            if currTag2.contents[0] == 'MEAN: ':
                currTag2 = currTag2.next_sibling.next_sibling
            avgRate = float(currTag2.contents[1].text)    #  weighted Average
            #  Deal with the fact that some of the following information may be missing
            currTag2 = currTag2.next_sibling    #  Check for Seasonality
            if (currTag2.strip() == 'SEASONAL:'):
                currTag2 = currTag2.next_sibling
                seasonality = currTag2.text
            else:
                seasonality = None
                while (type(currTag2) == bs4.NavigableString or
                       currTag2.name != 'abbr'):
                    currTag2 = currTag2.next_sibling
            if currTag2.text == 'IBU':    #  Check for IBU
                currTag2 = currTag2.next_sibling.next_sibling
                IBU = int(currTag2.text)
                while (type(currTag2) == bs4.NavigableString or
                       currTag2.name != 'abbr'):
                    currTag2 = currTag2.next_sibling
            else:
                IBU = None
            if currTag2.text == 'EST. CALORIES':    #  Check for Calories
                currTag2 = currTag2.next_sibling.next_sibling
                calories = int(currTag2.text)
                while (type(currTag2) == bs4.NavigableString or
                       currTag2.name != 'abbr'):
                    currTag2 = currTag2.next_sibling
            else:
                calories = None
            if currTag2.text == 'ABV':    #  Check for abv
                currTag2 = currTag2.next_sibling.next_sibling
                try:
                    abv = float(currTag2.text[:-1])
                except ValueError:
                    abv = None
            else:
                abv = None
            theBeer = Beer(beerId, beerName, self._currBrewery, beerURL, style,
                           styleName, abv, IBU, calories, glasses, avgRate, overPerf,
                           stylePerf, nRatings, city, availBottle, seasonality,
                           availTap, distrScope)
            return theBeer

        def getRatings(beerPg):
            """
            Gets the ratings from the table at XPath '//*[@id="container"]/span/table/tbody/tr[2]/td[2]/div/table[3]'
            :param beerPg: the beer page itself
            :type beerPage: bs4.Tag
            """
            currTag = beerPg.body.findChild('td', {'id': 'tdL'}).next_sibling
            currTag = currTag.contents[0].findChild('table',
                                                    {'cellpadding': '0',
                                                     'cellspacing': '0',
                                                     'border': '0',
                                                     'style': 'padding: 10px;'})
            currTag2 = currTag.contents[0].contents[0].contents[0]
            while currTag2 is not None:
                if (currTag2.name == 'table'):    #  Skipping ad blocks in the middle of the table
                    currTag2 = currTag2.next_sibling.next_sibling
                    continue
                currTag3 = currTag2.contents[1]    #  Compound rating
                compound = float(currTag3.text)
                currTag3 = currTag3.next_sibling
                for i in currTag3.children:
                    if (type(i) == bs4.NavigableString) or (i.name == 'big'):
                        continue
                    texto = i.text.strip()
                    if (texto == "AROMA"):
                        aroma = int(i.next_sibling.text.split('/')[0])
                    elif (texto == "APPEARANCE"):
                        appearance = int(i.next_sibling.text.split('/')[0])
                    elif (texto == "TASTE"):
                        taste = int(i.next_sibling.text.split('/')[0])
                    elif (texto == "PALATE"):
                        palate = int(i.next_sibling.text.split('/')[0])
                    elif (texto == "OVERALL"):
                        overall = int(i.next_sibling.text.split('/')[0])
                currTag2 = currTag2.next_sibling
                currTag3 = currTag2.contents[0]
                userId = currTag3.attrs['href'].split('/')[-2]    #  User id (I may need it for training)
                userName = currTag3.text.split()[0]
                currTag3 = currTag3.next_sibling
                rateLoc = currTag3.split(' - ')[1].strip()
                rateDate = datetime.datetime.strptime(currTag3.split('-')[-1].strip(), "%b %d, %Y")    #  TODO: Check if locale will cause problems here
                currTag2 = currTag2.next_sibling.next_sibling    #  Moving to the notes
                rateNotes = currTag2.text    #  TODO: Check what kinds of characters I need to process in order to avoid problems. Maybe encapsulate in the object.
                theRating = UserRating(self._currBeer, userId, userName,
                                       compound, aroma, appearance, taste,
                                       palate, overall, rateLoc, rateDate,
                                       rateNotes)
                self._currBeer.addRating(theRating)
                #  Go to the next line, if there's one
                currTag2 = currTag2.next_sibling.next_sibling

        try:
            beerHTML = self.scraper.getSite(u'http://www.ratebeer.com{}'.format(unicode(beerURL)))
            beerPage = bs4.BeautifulSoup(beerHTML)
            #  Get beer header information
            theBeer = getHeader(beerPage.html.body)
            if theBeer.overPerf is None:
                raise ValueError
        except:
            return None
        previousBeer, self._currBeer = self._currBeer, theBeer
        if (not len(self._countriesToRate) or
                self._currCountry.name in self._countriesToRate):
            try:
                getRatings(beerPage)
            except:
                self._currBeer = previousBeer
            #  Check if there are more rating pages
            #  //*[@id="container"]/span/table/tbody/tr[2]/td[2]/div
            currTag = beerPage.html.body.findChild('div', id='container').contents[3].contents[0].contents[2].contents[1].contents[0]
            for currTag2 in currTag.findChildren('a', recursive=False):
                beerHTML = self.scraper.getSite(u'http://www.ratebeer.com{}'.format(unicode(currTag2.attrs['href'])))
                beerPg2 = bs4.BeautifulSoup(beerHTML)
                try:
                    getRatings(beerPg2)
                except:
                    self._currBeer = previousBeer
                    return None
            with open('{}/ratings.csv'.format(self.fLocation), 'a') as fReviews:
                for r in theBeer.getRatings():
                    fReviews.write(u'{}\n'.format(unicode(r)).encode('utf8'))
        #  TODO: Save the glasses
        return theBeer

    def parseBrewery(self, brURL):
        """
        Processes the brewer's information and returns a Brewery object with all underlying beers.
        Skips retired, once-in-a-lifetime beers and beers with less than 10 ratings.
        :param brURL: brewer's landing page
        :type brURL: str
        :rtype Brewery
        """
        def processBeerRow(tag):
            """
            Gets a Tag object with a row of beer data and returns a link
            for that beer's page if applicable. Retired beers or beers with
            less than 10 ratings should not be considered.
            :param tag: tag pointing to the line of data about the beer
            :rtype str
            """
            #  //*[@id="container"]/table/tbody/tr/td[2]/span/table[2]/tbody/tr[5]/td[2]/span
            if tag.findChild('span', {'class': 'rip'}) is not None:    #  Skip retired beers
                return None
            try:
                if (len(tag.contents) < 7 or
                        robustConv(tag.contents[3].text) is None or    #  Skip beers with no avg/5 - not enough data
                        robustConv(tag.contents[4].text) is None or    #  Skip beers with no overall - not enough data
                        robustConv(tag.contents[6].text) < 10):    #  Skip beers with too few ratings - not enough data
                    return None
            except:
                print(tag.text)
                return None
            try:
                beerURL = unicode(tag.contents[0].contents[1].attrs['href'].decode('latin-1'))
            except:
                return None
            return beerURL

        response = self.scraper.getSite('http://www.ratebeer.com{}'.format(brURL))
        soup = bs4.BeautifulSoup(response).html.body
        try:
            brewerPage = soup.findChild('td', {'width': '85%'}).findChild('span', {'class': 'beerfoot'}).findChild('table', {'class': 'maintable nohover'})
        except AttributeError:    #  Probably a brewer no longer in the database, can't create data
            return None

        with open('{}/beers.csv'.format(self.fLocation), 'a') as fBeers:
            sleepTime, self.scraper.sleepTime = self.scraper.sleepTime, 0
            for b in itertools.chain(brewerPage.findChildren('tr',
                                     {'class': 'dataTableRowAlternate'}),
                                     brewerPage.findChildren('tr',
                                     {'class': ''})):
                beerURL = processBeerRow(b)
                if beerURL is not None:
                    theBeer = self.parseBeerDetails(beerURL)
                    if theBeer is not None:
                        fBeers.write(u'{}\n'.format(unicode(theBeer)).encode('utf8'))
                        self._currBrewery.addBeer(theBeer)
            self.scraper.sleepTime = sleepTime
        return self._currBrewery

    def parseLocation(self, locURL):
        """
        Processes the location page and the brewers in int. Returns a Location
        object, which contains all active breweries under it. Assumes the
        location is under self._currCountry.
        :param locURL: the location's URL
        :type locURL: str
        :rtype Location
        """
        def processLocRow(tag):
            frCol = tag.findChild()
            brewerHTML = frCol.findChild()
            #  FIXME: This code must be improved to deal with the possibility that only part of the information is available
            #  and it changes. It'd be nice also to get some more information, like address (at least city), Google maps link, etc.
            """
            brBase = soup.html.body.findChild('td', {'width':'85%'}).findChild('span', {'class': 'beerfoot'}).findChild('span', {'class': 'beerfoot'}).nextSibling.nextSibling.nextSibling
            try:
                assocPlace = brBase.text
                assocURL = brBase.contents[0].attrs['href']
                brURL = brBase.nextSibling.nextSibling.nextSibling.attrs['href']
                brFcbk = brBase.nextSibling.nextSibling.nextSibling.nextSibling.attrs['href']"""
            brewery = brewerHTML.text
            if self.verbose:
                print u'\t\t\t Processing {}'.format(brewery).encode('utf8')
            brType = frCol.next_sibling
            brNBeer = brType.next_sibling
            brEstDate = int(brNBeer.next_sibling.next_sibling.text)    #  @IgnorePep8
            theBrewery = Brewery(self._currLocation,
                                 int(brewerHTML.attrs['href'][9:].split('/')[1]),
                                 brewery, brType.text, int(brNBeer.text), int(brEstDate),
                                 brewerHTML.attrs['href'])
            if self.verbose:
                print self._currCont.id, self.findNextSibling_currCountry.id, self._currLocation.id, \
                    theBrewery.id, theBrewery.name, \
                    theBrewery.bType, len(theBrewery.Beers.keys()), \
                    theBrewery.yEstb
            return theBrewery

        response = self.scraper.getSite(locURL)
        soup = bs4.BeautifulSoup(response).html.body
        self._nLocs += 1
        locName = soup.findChild('div', id='brewerCover').contents[1].text.split('  ')[0]
        self._currLocation = Location(self._currCountry, self._nLocs, locName, locURL)
        if (not len(self._locationsToRate) or
                locName in self._locationsToRate):
            if self.verbose:
                print u'\t\tBreweries from Country {}, Location {}'.format(
                    self._currCountry.name, self._currLocation.name).encode('utf8')
            locPage = soup.findChild(id='brewerTable').findChild('tbody')
            with open('{}/breweries.csv'.format(self.fLocation), 'a') as fBrewers:
                for bTabLin in locPage.childGenerator():
                    #  Process the brewery table row
                    self._currBrewery = processLocRow(bTabLin)
                    #  Now let's go to the brewer's page and process the beers
                    theBrewery = self.parseBrewery(self._currBrewery.URL)
                    if theBrewery is not None:
                        self._currLocation.addBrewery(theBrewery)
                        fBrewers.write(u'{}\n'.format(unicode(theBrewery)).encode('utf8'))
                        self._currBrewery = theBrewery
        return self._currLocation

    def parseContinents(self, initPage):
        """
        Parse the inicial continent page, returning everything as a dict of Continents.
        :param initPage: the recovered page to be parsed.
        :type initPage: str
        :rtype dict of Continent
        """
        resposta = self.scraper.getSite(initPage)
        soup = bs4.BeautifulSoup(resposta)
        locPage = soup.html.body.findChild(id='brewerCover').next_sibling.next_sibling    #  @IgnorePep8
        bigCountry = ''
        countrySet = set()
        with open('{}/continents.csv'.format(self.fLocation), 'a') as fConts, \
             open('{}/countries.csv'.format(self.fLocation), 'a') as fCountries, \
             open('{}/locations.csv'.format(self.fLocation), 'a') as fLocs:
            for i in locPage.children:
                if (type(i) == bs4.element.Tag):    #  Found a continent
                    if (i.name == u'div'):
                        self._nConts += 1
                        self._currCont = Continent(self._nConts, i.text)
                        if self.verbose:
                            print u'Breweries from {}'.format(self._currCont.name).encode('utf8')
                        fConts.write(u'{}\n'.format(unicode(self._currCont)).encode('utf8'))
                        self.beerContinents[self._currCont.id] = self._currCont
                        bigCountry = ''
                    elif (i.name == u'a'):    #  Found a country, which may have subregions
                        country = bigCountry if len(bigCountry) else i.text
                        if (country not in countrySet):
                            self._nCountries += 1
                            self._currCountry = Country(self._currCont, self._nCountries, country)
                            self._currCont.addCountry(self._currCountry)
                            countrySet.add(country)
                            if self.verbose:
                                print u'\tBreweries from country {}'.format(self._currCountry.name).encode('utf8')
                            fCountries.write(u'{}\n'.format(unicode(self._currCountry)).encode('utf8'))
                        if (not len(self._continentsToRate) or
                                self._currCont.name in self._continentsToRate):
                            locPage = i.attrs['href']
                            currLoc = self.parseLocation('http://www.ratebeer.com{}'.format(locPage))
                            self._currCountry.addLocation(currLoc)
                            fLocs.write(u'{}\n'.format(unicode(currLoc)).encode('utf8'))
                elif (type(i) == bs4.element.NavigableString and
                      len(i.strip()) > 0 and len(i.strip()) < 40):
                    bigCountry = i.strip()
        return self.beerContinents


def robustConv(x, toType=float):
    """
    Converts an object to another type. Will return None when conversion fails.
    :param object x: the object to be converted
    :param type toType: the type to convert to
    """
    try:
        y = toType(x)
    except:
        y = None
    finally:
        return y
