import bs4
import codecs
import os
import random
import socket
import time
import urllib2
from urlparse import urlparse

import socks


def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

nGets = 0
useCache = True
SCRAPER_CACHE_DIR = '/home/bobbruno/workspace/BeerApp/dumps/'


def getSite(site):
    '''
    Downloads a site through a proxy (different one each time) and up to
    100 retries.
    :param site: str Site URL
    :rtype: str HTML
    '''

    print 'getting {}\n'.format(site)
    parsedURL = urlparse(site)
    path = parsedURL.path
    if (path == ''):
        path = 'INDEX'
    if (path[0] == '/'):
        path = path[1:]
    if (path[-1] == '/'):
        path = '{}INDEX'.format(path)
    dirPath = os.path.split(path)[0]
    cacheDir = os.path.join(SCRAPER_CACHE_DIR, parsedURL.netloc, dirPath)
    cacheFile = os.path.join(SCRAPER_CACHE_DIR, parsedURL.netloc, path)

    if useCache:
        if os.path.isfile(cacheFile):
            inputStream = codecs.open(cacheFile, 'r', encoding='utf8')
            html = inputStream.readlines()
            inputStream.close()
            return u''.join(html)
        else:
            global nGets
            tryCounter = 0
            time.sleep(random.expovariate(1 / 7.))
            while True:
                try:
                    nGets += 1
                    request = urllib2.Request(site)
                    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:27.3) Gecko/20130101 Firefox/27.3')
                    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
                    retVal = opener.open(request, timeout=30)
                    theHTML = retVal.read()
                    if useCache:
                        if not os.path.exists(cacheDir):
                            os.makedirs(cacheDir)
                        fstream = codecs.open(cacheFile, 'w', encoding='utf8')
                        fstream.write(theHTML.decode('latin-1'))
                        fstream.close()
                    return theHTML
                except Exception, e:
                    tryCounter += 1
                    print 'Getting {} did not work ({})'.format(site, str(e))
                    if tryCounter >= 20:
                        print 'Could not get {}: Error {}'.format(site, str(e))
                        raise e
                    else:
                        continue
                else:
                    break

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
#  patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection

#  First, let's get the locations
#  This code captures all the countries and country subdivisions
#  which have known breweries

resposta = getSite('http://www.ratebeer.com/breweries/')
soup = bs4.BeautifulSoup(resposta)
breweries = soup.html.body.findChild(id='brewerCover').next_sibling.next_sibling    #  @IgnorePep8

beerContinents = {}
bigCountry = ''
for i in breweries.children:
    if (type(i) == bs4.element.Tag):
        if (i.name == u'div'):
            currContinent = i.text
            beerContinents[currContinent] = {}
            bigCountry = ''
        elif (i.name == u'a'):
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
                    resposta = getSite('http://www.ratebeer.com/breweries/{}'.format(breweries[subURL]))    #  @IgnorePep8
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
                    breweries[brewer.text] = [brewer.attrs['href'][9:].split('/')[1],
                                    brType.text, int(brNBeer.text), brEstDate, {}]
                if (nGets > 100):
                    break
            if len(retryList3):
                retryList2[country] = retryList3.copy()
            if (nGets > 100):
                break
        if len(retryList2):
            retryList1[continent] = retryList2.copy()
        if (nGets > 100):
            runs = 21
            break

    runList = retryList1.copy()
    runs += 1

with open('/home/bobbruno/workspace/BeerApp/dumps/continents.csv', 'w') as fconts, \
    open('/home/bobbruno/workspace/BeerApp/dumps/countries.csv', 'w') as fcountries, \
    open('/home/bobbruno/workspace/BeerApp/dumps/locations.csv', 'w') as flocs, \
    open('/home/bobbruno/workspace/BeerApp/dumps/breweries.csv', 'w') as fbrewers:
        fconts.write('id, Continent\n')
        fcountries.write('Continent, id, Country\n')
        flocs.write('Continent, Country, id, Location\n')
        fbrewers.write('Continent, Country, Location, id, Brewery, Brewery Type, NBeers, EstYear\n')
        maxcounter = 0
        for i1, (continent, countries) in enumerate(beerContinents.iteritems(), 1):    #  Continents
            if maxcounter >= 100:
                break
            print i1, continent
            fconts.write(u'{}, "{}"\n'.format(i1, continent).encode('utf8'))
            for i2, (country, location) in enumerate(countries.iteritems(), 1):    #  Countries
                print i1, i2, location
                fcountries.write(u'{}, {}, "{}"\n'.format(i1, i2, country).encode('utf8'))
                for i3, (location, breweries) in enumerate(location.iteritems(), 1):    #  Locations
                    print i1, i2, i3, location
                    flocs.write(u'{}, {}, {}, "{}"\n'.format(i1, i2, i3, location).encode('utf8'))
                    for brewery, brewerInfo in breweries.iteritems():
                        print i1, i2, i3, brewerInfo[0], brewery, brewerInfo[1], brewerInfo[2], brewerInfo[3]
                        fbrewers.write(u'{}, {}, {}, {}, "{}", "{}", {}, {}\n'.format(
                            i1, i2, i3, brewerInfo[0], brewery, brewerInfo[1], brewerInfo[2], brewerInfo[3]).encode('utf8'))
                        maxcounter += 1

