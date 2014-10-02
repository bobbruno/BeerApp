#!/usr/bin/env python
#  encoding: utf-8
'''
Modeler.DBLoad -- Loads the Continents, Countries, Locations, Breweries, Beers and Ratings to the database, then generates the Users, Glasses and Styles tables.

Modeler.DBLoad is a main program for loading csv generated by Scraper.ratebeerscraper into a Postgres database. It expects to get a path and a destination tablespace
from the command line (--help for option syntax). Then it will try to load

It defines classes_and_methods

@author:     Roberto Bruno Martins

@copyright:  2014 Wu Wei Ltda. All rights reserved

@license:    unlicensed

@contact:    bobbruno@gmail.com
@deffield    updated: September 25th, 2014
'''

from __builtin__ import int
import csv
from optparse import OptionParser
import os
import psycopg2
import psycopg2.extras
import sys

from Scraper.Parser import Continent, Country, Location, Brewery, Beer, City, \
    UserRating

from Modeler.dbBridge import dbContinent, dbCountry, dbLocation, dbBrewery, \
    dbBeer, dBRating


__all__ = []
__version__ = 0.1
__date__ = '2014-09-25'
__updated__ = '2014-10-02'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

INTERV_MSG = 1000

def nvl(x, toType):
    if type(x) == str and x == 'None':
        return None
    else:
        return toType(x)

