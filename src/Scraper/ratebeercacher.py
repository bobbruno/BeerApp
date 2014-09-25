#!/usr/bin/env python
#  -*- coding: utf-8 -*-from __builtin__ import str

from Parser import Parser
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


beerScraper = Scraper(sleepTime=3, cacheDir=SCRAPER_CACHE_DIR, verbose=True, uaString=uaS[2])
beerParser = Parser(scraper=beerScraper, loc=SCRAPER_CACHE_DIR + 'dummy/')
beerParser.limitCountries(set([u'England', u'Ireland', u'Other United Kingdom', u'Belgium', u'Germany', u'United States']))
beerParser.limitContinents(set([u'Europe']))

beerScraper.login(accounts[1][0], accounts[1][2],
                  'http://www.ratebeer.com/login.asp',
                  'signin', 'http://www.ratebeer.com')

beerData = beerParser.parseContinents('http://www.ratebeer.com/breweries/')

#  Now let's get some beers from a brewery
#  I can get:
#  Associated place: <span class="beerfoot"></span>.
#  nextSibling.nextSibling.firstChild: get href and text
#  website: from previous last sibling, nextSibling.firstChild:get href and text
#  facebook,
#  email
#  The beer list with:
#     Beer name, abv, avg/5 overall, stype, ratings
