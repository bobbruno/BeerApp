import bs4
import os
import sys

from Scraper import Scraper


#  import codecs
SCRAPER_CACHE_DIR = '/home/bobbruno/workspace/BeerApp/dumps/'

accounts = [('Eo8xsuVxwG1V', 'Eo8xsuVxwG1V@meltmail.com', 'Eo8xsuVxwG1V01'),
            ('928vr9z45T7b', '928vr9z45T7b@meltmail.com', '928vr9z45T7b01'),
            ('sYprtRIeu2GF', 'sYprtRIeu2GF@meltmail.com', 'sYprtRIeu2GF01')]

uaS = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36']

def processBeerRow(tag):
    """
    Gets a Tag object with a full row of beer data and returns all info on
    that beer as a list:
        0: Beer name
        1: Beer id
        2: beer URL
        3: abv
        4: avg
        5: overall
        6: style rating
        7: ratings
    :param tag: tag pointing to the line of data about the beer
    :type tag: bs4.Tag
    :rtype list
    """
    if tag.findChild('span', {'class': 'rip'}) is not None:
        return []
    try:
        retVal = [tag.contents[0].contents[1].text]
        beerURL = tag.contents[0].contents[1].attrs['href']
        retVal.append(beerURL.split('/')[-2])
        retVal.append(beerURL)
        retVal.append(tag.contents[2].text)
        retVal.append(tag.contents[3].text)
        retVal.append(tag.contents[4].text)
        retVal.append(tag.contents[5].text)
        retVal.append(tag.contents[6].text)
    except Exception, e:
        print e
        retVal = []
    return retVal


#  First, let's get the locations
#  This code captures all the countries and country subdivisions
#  which have known breweries

beerScraper = Scraper(sleepTime=3, cacheDir=SCRAPER_CACHE_DIR, verbose=True, uaString=uaS[2])
result = beerScraper.login(accounts[1][0], accounts[1][2],
                           'http://www.ratebeer.com/login.asp',
                           'signin', 'http://www.ratebeer.com')

resposta = beerScraper.getSite('http://www.ratebeer.com/breweries/')
soup = bs4.BeautifulSoup(resposta)
brwrs = soup.html.body.findChild(id='brewerCover').next_sibling.next_sibling    #  @IgnorePep8

beerContinents = {}
bigCountry = ''
for i in brwrs.children:
    if (type(i) == bs4.element.Tag):    #  Found a continent
        if (i.name == u'div'):
            currContinent = i.text
            beerContinents[currContinent] = {}
            bigCountry = ''
        elif (i.name == u'a'):    #  Found a country, which may have subregions
            country = bigCountry if len(bigCountry) else i.text
            if (country not in beerContinents[currContinent]):
                beerContinents[currContinent][country] = {}
            beerContinents[currContinent][country][i.text] = [i.attrs['href'][11:], {}]    #  @IgnorePep8
    elif (type(i) == bs4.element.NavigableString and
          len(i.strip()) > 0 and len(i.strip()) < 40):
        bigCountry = i.strip()

#  This code captures the breweries for a list of locations for a specific
#  continent and country
subURL = 0
subBreweries = 1
runs = 0

runList = beerContinents
while (len(runList) and (runs < 20)):
    retryList1 = {}
    for continent, countries in beerContinents.iteritems():
        print u'Breweries from {}'.format(continent)
        retryList2 = {}
        for country, locations in countries.iteritems():
            print u'\tBreweries from {}'.format(country)
            retryList3 = {}
            for location, breweries in locations.iteritems():
                print u'\t\tBreweries from {}'.format(location)
                try:
                    resposta = beerScraper.getSite('http://www.ratebeer.com/breweries/{}'.format(breweries[subURL]))    #  @IgnorePep8
                    soup = bs4.BeautifulSoup(resposta)
                except:
                    retryList3[location] = {}
                    continue
                for bTabLin in soup.html.body.findChild(
                        id='brewerTable').findChild('tbody').childGenerator():
                    frCol = bTabLin.findChild()
                    brewer = frCol.findChild()
                    print u'\t\t\t Processing {}'.format(brewer.text)
                    brType = frCol.findNextSibling()
                    brNBeer = brType.findNextSibling()
                    brEstDate = int(brNBeer.findNextSibling().findNextSibling().text)    #  @IgnorePep8
                    breweries[subBreweries][brewer.text] = [brewer.attrs['href'][9:].split('/')[1],
                                    brType.text, int(brNBeer.text), brEstDate, {}]
            if len(retryList3):
                retryList2[country] = retryList3.copy()
        if len(retryList2):
            retryList1[continent] = retryList2.copy()
        break
    runList = retryList1.copy()
    break
    runs += 1

