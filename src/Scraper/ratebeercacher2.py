#!/usr/bin/env python
#  -*- coding: utf-8 -*-from __builtin__ import str

import cProfile
import pstats

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


beerScraper = Scraper(sleepTime=3, cacheDir=SCRAPER_CACHE_DIR, verbose=True, uaString=uaS[3])
beerParser = Parser(scraper=beerScraper, loc=SCRAPER_CACHE_DIR + 'dummy2/')
beerParser.limitCountries(set([u'England', u'Ireland', u'Other United Kingdom', u'Belgium', u'Germany', u'United States']))
beerParser.limitContinents(set([u'North America']))
beerParser.limitLocations(set([u'New Jersey', u'New Mexico', u'New York', u'North Carolina', u'North Dakota',
                               u'Ohio', u'Oklahoma', u'Oregon', u'Pennsylvania', u'Rhode Island', u'South Dakota',
                               u'Tennessee', u'Texas', u'Utah', u'Vermont', u'Virginia', u'Washington', u'Washington DC',
                               u'West Virginia', u'Wisconsin', u'Wyoming']))

beerScraper.login(accounts[2][0], accounts[2][2],
                  'http://www.ratebeer.com/login.asp',
                  'signin', 'http://www.ratebeer.com')
profile_filename = 'Modeler.DBLoad_profile.txt'
cProfile.run('beerParser.parseContinents("http://www.ratebeer.com/breweries/")', profile_filename)
statsfile = open("profile_stats.txt", "wb")
p = pstats.Stats(profile_filename, stream=statsfile)
stats = p.strip_dirs().sort_stats('cumulative')
stats.print_stats()
statsfile.close()

#  Now let's get some beers from a brewery
#  I can get:
#  Associated place: <span class="beerfoot"></span>.
#  nextSibling.nextSibling.firstChild: get href and text
#  website: from previous last sibling, nextSibling.firstChild:get href and text
#  facebook,
#  email
#  The beer list with:
#     Beer name, abv, avg/5 overall, stype, ratings
