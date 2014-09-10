import bs4
from itertools import cycle
import mechanize
import random
import socket
import time

import socks


PROXY_LIST = ['107.182.16.221:7808',
'111.185.187.226:8088',
'112.104.120.38:8088',
'162.208.49.45:7808',
'177.36.8.99:80',
'186.92.77.157:8080',
'190.205.5.28:8080',
'192.227.146.119:3127',
'199.200.120.140:3127',
'199.200.120.36:3127',
'201.243.114.46:8080',
'217.112.131.63:7808',
'37.239.46.26:80',
'58.114.235.62:8088',
'61.7.149.69:8080',
'66.85.131.18:7808',
'85.120.159.1:8000',
'186.91.92.227:8080',
'111.254.184.31:8088',
'162.243.135.237:3128',
'76.164.213.124:7808',
'103.25.203.227:3127',
'111.255.115.98:8088',
'190.36.170.52:8080',
'200.84.80.254:8080',
'111.252.243.67:8088',
'111.254.105.57:8088',
'190.78.120.250:8080',
'200.84.110.80:8080',
'58.115.107.71:8088',
'190.204.111.143:8080',
'200.84.129.69:8080',
'201.211.162.46:8080',
'61.57.93.194:8088',
'177.75.42.33:8080',
'183.178.176.226:8088',
'111.252.249.220:8088',
'111.254.164.81:8088',
'114.27.224.168:8088',
'111.255.108.178:8088',
'114.39.221.21:8088',
'119.46.91.234:80',
'186.89.242.248:8080',
'186.91.126.80:8080',
'192.3.17.220:8080',
'201.249.22.107:8080',
'23.251.149.27:80',
'111.252.130.124:8088',
'111.252.179.223:8088',
'111.255.34.219:8088',
]

prxyGen = cycle(PROXY_LIST)
prxy = None

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

nGets = 0

def getSite(br, site):
    '''
    Downloads a site through a proxy (different one each time) and up to 100 retries. This should
    probably by a descendant of mechanize.Browser() 
    :param br: mechanize.Browser
    :param site: str
    '''

    print 'getting {}\n'.format(site)
    global nGets
    tryCounter = 0
    time.sleep(random.expovariate(1 / 7.))
    while True:
        try:
            br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; rv:27.3) Gecko/20130101 Firefox/27.3')]
            br._ua_handlers['_cookies'].cookiejar.clear_session_cookies()
            nGets += 1
            return br.open(site, timeout=30)
        except Exception, e:
            tryCounter += 1
            print 'Getting {} did not work ({})'.format(site, str(e))
            if tryCounter >= 20:
                print 'Could not get {} through any proxy: Error {}'.format(site, str(e))
                raise e
            else:
                continue
        else:
            break

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
#  patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection

br = mechanize.Browser()

#  First, let's get the locations
#  This code captures all the countries and country subdivisions which have known breweries

getSite(br, 'http://www.ratebeer.com/breweries/')
soup = bs4.BeautifulSoup(br.response().read())
breweries = soup.html.body.findChild(id='brewerCover').next_sibling.next_sibling

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
            if (not beerContinents[currContinent].has_key(country)):
                beerContinents[currContinent][country] = {}
            beerContinents[currContinent][country][i.text] = [i.attrs['href'][11:], {}]
    elif (type(i) == bs4.element.NavigableString and len(i.strip()) > 0 and len(i.strip()) < 40):
        bigCountry = i.strip()

#  This code captures the breweries for a list of locations for a specific continent and country
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
                    getSite(br, u'http://www.ratebeer.com/breweries/{}'.format(breweries[subURL]))
                except:
                    retryList3[location] = {}
                    continue
                soup = bs4.BeautifulSoup(br.response().read())
                for bTabLin in soup.html.body.findChild(id='brewerTable').findChild('tbody').childGenerator():
                    firstColumn = bTabLin.findChild()
                    brewer = firstColumn.findChild()    #  .text, .attrs['href'] - I only need the digits in the end
                    print u'\t\t\t Processing {}'.format(brewer.text)
                    brewerType = firstColumn.findNextSibling()    #  .text
                    brewerNBeers = brewerType.findNextSibling()    #  Can't get text only, need the object for next nav
                    brewerEstDate = int(brewerNBeers.findNextSibling().findNextSibling().text)
                    breweries[brewer.text] = [brewer.attrs['href'][9:].split('/')[1],
                                    brewerType.text, int(brewerNBeers.text), brewerEstDate, {}]
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