#  Now let's get some beers from a brewery
#  I can get:
#  Associated place: <span class="beerfoot"></span>.nextSibling.nextSibling.firstChild: get href and text
#  website: from previous last sibling, nextSibling.firstChild: get href and text
#  facebook,
#  email
#  The beer list with:
#     Beer name, abv, avg/5 overall, stype, ratings

with open('/home/bobbruno/workspace/BeerApp/dumps/continents.csv', 'w') as fConts, \
    open('/home/bobbruno/workspace/BeerApp/dumps/countries.csv', 'w') as fCountries, \
    open('/home/bobbruno/workspace/BeerApp/dumps/locations.csv', 'w') as fLocs, \
    open('/home/bobbruno/workspace/BeerApp/dumps/breweries.csv', 'w') as fBrewers, \
    open('/home/bobbruno/workspace/BeerApp/dumps/beers.csv', 'w') as fBeers:
    fConts.write('id, Continent\n')
    fCountries.write('Continent, id, Country\n')
    fLocs.write('Continent, Country, id, Location\n')
    fBrewers.write('Continent, Country, Location, id, Brewery, Brewery Type, NBeers, EstYear\n')
    fBeers.write('Continent, Country, Location, Brewery, id, Beer, Abv, Avg, Overall, StyleRt, NRatings\n')
    maxcounter = 0
    for i1, (continent, countries) in enumerate(beerContinents.iteritems(), 1):    #  Continents
        print i1, continent
        fConts.write(u'{}, "{}"\n'.format(i1, continent).encode('utf8'))
        for i2, (country, location) in enumerate(countries.iteritems(), 1):    #  Countries
            print i1, i2, location
            fCountries.write(u'{}, {}, "{}"\n'.format(i1, i2, country).encode('utf8'))
            for i3, (location, breweries) in enumerate(location.iteritems(), 1):    #  Locations
                #  print i1, i2, i3, location
                fLocs.write(u'{}, {}, {}, "{}"\n'.format(i1, i2, i3, location).encode('utf8'))
                for brewery, brewerInfo in breweries[1].iteritems():
                    #  print i1, i2, i3, brewerInfo[0], brewery, brewerInfo[1], brewerInfo[2], brewerInfo[3]
                    resposta = beerScraper.getSite('http://www.ratebeer.com/brewers/x/{}/'.format(brewerInfo[0]))
                    soup = bs4.BeautifulSoup(resposta)
                    """
                    brBase = soup.html.body.findChild('td', {'width':'85%'}).findChild('span', {'class': 'beerfoot'}).findChild('span', {'class': 'beerfoot'}).nextSibling.nextSibling.nextSibling
                    try:
                        assocPlace = brBase.text
                        assocURL = brBase.contents[0].attrs['href']
                        brURL = brBase.nextSibling.nextSibling.nextSibling.attrs['href']
                        brFcbk = brBase.nextSibling.nextSibling.nextSibling.nextSibling.attrs['href']"""
                    fBrewers.write(u'{}, {}, {}, {}, "{}", "{}", {}, {}\n'.format(i1, i2, i3, brewerInfo[0], brewery, brewerInfo[1], brewerInfo[2], brewerInfo[3]).encode('utf8'))
                    beers = brewerInfo[4]
                    brBase = soup.html.body.findChild('td', {'width': '85%'}).findChild('span', {'class': 'beerfoot'}).findChild('table', {'class': 'maintable nohover'})
                    for b in  brBase.findChildren('tr', {'class': 'dataTableRowAlternate'}):
                        beerData = processBeerRow(b)
                        if len(beerData):
                            beers[beerData[0]] = beerData[1:] + [{}]
                            fBeers.write(u'{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n'.format(
                                i1, i2, i3, brewerInfo[0], beerData[1], beerData[0], beerData[3], beerData[4], beerData[5], beerData[6], beerData[7]).encode('utf8'))
                    for b in  brBase.findChildren('tr', {'class': ''}):
                        beerData = processBeerRow(b)
                        if len(beerData):
                            beers[beerData[0]] = beerData[1:] + [{}]
                            fBeers.write(u'{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n'.format(
                                i1, i2, i3, brewerInfo[0], beerData[1], beerData[0], beerData[2], beerData[3], beerData[4], beerData[5], beerData[6]).encode('utf8'))
