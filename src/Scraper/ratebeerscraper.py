import bs4
import codecs
import cookielib
from django.core.management.commands import startproject
import os
import random
import socket
import time
import urllib2
from urlparse import urlparse

import socks


SCRAPER_CACHE_DIR = '/home/bobbruno/workspace/BeerApp/dumps/'


class Scraper(object):
    """
    Controls all the scraping for a particular website and its subsites.
    scrapeSite method should be overriden to manage navigation through
    the web pages.
    """
    @staticmethod
    def _createConnection(address, timeout=None, source_address=None):
        sock = socks.socksocket()
        sock.connect(address)
        return sock

    def __init__(self, sleepTime=5, maxTries=20,
                 useCache=True, clearCookies=False,
                 cacheDir='./', proxy='127.0.0.1',
                 proxyPort=9050, verbose=False, maxGets=None,
                 uaString='Your friendly neighbourhood spiderbot.'):
        """
        Constructor for the class.
        :param sleepTime: average time to sleep (in seconds) between calls.
               The scraper will wait a random amount of time based on that
               average after GETting each page.
        :type sleepTime: int
        :param maxTries: maximum number of retries before raising an exception.
               Defaults to 20.
        :type maxTries: int
        :param useCache: defines if the site should be cached or not.
               True by default
        :type useCache: bool
        :param clearCookies: Defines if the scraper should clear cookies
               before each access
        :type clearCookies: bool
        :param cacheDir: Directory where cached pages should be stored.
               Defaults to current directory
        :type cacheDir: str
        :param proxy: string address of the proxy website.
               Defaults to tor's default address.
        :type proxy: str
        :param proxyPort: Port number for the proxy.
               Defaults to tor's default port
        :type proxyPort: int
        :param verbose: Defines if the scraper should produce messages
               during its work or not. Defaults to false
        :type verbose: bool
        :param maxGets: if defined, sets a limit on the number of pages,
              after which the scraper will always fail.
        :type maxGets: int
        :param uaString: user-agent string
        :type uaString: str
        """
        self.sleepTime = sleepTime
        self.maxTries = maxTries
        self.useCache = useCache
        self.clearCookies = clearCookies
        self.cacheDir = cacheDir
        self.proxy = proxy
        self.proxyPort = proxyPort
        self.nGets = 0
        self.verbose = verbose
        self.maxGets = maxGets
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, self.proxy, self.proxyPort)
        socket.socket = socks.socksocket
        socket.create_connection = Scraper._createConnection
        socket.setdefaulttimeout(60)
        self.cj = cookielib.CookieJar()
        self.uaString = uaString

    def changeConnParms(self, sleepTime=None, maxTries=None, useCache=None,
                        clearCookies=None, cacheDir=None, proxy=None,
                        proxyPort=None, verbose=None, maxGets=None,
                        uaString=None):
        """
        Changes any of the connection parameters specified.
        :param sleepTime: average time to sleep (in seconds) between calls.
               The scraper will wait a random amount of time based on that
               average after GETting each page.
        :type sleepTime: int
        :param maxTries: maximum number of retries before raising an exception.
        :type maxTries: int
        :param useCache: defines if the site should be cached or not.
        :type useCache: bool
        :param clearCookies: Defines if the scraper should clear cookies
               before each access
        :type clearCookies: bool
        :param cacheDir: Directory where cached pages should be stored.
        :type cacheDir: str
        :param proxy: string address of the proxy website.
        :type proxy: str
        :param proxyPort: Port number for the proxy.
        :type proxyPort: int
        :param verbose: Defines if the scraper should produce messages
               during its work or not.
        :type verbose: bool
        :param maxGets: if defined, sets a limit on the number of pages,
              after which the scrapDefaults to tor's default porter will always fail.
        :type maxGets: int
        :param uaString: user-agent string
        :type uaString: str
        """
        if (sleepTime is not None):
            self.sleepTime = sleepTime
        if (maxTries is not None):
            self.maxTries = maxTries
        if (useCache is not None):
            self.useCache = useCache
        if (clearCookies is not None):
            self.clearCookies = clearCookies
        if (cacheDir is not None):
            self.cacheDir = cacheDir
        if (proxy is not None):
            self.proxy = proxy
        if (proxyPort is not None):
            self.proxyPort = proxyPort
        if (verbose is not None):
            self.verbose = verbose
        if (maxGets is not None):
            self.maxGets = maxGets
        if (uaString is not None):
            self.uaString = uaString

    def login(self, user='', password='', loginPage=None, loginForm=None,
               startPage=None,):
        """
        Login method for the scraper.
        :param user: Username to be used for login
        :type user: str
        :param password: password for that user
        :type password: str
        :param loginPage: URL of the login page
        :type loginPage: str
        :param loginForm: name of the Form object to look for
        :type loginForm: str
        :param startPage: URL of an optional starting page to navigate
               from, simulating a real user.
        :type startPage: str
        """
        self.user = user
        self.password = password
        #  First, let's go to the initial page, if it's there
        if (startPage is not None):
            self._getSitePure(startPage)
        text = self._getSitePure(loginPage)


    def beforeFirst(self):
        """
        Gets called before the first call to getSite(). Should deal with
        logins, etc.
        This method should be overriden by any descendants.
        """
        pass

    def _getSitePure(self, site):
        """
        Gets a site directly, with no caching whatsoever
        :param site: URL of the site that is to be downloaded
        :type site: str
        :rtype str
        """
        tryCounter = 0
        while True:
            try:
                self.nGets += 1
                request = urllib2.Request(site)
                request.add_header('User-Agent', self.uaString)
                if self.clearCookies:
                    self.cj.clear()
                opener = urllib2.build_opener(
                    urllib2.HTTPCookieProcessor(self.cj))
                if self.verbose:
                    print('Calling open on {}').format(request.get_full_url())
                retVal = opener.open(request)
                time.sleep(random.expovariate(1 / float(self.sleepTime)))
                theHTML = retVal.read()
            except Exception, e:
                tryCounter += 1
                if self.verbose:
                    print 'Getting {} did not work ({})'.format(site, str(e))
                    if (tryCounter >= self.maxTries // 2):
                        request = urllib2.Request('http://checkip.dyndns.com/')
                        request.add_header('User-Agent',
                            'Your friendly neighborhood spider-man.')
                        opener = urllib2.build_opener(
                            urllib2.HTTPCookieProcessor())
                        retVal = opener.open(request, timeout=60)
                        theHTML = retVal.read()
                        print 'Checking: {}'.format(theHTML)
                if (tryCounter >= self.maxTries):
                    if self.verbose:
                        print 'Could not get {}: Error {}'.format(site, str(e))
                    raise e
                else:
                    time.sleep(random.expovariate(1 / float(self.sleepTime)))
                    continue
            else:
                break
        return theHTML

    def getSite(self, site):
        '''
        Returns the HTML of the site requested. Raises an exception if more
        than maxTries attempts are made and the site cannot be recovered.
        :param site: Site URL
        :type site: str
        :rtype str
        '''
        if self.verbose:
            print 'getting {}\n'.format(site)

        if self.useCache:
            parsedURL = urlparse(site)
            path = parsedURL.path
            if (path == ''):
                path = 'INDEX'
            if (path[0] == '/'):
                path = path[1:]
            if (path[-1] == '/'):
                path = '{}INDEX'.format(path)
            dirPath = os.path.split(path)[0]
            cacheDir = os.path.join(self.cacheDir, parsedURL.netloc, dirPath)
            cacheFile = os.path.join(self.cacheDir, parsedURL.netloc, path)
            if os.path.isfile(cacheFile):
                inputStream = codecs.open(cacheFile, 'r', encoding='utf8')
                html = inputStream.readlines()
                inputStream.close()
                return u''.join(html)
            else:
                theHTML = self._getSitePure(site)
                if not os.path.exists(cacheDir):
                    os.makedirs(cacheDir)
                fstream = codecs.open(cacheFile, 'w', encoding='utf8')
                fstream.write(theHTML.decode('latin-1'))
                fstream.close()
        else:
            theHTML = self._getSitePure(site)
        return theHTML

    def getSiteCollection(self, siteCol):
        """
        Gets a collection of sites passed to it. Returns a dictionary
        of {id: html} for pages successfully recovered. If a page in the
        original collection cannot be recovered, it won't be on the
        returned dictionary.
        :param siteCol: dictionary of sites to be recovered,
            formatted as {id: URL}.Id can be any type acceptable
            as a dictionary key.
        :type siteCol: dict
        :rtype dict
        """
        sites = {}
        for key, url in siteCol.iteritems():
            try:
                theHTML = self.getSite(url)
            except:
                continue
            else:
                sites[key] = theHTML
        return sites



#  First, let's get the locations
#  This code captures all the countries and country subdivisions
#  which have known breweries

beerScraper = Scraper()

resposta = getSite('http://www.ratebeer.com/breweries/')
soup = bs4.BeautifulSoup(resposta)
breweries = soup.html.body.findChild(id='brewerCover').next_sibling.next_sibling    #  @IgnorePep8

beerContinents = {}
bigCountry = ''
for i in breweries.children:
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