def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    #  program_usage = '''usage: spam two eggs''' # optional - will be autogenerated by optparse
    program_longdesc = ''''''    #  optional - give further explanation about what the program does
    program_license = "Copyright 2014 user_name (organization_name)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

    if argv is None:
        argv = sys.argv[1:]
    try:
        #  setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-i", "--input", dest="inFile", default="./", help="set input path [default: %default]", metavar="PATH")
        parser.add_option("-H", "--host", dest="host", default="localhost", help="set host name of database [default: %default]", metavar="HOST")
        parser.add_option("-p", "--port", dest="port", default=5432, help="set connection port of database [default: %default]", metavar="PORT")
        parser.add_option("-d", "--destDB", dest="destDb", default="BeerDb", help="set destination Database [default: %default]", metavar="DB")
        parser.add_option("-v", "--verbose", dest="verbose", action="count", default=0, help="set verbosity level [default: %default]")
        parser.add_option("-t", "--truncate", dest="truncate", action="store_true", default=True, help="truncate tables on the destination tablespace ? [default: %default]")
        parser.add_option("-U", "--user", dest="userName", action="store", default="BeerApp", help="set username for connecting to the database [default: %default]", metavar="LOGIN")
        parser.add_option("-P", "--password", dest="password", action="store", help="set password for connecting to the database", metavar="PASSWD")
        parser.add_option("-e", "--error-level", dest="errorLevel", action="store", default=0, help="set error level [default: %default]")

        #  process options
        (opts, args) = parser.parse_args(argv)

        if opts.verbose > 0:
            print("verbosity level = %d" % opts.verbose)
        if opts.truncate:
            print("truncate is ON")
        else:
            print("truncate is OFF")
        if opts.inFile:
            print("infile = %s" % opts.inFile)
        if opts.destDb:
            print("destination DB = %s" % opts.destDb)

        conn = psycopg2.connect(database=opts.destDb, user=opts.userName,
                                password=opts.password, host=opts.host,
                                port=opts.port, cursor_factory=psycopg2.extras.DictCursor)

        Conts = dbContinent(conn, opts.truncate)
        Countries = dbCountry(conn, Conts, opts.truncate)
        Locations = dbLocation(conn, Countries, opts.truncate)
        Breweries = dbBrewery(conn, Locations, opts.truncate)
        Beers = dbBeer(conn, Breweries, opts.truncate)
        Ratings = dBRating(conn, Beers, opts.truncate)

        #  Load continents
        print 'Loading continents...'
        with open(opts.inFile + 'continents.csv', 'r') as fCont:
            reader = csv.reader(fCont, quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True)
            try:
                row = reader.next()
            except ValueError:
                pass
            for row in reader:
                if row[0] == 'id':
                    continue
                theCont = Continent(int(row[0]), row[1])
                Conts[theCont.id] = theCont
        print '{} records loaded.\n'.format(len(Conts))

        #  Load countries
        print 'Loading countries...'
        with open(opts.inFile + 'countries.csv', 'r') as fCont:
            reader = csv.reader(fCont, quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True)
            try:
                row = reader.next()
            except ValueError:
                pass
            for row in reader:
                if row[0] == 'Continent':
                    continue
                theCountry = Country(Conts[int(row[0])], int(row[1]), row[2])
                Countries[theCountry.id] = theCountry
        print '{} records loaded.\n'.format(len(Countries))

        #  Load Locations
        print 'Loading locations...'
        with open(opts.inFile + 'locations.csv', 'r') as fLoc:
            reader = csv.reader(fLoc, quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True)
            try:
                row = reader.next()
            except ValueError:
                pass
            for row in reader:
                if row[0] == 'Continent':
                    continue
                theLocation = Location(Countries[int(row[1])], int(row[2]), row[3], '')
                Locations[theLocation.id] = theLocation
        print '{} records loaded.\n'.format(len(Locations))

        #  Load Breweries
        print 'Loading breweries...'
        with open(opts.inFile + 'breweries.csv', 'r') as fLoc:
            reader = csv.reader(fLoc, quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True)
            try:
                row = reader.next()
            except ValueError:
                pass
            for i, row in enumerate(reader, 0):
                if row[0] == 'Continent':
                    continue
                theBrewery = Brewery(Locations[int(row[2])], int(row[3]), row[4], row[5], int(row[6]), int(row[7]), '')
                Breweries[theBrewery.id] = theBrewery
                if not i % INTERV_MSG and i:
                    print "{} records saved...".format(i)
            else:
                conn.commit()
                print '{} records loaded.\n'.format(i)


        #  Load Beers
        print 'Loading beers...'
        with open(opts.inFile + 'beers.csv', 'r') as fLoc:
            reader = csv.reader(fLoc, quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True)
            try:
                row = reader.next()
            except ValueError:
                pass
            for i, row in enumerate(reader, 0):
                #  Continent,Country,Location,Brewery,BeerId,BeerName,BeerStyle,"Style Name",CityId,CityName,ABV,IBU,NCals,AvailBottle,AvailTap,Seasonal,OveralllRating,BayesianAvg,StyleRating,NRatings
                if row[0] == 'Continent':
                    continue
                #  TODO: Since I haven't written info on distribution scope or glasses, I'm writing them as blanks here.
                try:
                    theBeer = Beer(int(row[4]), row[5], Breweries[int(row[3])], '', int(row[6]), row[7], nvl(row[10], float),
                                   nvl(row[11], int), nvl(row[12], float), [], nvl(row[17], float), nvl(row[16], float),
                                   nvl(row[18], float), nvl(row[19], float), City(nvl(row[8], int), row[9]), row[13] == 'True',
                                   row[15], row[14] == 'True', '')
                    Beers[theBeer.id] = theBeer
                except Exception as e:
                    print row
                    print e
                if not i % INTERV_MSG and i:
                    print "{} records saved...".format(i)
            else:
                conn.commit()
                print '{} records loaded.\n'.format(i)

        #  Load Ratings
        print 'Loading ratings...'
        with open(opts.inFile + 'ratings.csv', 'r') as fLoc:
            reader = csv.reader(fLoc, quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True)
            try:
                row = reader.next()
            except ValueError:
                pass
            for i, row in enumerate(reader, 0):
                #  BeerId,userId,"userName",compound,aroma,appearance,taste,palate,overall,"location","date","notes"
                try:
                    if row[0] == 'BeerId':
                        continue
                    theRating = UserRating(Beers[int(row[0])], int(row[1]), row[2], float(row[3]),
                                           int(row[4]), int(row[5]), int(row[6]), int(row[7]), int(row[8]),
                                           row[9], row[10], row[11])
                    Ratings.append(theRating)
                except Exception as e:
                    print row
                    print e
                    raise
                if not i % INTERV_MSG and i:
                    print "{} records saved...".format(i)
            else:
                conn.commit()
                print '{} records loaded.'.format(i)

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        raise    #  return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'Modeler.DBLoad_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
