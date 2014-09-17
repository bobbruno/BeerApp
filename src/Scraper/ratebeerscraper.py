#!/usr/bin/env python
#  -*- coding: utf-8 -*-from __builtin__ import str

import bs4
import itertools
import math
import os
import sys
from timeit import itertools

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


def robustConv(x, toType=float):
    """
    Converts an object to another type. Will return None when conversion fails.
    :param x: the object to be converted
    :param type toType: the type to convert to
    """
    try:
        y = toType(x)
    except ValueError:
        y = None
    finally:
        return y


class Parser(object):
    """
    Class for parsing the html data
    """
    def __init__(self, scraper, loc=SCRAPER_CACHE_DIR, initFiles=True, verbose=False):
        """
        Constructor for the class
        :param Scraper scraper: scraper to use to get the site pages
        :param str fLocation: location to create the csv files
        :param bool initFiles: Should the csv files be initialized ?
        :param bool verbose: Should the progress be printed ?
        """
        self.fLocation = loc
        self.scraper = scraper
        self.verbose = verbose
        if initFiles:
            self.initializeFiles()

    def initializeFiles(self):
        """
        Initializes all the csv files, deleting whatever was there and creating just headers for all of them.
        """
        with open('{}/continents.csv'.format(self.fLocation), 'w') as fConts:
            fConts.write('id, Continent\n')
        with open('{}/countries.csv'.format(self.fLocation), 'w') as fCountries:
            fCountries.write('Continent, id, Country\n')
        with open('{}/locations.csv'.format(self.fLocation), 'w') as fLocs:
            fLocs.write('Continent, Country, id, Location\n')
        with open('{}/breweries.csv'.format(self.fLocation), 'w') as fBrewers:
            fBrewers.write('Continent, Country, Location, id, Brewery, Brewery Type, NBeers, EstYear\n')
        with open('{}/beers.csv'.format(self.fLocation), 'w') as fBeers:
            fBeers.write(('Continent, Country, Location, Brewery, '
                          'id, Beer, Abv, Avg, Overall, StyleRt, NRatings\n'))

    def parseBeers(self, continent, country, location, brewer, brewerPage):
        """
        Processes the beer information and returns a dict
        of beers from that brewer.
        :param int continent: continent id
        :param int country: country id
        :param int location: location id
        :param int brewer: brewer id
        :param bs4.Tag brewerPage: beer table from Brewer's page
        :rtype dict
        """
        def processBeerHTML(tag):
            """
            Gets a Tag object with a full row of beer data and returns all
            info on that beer as a list:
                0: Beer name
                1: Beer id
                2: beer URL
                3: abv
                4: avg
                5: overall
                6: style rating
                7: # of ratings
            :param bs4.Tag tag: tag pointing to the line of data about the beer
            :rtype list
            """
            if tag.findChild('span', {'class': 'rip'}) is not None:
                return []
            retVal = []
            try:
                retVal = [tag.contents[0].contents[1].text]
                beerURL = tag.contents[0].contents[1].attrs['href']
                retVal.append(beerURL.split('/')[-2])
                retVal.append(beerURL)
                retVal.append(robustConv(tag.contents[2].text))
                retVal.append(robustConv(tag.contents[3].text))
                retVal.append(robustConv(tag.contents[4].text))
                retVal.append(robustConv(tag.contents[5].text))
                retVal.append(robustConv(tag.contents[6].text))
                retVal.append(robustConv(tag.contents[7].text))
            except:
                pass
            return retVal

        beers = {}
        with open('{}/beers.csv'.format(self.fLocation), 'a') as fBeers:
            for b in itertools.chain(brewer.findChildren('tr',
                                     {'class': 'dataTableRowAlternate'}),
                                     brewer.findChildren('tr',
                                     {'class': ''})):
                beerData = processBeerHTML(b)
                if len(beerData):
                    beers[beerData[0]] = beerData[1:] + [{}]
                    fBeers.write((u'{continent}, {country}, {location}'
                                  u', {brewery}, {bId}, "{bName}", '
                                  u'{bAbv}, {bAvg}, {bOverall}, '
                                  u'{bStyleRt}, {bNRatings}\n').format(
                        continent=continent, country=country,
                        location=location, brewery=brewer,
                        bId=beerData[1], bName=beerData[0], bAbv=beerData[3],
                        bAvg=beerData[4], bOverall=beerData[5],
                        bStyleRt=beerData[6],
                        bNRatings=beerData[7]).encode('utf8'))
        return beers

    def parseBreweries(self, continent, country, location, locPage):
        """
        Processes the brewer table from the location and returns a dict
        of brewers from that location.
        :param int continent: continent id
        :param int country: country id
        :param int location: location id
        :param bs4.Tag locPage: brewer table from location's page
        :rtype dict
        """
        breweries = {}
        with open('{}/breweries.csv'.format(self.fLocation), 'a') as fBrewers:
            for bTabLin in locPage.childGenerator():
                #  Process the brewery table row
                frCol = bTabLin.findChild()
                brewerHTML = frCol.findChild()
                brewery = brewerHTML.text
                if self.verbose:
                    print u'\t\t\t Processing {}'.format(brewery).encode('utf8')
                brType = frCol.findNextSibling()
                brNBeer = brType.findNextSibling()
                brEstDate = int(brNBeer.findNextSibling().findNextSibling().text)    #  @IgnorePep8
                brewerInfo = [int(brewerHTML.attrs['href'][9:].split('/')[1]),
                    brType.text, int(brNBeer.text), int(brEstDate)]
                if self.verbose:
                    print continent, country, location, brewerInfo[0], brewery, brewerInfo[1], brewerInfo[2], brewerInfo[3]
                #  Now let's go to the brewer's page
                response = self.scraper.getSite(
                    'http://www.ratebeer.com/brewers/x/{}/'.format(brewerInfo[0]))
                soup = bs4.BeautifulSoup(response).html.body
                #  FIXME: This code must be improved to deal with the possibility that only part of the information is available, and that part changes
                """
                brBase = soup.html.body.findChild('td', {'width':'85%'}).findChild('span', {'class': 'beerfoot'}).findChild('span', {'class': 'beerfoot'}).nextSibling.nextSibling.nextSibling
                try:
                    assocPlace = brBase.text
                    assocURL = brBase.contents[0].attrs['href']
                    brURL = brBase.nextSibling.nextSibling.nextSibling.attrs['href']
                    brFcbk = brBase.nextSibling.nextSibling.nextSibling.nextSibling.attrs['href']"""
                try:
                    brBase = soup.findChild('td', {'width': '85%'}).findChild('span', {'class': 'beerfoot'}).findChild('table', {'class': 'maintable nohover'})
                    beers = self.parseBeers(continent, country, location,
                                            brewerInfo[0], brBase)
                    breweries[brewery] = brewerInfo + [beers]
                    fBrewers.write(u'{},{},{},{},"{}","{}",{},{}\n'.format(
                        continent, country, location, brewerInfo[0],
                        brewery, brewerInfo[1], brewerInfo[2],
                        brewerInfo[3]).encode('utf8'))
                except AttributeError:    #  Probably a brewer no longer in the database, move on to the next
                    continue
        return breweries

    def parseLocations(self, initPage):
        """
        Parse the inicial locations page, returning everythin as a dictionary.
        :param Scraper scraper: the scraper to use to parse eacho location's page
        :param bs4.Tag initPage: the recovered page to be parsed.
        :rtype dict
        """
        beerContinents = {}
        bigCountry = ''
        nConts, nCountries, nLocs = -1, -1, -1
        with open('{}/continents.csv'.format(self.fLocation), 'a') as fConts, \
             open('{}/countries.csv'.format(self.fLocation), 'a') as fCountries, \
             open('{}/locations.csv'.format(self.fLocation), 'a') as fLocs:
            for i in initPage.children:
                if (type(i) == bs4.element.Tag):    #  Found a continent
                    if (i.name == u'div'):
                        currContinent = i.text
                        if self.verbose:
                            print u'Breweries from {}'.format(currContinent).encode('utf8')
                        nConts += 1
                        fConts.write(u'{}, "{}"\n'.format(nConts, currContinent).encode('utf8'))
                        beerContinents[currContinent] = {}
                        bigCountry = ''
                    elif (i.name == u'a'):    #  Found a country, which may have subregions
                        country = bigCountry if len(bigCountry) else i.text
                        if (country not in beerContinents[currContinent]):
                            if self.verbose:
                                print u'\tBreweries from {}'.format(country).encode('utf8')
                            nCountries += 1
                            fCountries.write(u'{}, {}, "{}"\n'.format(nConts, nCountries, country).encode('utf8'))
                            beerContinents[currContinent][country] = {}
                        locPage = i.attrs['href'][11:]
                        if self.verbose:
                            print u'\t\tBreweries from {}'.format(i.text).encode('utf8')
                        response = self.scraper.getSite('http://www.ratebeer.com/breweries/{}'.format(locPage))
                        soup = bs4.BeautifulSoup(response).html.body
                        nLocs += 1
                        fLocs.write(u'{}, {}, {}, "{}"\n'.format(nConts, nCountries, nLocs, i.text).encode('utf8'))
                        beerContinents[currContinent][country][i.text] = [locPage] + \
                            [self.parseBreweries(currContinent, country, i.text,
                                    soup.findChild(id='brewerTable').findChild('tbody'))]
                elif (type(i) == bs4.element.NavigableString and
                      len(i.strip()) > 0 and len(i.strip()) < 40):
                    bigCountry = i.strip()
        return beerContinents

beerScraper = Scraper(sleepTime=3, cacheDir=SCRAPER_CACHE_DIR, verbose=True, uaString=uaS[0])
beerParser = Parser(scraper=beerScraper)

beerScraper.login(accounts[0][0], accounts[0][2],
                  'http://www.ratebeer.com/login.asp',
                  'signin', 'http://www.ratebeer.com')

resposta = beerScraper.getSite('http://www.ratebeer.com/breweries/')
soup = bs4.BeautifulSoup(resposta)
locPage = soup.html.body.findChild(id='brewerCover').next_sibling.next_sibling    #  @IgnorePep8

beerData = beerParser.parseLocations(locPage)

#  Now let's get some beers from a brewery
#  I can get:
#  Associated place: <span class="beerfoot"></span>.
#  nextSibling.nextSibling.firstChild: get href and text
#  website: from previous last sibling, nextSibling.firstChild:get href and text
#  facebook,
#  email
#  The beer list with:
#     Beer name, abv, avg/5 overall, stype, ratings

