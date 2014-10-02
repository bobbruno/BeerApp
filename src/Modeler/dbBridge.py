'''
dbContinent: database bridge between Continent and Postgresql
Created on 25/09/2014

@author: Roberto Bruno Martins
'''

import psycopg2

from Parser import Brewery
from Scraper.Parser import Continent, Country, Location, Beer, City, UserRating


#  TODO: Review this code. If I used currItem instead of currCont, currCountry, etc, I could probably have much simpler objects.
#  >>>>>>>>>>>>>>>>>>>>>>>>>Already did that for dBBeer and dBBrewery

class DuplicateValue(Exception):
    def __init__(self, id, objType, name, origName=None):
        self.id = id
        self.objType = objType
        self.name = name
        self.origName = origName

    def __str__(self):
        return u'Duplicate {} value: Id {} assigned to "{}" is already assigned to "{}'.format(self.objType, self.id, self.name, self.origName)


class dbContinent(dict):
    '''
    Generates a python dict representation of continents table in the database.
    '''

    def __init__(self, dB, truncate=False, persist=True, upSert=True, *args):
        """ Initializes the manager for a tb_continent table (which behaves as a collection of continents as well).
        :param dB: the database connection to be used
        :type dB: psycopg2.connection
        :param truncate: If true, table will be truncated as object is created. USE WITH CARE!
        :type truncate: bool
        :param upSert: if True, write() will try both an insert and an update if the record exists.
                       Otherwise, a DuplicateValue error may be returned.
        :type upSert: bool
        :param persist: Defines if objects added or altered should be immediately persisted on the database
        :type persist: bool
        """
        self.dbConn = dB
        self.tbExists = False
        self.upSert = upSert
        self.persist = persist
        self.currCont = None
        if not self.tableExists():
            self.create()
        elif truncate:
            self.truncate()
        dict.__init__(self, *args)

    def __getitem__(self, key):
        """
        Retrieves a continent by key. Goes to the database if needed. Behaves just like a dict
        :param key: the continent id.
        :type key: int
        """
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        try:
            self.currCont = dict.__getitem__(self, key)
        except KeyError:
            self.currCont = self.read(key)
            dict.__setitem__(self, key, self.currCont)
        return self.currCont

    def __setitem__(self, key, value):
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        if not self.upSert and key in dict:
            raise DuplicateValue(key, "continent", value.name, dict.__getitem__(key))
        self.currCont = value
        if self.persist:
            self.write()
        dict.__setitem__(self, key, value)
        return self.currCont

    def tableExists(self):
        if self.tbExists:
            return True
        cur = self.dbConn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s;", ('tb_continent',))
        self.tbExists = bool(cur.rowcount)
        self.dbConn.commit()
        return self.tbExists

    def create(self):
        cur = self.dbConn.cursor()
        cur.execute('CREATE TABLE tb_continent('
                    '"CONT_ID" integer NOT NULL, '
                    '"CONT_NAME" character varying(50), '
                    'CONSTRAINT "PK_CONTINENT" PRIMARY KEY ("CONT_ID");')
        self.dbConn.commit()

    def truncate(self):
        cur = self.dbConn.cursor()
        cur.execute('truncate table TB_CONTINENT;')
        self.dbConn.commit()

    def write(self):
        cur = self.dbConn.cursor()
        try:
            cur.execute('insert into TB_CONTINENT '
                        '   VALUES (%s, %s);', (self.currCont.id, self.currCont.name,))
            self.dbConn.commit()
        except psycopg2.IntegrityError:
            if self.upSert:
                cur.rollback()
                cur.execute('update tb_continent '
                            "   set CONT_NAME = '%s'"
                            '   where CONT_ID = %s;',
                            (self.currCont.name, self.currCont.id))
                self.dbConn.commit()
            else:
                cur.rollback()
                self.dbConn.commit()
                raise

    def read(self, param):
        """
        Recovers and creates a continent from the database.
        :param param: Search condition. Can be either an Id or a Continent name
        :type param: int or Continent
        """
        cur = self.dbConn.cursor()
        if type(param == int):
            cur.execute('SELECT CONT_ID, CONT_NAME FROM TB_CONTINENT '
                        ' WHERE CONT_ID = %s;', (param,))
        elif type(param == str):
            cur.execute("SELECT CONT_ID, CONT_NAME FROM TB_CONTINENT "
                        " WHERE CONT_NAME = '%s';", (param,))
        else:
            raise ValueError
        try:
            theCont = cur.fetchone()
        except psycopg2.ProgrammingError:
            self.dbConn.commit()
            raise KeyError
        theCont = Continent(int(theCont[0]), theCont[1])
        self.dbConn.commit()
        return theCont


class dBRating(list):
    '''
    Generates a python list representation of ratings table in the database.
    '''

    def __init__(self, dB, beers, truncate=False, persist=True, upSert=True, blocksize=1000, *args):
        """ Initializes the manager for a tb_beer table (which behaves as a dict of beers as well).
        :param dB: the database connection to be used
        :type dB: psycopg2.connection
        :param beers: The beers  dict to which the beer should be subordinated.
        :type beers: dbBeer
        :param truncate: If true, table will be truncated as object is created. USE WITH CARE!
        :type truncate: bool
        :param upSert: if True, write() will try both an insert and an update if the record exists.
                       Otherwise, a DuplicateValue error may be returned.
        :type upSert: bool
        :param persist: Defines if objects added or altered should be immediately persisted on the database
        :type persist: bool
        :param blocksize: controls the number of records which should be recorded before a commit.
        :type blocksize: int
        """
        self.dbConn = dB
        self.nWrites = 0
        self.blockSize = blocksize
        self.parents = beers
        self.tbExists = False
        self.upSert = upSert
        self.persist = persist
        #  : :type self.currItem: UserRating
        self.currItem = None
        if not self.tableExists():
            self.create()
        elif truncate:
            self.truncate()
        list.__init__(self, *args)

    def doCommit(self):
        self.nWrites += 1
        if self.nWrites >= self.blockSize:
            self.dbConn.commit()
            self.nWrites = 0

    def integrity(self, item=None):
        """
        Keeps the integrity between rating and beer in the dictionaries. the database part should be ok.
        :param item: The item to be changed. If None, assumed to be the last used item.
        :type item: UserRating
        """

        if item is None:
            item = self.currItem
        if item.beer.id not in self.parents:
            temp, self.parents.persist = self.parents.persist, False
            self.parents[item.beer.id] = self.parents.read(item.beer.id)
            self.parents.persist = temp
            item.beer = self.parents[item.beer.id]
        if item.id not in self.parents[item.beer.id].ratings:
            self.parents[item.beer.id].addRating(item)

    def __getitem__(self, key):
        """
        Retrieves a rating by key (index). Goes to the database if needed. Behaves just like a dict
        :param key: the beer id.
        :type key: int
        """
        if type(key) != int:
            raise TypeError('Key must be integer, was "{}"'.format(key))
        try:
            self.currItem = list.__getitem__(self, key)
        except KeyError:
            self.currItem = self.read(key)
            list.__setitem__(self, key, self.currItem)
        self.integrity()
        return self.currItem

    def append(self, item):
        if type(item) != UserRating:
            raise TypeError('Item must be UserRating, was "{}"'.format(type(item)))
        self.currItem = item
        self.integrity()
        if self.persist:
            self.write()
        list.append(self, item)

    def __setitem__(self, key, value):
        if type(key) != int:
            raise TypeError('Key must be integer, was "{}"'.format(key))
        self.currItem = value
        self.integrity()
        if self.persist:
            self.write()
        list.__setitem__(self, key, value)
        return self.currItem

    def tableExists(self):
        if self.tbExists:
            return True
        cur = self.dbConn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s", ('tb_rating',))
        self.tbExists = bool(cur.rowcount)
        self.doCommit()
        return self.tbExists

    def create(self):
        cur = self.dbConn.cursor()
        #  BeerId,userId,"userName",compound,aroma,appearance,taste,palate,overall,"location","date","notes"
        #  TODO: RATING_DATE data is not timestamp, it's only date. I should process that on DBLoad
        cur.execute('CREATE TABLE tb_rating('
                    '"BEER_ID" integer NOT NULL,'
                    '"USER_ID" integer NOT NULL,'
                    '"USER_NAME" character varying(50) NOT NULL,'
                    '"RATING_COMPOUND" double precision,'
                    '"RATING_AROMA" integer,'
                    '"RATING_APPEARANCE" integer,'
                    '"RATING_TASTE" integer,'
                    '"RATING_PALATE" integer,'
                    '"RATING_OVERALL" integer,'
                    '"RATING_LOCATION" character varying(100),'
                    '"RATING_DATE" timestamp,'
                    '"RATING_NOTES" text,'
                    'CONSTRAINT "PK_RATING" PRIMARY KEY ("BEER_ID", "USER_ID", "RATING_DATE"));')
        self.doCommit()

    def truncate(self):
        cur = self.dbConn.cursor()
        cur.execute('truncate table TB_RATING;')
        self.doCommit()

    def write(self):
        cur = self.dbConn.cursor()
        try:
            cur.execute('savepoint mysave;')
            cur.execute('insert into tb_rating '
                        "   VALUES (%s, %s, %s, %s, %s, %s,"
                        "%s, %s, %s, %s, %s, %s);",
                        (self.currItem.beer.id,
                         self.currItem.id,
                         self.currItem.name,
                         self.currItem.compound,
                         self.currItem.aroma,
                         self.currItem.appearance,
                         self.currItem.taste,
                         self.currItem.palate,
                         self.currItem.overall,
                         self.currItem.location,
                         self.currItem.date,
                         self.currItem.notes))
            self.doCommit()
        except psycopg2.IntegrityError:
            if self.upSert:
                self.dbConn.rollback()
                cur.execute('update tb_rating '
                            '   set "USER_NAME" = %s,'
                            '       "RATING_COMPOUND" = %s,'
                            '       "RATING_AROMA" = %s,'
                            '       "RATING_APPEARANCE" = %s,'
                            '       "RATING_TASTE" = %s,'
                            '       "RATING_PALATE" = %s,'
                            '       "RATING_OVERALL" = %s,'
                            '       "RATING_LOCATION" = %s,'
                            '       "RATING_NOTES" = %s'
                            '   where "BEER_ID" = %s and "USER_ID" = %s AND "RATING_DATE" = %s;',
                            (self.currItem.name,
                             self.currItem.compound,
                             self.currItem.aroma,
                             self.currItem.appearance,
                             self.currItem.taste,
                             self.currItem.palate,
                             self.currItem.overall,
                             self.currItem.location,
                             self.currItem.notes,
                             self.currItem.beer.id,
                             self.currItem.id,
                             self.currItem.date))
                self.doCommit()
            else:
                cur.rollback()
                self.doCommit()
                raise

    def read(self, param):
        """
        Recovers and creates a rating from the database. Will create a beer as well, if required.
        :param param: Search condition.
        :type param: tuple
        """
        #  TODO: Check for repetition of the same rating. Possibly transform Ratings into a dict hashable from beer, user and date.
        cur = self.dbConn.cursor()
        if type(param) == tuple:
            cur.execute('SELECT "BEER_ID",'
                        '"USER_ID",'
                        '"USER_NAME",'
                        '"RATING_COMPOUND",'
                        '"RATING_AROMA",'
                        '"RATING_APPEARANCE",'
                        '"RATING_TASTE",'
                        '"RATING_PALATE",'
                        '"RATING_OVERALL",'
                        '"RATING_LOCATION",'
                        '"RATING_DATE",'
                        '"RATING_NOTES"'
                        '   FROM TB_RATING '
                        '   WHERE BEER_ID = %s AND USER_ID = %s AND RATING_DATE = %s;', param)
        else:
            raise ValueError
        try:
            theItem = cur.fetchone()
        except psycopg2.ProgrammingError:
            self.doCommit()
            raise KeyError
        if int(theItem[0]) not in self.parents:
            theParent = self.parents.read(int(theItem[0]))
        theItem = UserRating(theParent, theItem[1], theItem[2], theItem[3],
                             theItem[4], theItem[5], theItem[6], theItem[7],
                             theItem[8], theItem[9], theItem[10], theItem[11], theItem[12])
        self.integrity(theItem)
        self.doCommit()
        return theItem


class dbBeer(dict):
    '''
    Generates a python dict representation of beers table in the database.
    '''

    def __init__(self, dB, breweries, truncate=False, persist=True, upSert=True, blocksize=1000, *args):
        """ Initializes the manager for a tb_beer table (which behaves as a dict of beers as well).
        :param dB: the database connection to be used
        :type dB: psycopg2.connection
        :param breweries: The breweries dict to which the beer should be subordinated.
        :type breweries: dbBrewery
        :param truncate: If true, table will be truncated as object is created. USE WITH CARE!
        :type truncate: bool
        :param upSert: if True, write() will try both an insert and an update if the record exists.
                       Otherwise, a DuplicateValue error may be returned.
        :type upSert: bool
        :param persist: Defines if objects added or altered should be immediately persisted on the database
        :type persist: bool
        :param blocksize: controls the number of records which should be recorded before a commit.
        :type blocksize: int
        """
        self.dbConn = dB
        self.nWrites = 0
        self.blockSize = blocksize
        self.parents = breweries
        self.tbExists = False
        self.upSert = upSert
        self.persist = persist
        #  : :type self.currItem: Beer
        self.currItem = None
        if not self.tableExists():
            self.create()
        elif truncate:
            self.truncate()
        dict.__init__(self, *args)

    def doCommit(self):
        self.nWrites += 1
        if self.nWrites >= self.blockSize:
            self.dbConn.commit()
            self.nWrites = 0

    def integrity(self, item=None):
        """
        Keeps the integrity between beer and brewery in the dictionaries. the database part should be ok.
        :param item: The item to be changed. If None, assumed to be the last used item.
        :type item: Beer
        """

        if item is None:
            item = self.currItem
        if item.brewer.id not in self.parents:
            temp, self.parents.persist = self.parents.persist, False
            self.parents[item.brewer.id] = self.parents.read(item.brewer.id)
            self.parents.persist = temp
            item.brewer = self.parents[item.brewer.id]
        if item.id not in self.parents[item.brewer.id].Beers:
            self.parents[item.brewer.id].addBeer(item)

    def __getitem__(self, key):
        """
        Retrieves a beer by key. Goes to the database if needed. Behaves just like a dict
        :param key: the beer id.
        :type key: int
        """
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        try:
            self.currItem = dict.__getitem__(self, key)
        except KeyError:
            self.currItem = self.read(key)
            dict.__setitem__(self, key, self.currItem)
        self.integrity()
        return self.currItem

    def __setitem__(self, key, value):
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        if not self.upSert and key in dict:
            raise DuplicateValue(key, "beer", value.name, dict.__getitem__(key))
        self.currItem = value
        self.integrity()
        if self.persist:
            self.write()
        dict.__setitem__(self, key, value)
        return self.currItem

    def tableExists(self):
        if self.tbExists:
            return True
        cur = self.dbConn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s", ('tb_beer',))
        self.tbExists = bool(cur.rowcount)
        self.doCommit()
        return self.tbExists

    def create(self):
        cur = self.dbConn.cursor()
        #  TODO: I'm not considering glasses right now
        cur.execute('CREATE TABLE tb_beer('
                    '"CONT_ID" integer NOT NULL,'
                    '"COUNTRY_ID" integer NOT NULL,'
                    '"LOCATION_ID" integer NOT NULL,'
                    '"BREWERY_ID" integer NOT NULL,'
                    '"BEER_ID" integer NOT NULL,'
                    '"BEER_NAME" character varying(100) NOT NULL,'
                    '"BEER_STYLE_ID" integer,'
                    '"BEER_STYLE_NAME" character varying(50),'
                    '"BEER_CITY_ID" integer,'
                    '"BEER_CITY_NAME" character varying(100),'
                    '"BEER_ABV" double precision,'
                    '"BEER_IBU" integer,'
                    '"BEER_CALORIES" integer,'
                    '"BEER_AVAIL_BOTTLE" boolean,'
                    '"BEER_AVAIL_TAP" boolean,'
                    '"BEER_SEASONAL" character varying(30),'
                    '"BEER_OVERALL_RATING" double precision,'
                    '"BEER_AVG_RATING" double precision,'
                    '"BEER_STYLE_RATING" double precision,'
                    '"BEER_NRATINGS" integer,'
                    '"BEER_DISTRIBUTION" character varying(50),'
                    'CONSTRAINT "PK_BEER" PRIMARY KEY ("BEER_ID"));')
        self.doCommit()

    def truncate(self):
        cur = self.dbConn.cursor()
        cur.execute('truncate table TB_BEER;')
        self.doCommit()

    def write(self):
        cur = self.dbConn.cursor()
        try:
            cur.execute('insert into tb_beer '
                        "   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
                        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (self.currItem.brewer.location.country.continent.id,
                         self.currItem.brewer.location.country.id,
                         self.currItem.brewer.location.id,
                         self.currItem.brewer.id,
                         self.currItem.id,
                         self.currItem.name,
                         self.currItem.styleId,
                         self.currItem.styleName,
                         self.currItem.city.id,
                         self.currItem.city.name,
                         self.currItem.abv,
                         self.currItem.IBU,
                         self.currItem.calories,
                         self.currItem.availBottle,
                         self.currItem.availTap,
                         self.currItem.seasonality,
                         self.currItem.overPerf,
                         self.currItem.avgRate,
                         self.currItem.stylePerf,
                         self.currItem.nRatings,
                         self.currItem.distrScope))
            self.doCommit()
        except psycopg2.IntegrityError:
            if self.upSert:
                cur.rollback()
                cur.execute('update tb_beer '
                            '   set CONT_ID = %s,'
                            '       COUNTRY_ID = %s,'
                            '       LOCATION_ID = %s,'
                            '       BREWERY_ID = %s,'
                            '       BEER_NAME = %s,'
                            '       BEER_STYLE_ID = %s,'
                            '       BEER_STYLE_NAME = %s,'
                            '       BEER_CITY_ID = %s,'
                            '       BEER_CITY_NAME = %s,'
                            '       BEER_ABV = %s,'
                            '       BEER_IBU = %s,'
                            '       BEER_CALORIES = %s,'
                            '       BEER_AVAIL_BOTTLE = %s,'
                            '       BEER_AVAIL_TAP = %s,'
                            '       BEER_SEASONAL = %s,'
                            '       BEER_OVERALL_RATING = %s,'
                            '       BEER_AVG_RATING = %s,'
                            '       BEER_STYLE_RATING = %s,'
                            '       BEER_NRATINGS = %s,'
                            '       BEER_DISTRIBUTION = %s'
                            '   where BEER_ID = %s;',
                            (self.currItem.brewer.location.country.continent.id,
                             self.currItem.brewer.location.country.id,
                             self.currItem.brewer.location.id,
                             self.currItem.brewer.id,
                             self.currItem.name,
                             self.currItem.styleId,
                             self.currItem.styleName,
                             self.currItem.city.id,
                             self.currItem.city.name,
                             self.currItem.abv,
                             self.currItem.IBU,
                             self.currItem.calories,
                             self.currItem.availBottle,
                             self.currItem.availTap,
                             self.currItem.seasonality,
                             self.currItem.overPerf,
                             self.currItem.avgRate,
                             self.currItem.stylePerf,
                             self.currItem.nRatings,
                             self.currItem.distrScope,
                             self.currItem.id,))
                self.doCommit()
            else:
                cur.rollback()
                self.doCommit()
                raise

    def read(self, param):
        """
        Recovers and creates a beer from the database. Will create a brewery as well, if required.
        :param param: Search condition.
        :type param: int or Beer
        """
        cur = self.dbConn.cursor()
        if type(param) == int:
            cur.execute('SELECT CONT_ID, COUNTRY_ID, LOCATION_ID, BREWERY_ID,'
                        '       BEER_ID,'
                        '       BEER_NAME,'
                        '       BEER_STYLE_ID,'
                        '       BEER_STYLE_NAME,'
                        '       BEER_CITY_ID,'
                        '       BEER_CITY_NAME,'
                        '       BEER_ABV,'
                        '       BEER_IBU,'
                        '       BEER_CALORIES,'
                        '       BEER_AVAIL_BOTTLE,'
                        '       BEER_AVAIL_TAP,'
                        '       BEER_SEASONAL,'
                        '       BEER_OVERALL_RATING,'
                        '       BEER_AVG_RATING,'
                        '       BEER_STYLE_RATING,'
                        '       BEER_NRATINGS,'
                        '       BEER_DISTRIBUTION'
                        '   FROM TB_BEER '
                        '   WHERE BEER_ID = %s;', (param,))
        elif type(param) == str:
            cur.execute('SELECT CONT_ID, COUNTRY_ID, LOCATION_ID, BREWERY_ID,'
                        '       BEER_ID,'
                        '       BEER_NAME,'
                        '       BEER_STYLE_ID,'
                        '       BEER_STYLE_NAME,'
                        '       BEER_CITY_ID,'
                        '       BEER_CITY_NAME,'
                        '       BEER_ABV,'
                        '       BEER_IBU,'
                        '       BEER_CALORIES,'
                        '       BEER_AVAIL_BOTTLE,'
                        '       BEER_AVAIL_TAP,'
                        '       BEER_SEASONAL,'
                        '       BEER_OVERALL_RATING,'
                        '       BEER_AVG_RATING,'
                        '       BEER_STYLE_RATING,'
                        '       BEER_NRATINGS,'
                        '       BEER_DISTRIBUTION'
                        '   FROM TB_BEER '
                        '   WHERE BEER_NAME = %s;', (param,))
        else:
            raise ValueError
        try:
            theItem = cur.fetchone()
        except psycopg2.ProgrammingError:
            self.doCommit()
            raise KeyError
        if int(theItem[3]) not in self.parents:
            theParent = self.parents.read(int(theItem[3]))
        #  TODO: I'm throwing away glass information. This could be important
        theItem = Beer(int(theItem[4]), theItem[5], theParent, '', int(theItem[6]), theItem[7], float(theItem[10]),
                       int(theItem[11]), float(theItem[12]), [], float(theItem[17]), float(theItem[16]), float(theItem[18]), float(theItem[19]),
                       City(int(theItem[8]), theItem[9]), theItem[13], theItem[15], theItem[14], theItem[20])
        self.integrity(theItem)
        self.doCommit()
        return theItem


class dbBrewery(dict):
    '''
    Generates a python dict representation of breweries table in the database.
    '''

    def __init__(self, dB, locations, truncate=False, persist=True, upSert=True, blocksize=1000, *args):
        """ Initializes the manager for a tb_brewery table (which behaves as a dict of breweries as well).
        :param dB: the database connection to be used
        :type dB: psycopg2.connection
        :param locations: The locations dict to which the brewery should be subordinated.
        :type locations: dbLocation
        :param truncate: If true, table will be truncated as object is created. USE WITH CARE!
        :type truncate: bool
        :param upSert: if True, write() will try both an insert and an update if the record exists.
                       Otherwise, a DuplicateValue error may be returned.
        :type upSert: bool
        :param persist: Defines if objects added or altered should be immediately persisted on the database
        :type persist: bool
        """
        self.dbConn = dB
        self.nWrites = 0
        self.blockSize = blocksize
        self.parents = locations
        self.tbExists = False
        self.upSert = upSert
        self.persist = persist
        #  : :type self.currItem: Brewery
        self.currItem = None
        if not self.tableExists():
            self.create()
        elif truncate:
            self.truncate()
        dict.__init__(self, *args)

    def doCommit(self):
        self.nWrites += 1
        if self.nWrites >= self.blockSize:
            self.dbConn.commit()
            self.nWrites = 0

    def integrity(self, item=None):
        """
        Keeps the integrity between brewery and location in the dictionaries. the database part should be ok.
        :param item: The item to be changed. If None, assumed to be the last used item.
        :type item: Brewery
        """

        if item is None:
            item = self.currItem
        if item.location.id not in self.parents:
            temp, self.parents.persist = self.parents.persist, False
            self.parents[item.location.id] = self.parents.read(item.location.id)
            self.parents.persist = temp
            item.location = self.parents[item.location.id]
        if item.id not in self.parents[item.location.id].breweries:
            self.parents[item.location.id].addBrewery(item)

    def __getitem__(self, key):
        """
        Retrieves a brewery by key. Goes to the database if needed. Behaves just like a dict
        :param key: the brewery id.
        :type key: int
        """
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        try:
            self.currItem = dict.__getitem__(self, key)
        except KeyError:
            self.currItem = self.read(key)
            dict.__setitem__(self, key, self.currItem)
        self.integrity()
        return self.currItem

    def __setitem__(self, key, value):
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        if not self.upSert and key in dict:
            raise DuplicateValue(key, "brewery", value.name, dict.__getitem__(key))
        self.currItem = value
        self.integrity()
        if self.persist:
            self.write()
        dict.__setitem__(self, key, value)
        return self.currItem

    def tableExists(self):
        if self.tbExists:
            return True
        cur = self.dbConn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s", ('tb_brewery',))
        self.tbExists = bool(cur.rowcount)
        self.doCommit()
        return self.tbExists

    def create(self):
        cur = self.dbConn.cursor()
        cur.execute('CREATE TABLE tb_brewery('
                    '"CONT_ID" integer NOT NULL,'
                    '"COUNTRY_ID" integer NOT NULL,'
                    '"LOCATION_ID" integer NOT NULL,'
                    '"BREWERY_ID" integer NOT NULL,'
                    '"BREWERY_NAME" character varying(100) NOT NULL,'
                    '"BREWERY_TYPE" character varying(30),'
                    'NUMBER_BEERS integer NOT NULL,'
                    'YEAR_ESTABLISHED integer NOT NULL,'
                    'CONSTRAINT "PK_BREWERY" PRIMARY KEY ("BREWERY_ID"));')
        self.doCommit()

    def truncate(self):
        cur = self.dbConn.cursor()
        cur.execute('truncate table TB_BREWERY;')
        self.doCommit()

    def write(self):
        cur = self.dbConn.cursor()
        try:
            cur.execute('insert into tb_brewery '
                        "   VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                        (self.currItem.location.country.continent.id,
                         self.currItem.location.country.id,
                         self.currItem.location.id,
                         self.currItem.id, self.currItem.name,
                         self.currItem.bType, self.currItem.nBeers, self.currItem.yEstb))
            self.doCommit()
        except psycopg2.IntegrityError:
            if self.upSert:
                cur.rollback()
                cur.execute('update tb_brewery '
                            "   set CONT_ID = %s,"
                            "       COUNTRY_ID = %s,"
                            "       LOCATION_ID = %s,"
                            "       BREWERY_NAME = '%s',"
                            "       BREWERY_TYPE = '%s',"
                            '       NUMBER_BEERS = %s,'
                            '       YEAR_ESTABLISHED = %s'
                            '   where COUNTRY_ID = %s;',
                            (self.currItem.location.country.continent.id,
                             self.currItem.location.country.id,
                             self.currItem.location.id,
                             self.currItem.name,
                             self.currItem.brType,
                             self.currItem.nBeers,
                             self.currItem.yEstb,
                             self.currItem.id))
                self.doCommit()
            else:
                cur.rollback()
                self.doCommit()
                raise

    def read(self, param):
        """
        Recovers and creates a brewery from the database. Will create a location as well, if required.
        :param param: Search condition. Can be either an Id or a brewery name
        :type param: int or Brewery
        """
        cur = self.dbConn.cursor()
        if type(param) == int:
            cur.execute('SELECT CONT_ID, COUNTRY_ID, LOCATION_ID, BREWERY_ID,'
                        '       BREWERY_NAME, BREWERY_TYPE, NUMBER_BEERS,'
                        '       YEAR_ESTABLISHED'
                        '   FROM TB_BREWERY '
                        '   WHERE BREWERY_ID = %s;', (param,))
        elif type(param) == str:
            cur.execute('SELECT CONT_ID, COUNTRY_ID, LOCATION_ID, BREWERY_ID,'
                        '       BREWERY_NAME, BREWERY_TYPE, NUMBER_BEERS,'
                        '       YEAR_ESTABLISHED'
                        '   FROM TB_BREWERY '
                        "   WHERE BREWERY_NAME = '%s';", (param,))
        else:
            raise ValueError
        try:
            theItem = cur.fetchone()
        except psycopg2.ProgrammingError:
            self.doCommit()
            raise KeyError
        if int(theItem[2]) not in self.parents:
            theParent = self.parents.read(int(theItem[2]))
        theItem = Brewery(theParent, int(theItem[3]), theItem[4], theItem[5], int(theItem[6]), int(theItem[7]))
        self.integrity(theItem)
        self.doCommit()
        return theItem


class dbLocation(dict):
    '''
    Generates a python dict representation of countries table in the database.
    '''

    def __init__(self, dB, countries, truncate=False, persist=True, upSert=True, *args):
        """ Initializes the manager for a tb_locations table (which behaves as a dict of locations as well).
        :param dB: the database connection to be used
        :type dB: psycopg2.connection
        :param countries: The countries dict to which the location should be subordinated.
        :type countries: dbCountry
        :param truncate: If true, table will be truncated as object is created. USE WITH CARE!
        :type truncate: bool
        :param upSert: if True, write() will try both an insert and an update if the record exists.
                       Otherwise, a DuplicateValue error may be returned.
        :type upSert: bool
        :param persist: Defines if objects added or altered should be immediately persisted on the database
        :type persist: bool
        """
        self.dbConn = dB
        self.countries = countries
        self.tbExists = False
        self.upSert = upSert
        self.persist = persist
        #  : :type self.currItem: Location
        self.currItem = None
        if not self.tableExists():
            self.create()
        elif truncate:
            self.truncate()
        dict.__init__(self, *args)

    def integrity(self, location=None):
        """
        Keeps the integrity between location and countries in the dictionaries. the database part should be ok.
        """

        if location is None:
            location = self.currItem
        if location.country.id not in self.countries:
            temp, self.countries.persist = self.countries.persist, False
            self.countries[location.country.id] = self.countries.read(location.country.id)
            self.countries.persist = temp
            location.country = self.countries[location.country.id]
        if location.id not in self.countries[location.country.id].locations:
            self.countries[location.country.id].addLocation(location)

    def __getitem__(self, key):
        """
        Retrieves a location by key. Goes to the database if needed. Behaves just like a dict
        :param key: the location id.
        :type key: int
        """
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        try:
            self.currItem = dict.__getitem__(self, key)
        except KeyError:
            self.currItem = self.read(key)
            dict.__setitem__(self, key, self.currItem)
        self.integrity()
        return self.currItem

    def __setitem__(self, key, value):
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        if not self.upSert and key in dict:
            raise DuplicateValue(key, "location", value.name, dict.__getitem__(key))
        self.currItem = value
        self.integrity()
        if self.persist:
            self.write()
        dict.__setitem__(self, key, value)
        return self.currItem

    def tableExists(self):
        if self.tbExists:
            return True
        cur = self.dbConn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s", ('tb_location',))
        self.tbExists = bool(cur.rowcount)
        self.dbConn.commit()
        return self.tbExists

    def create(self):
        cur = self.dbConn.cursor()
        cur.execute('CREATE TABLE tb_location('
                    '"CONT_ID" integer NOT NULL,'
                    '"COUNTRY_ID" integer NOT NULL,'
                    '"LOCATION_ID" integer NOT NULL,'
                    '"LOCATION_NAME" character varying(50),'
                    'CONSTRAINT "PK_LOCATION" PRIMARY KEY ("LOCATION_ID"));')
        self.dbConn.commit()

    def truncate(self):
        cur = self.dbConn.cursor()
        cur.execute('truncate table TB_LOCATION;')
        self.dbConn.commit()

    def write(self):
        cur = self.dbConn.cursor()
        try:
            cur.execute('insert into tb_location '
                        '   VALUES (%s, %s, %s, %s);',
                        (self.currItem.country.continent.id, self.currItem.country.id,
                         self.currItem.id, self.currItem.name))
            self.dbConn.commit()
        except psycopg2.IntegrityError:
            if self.upSert:
                cur.rollback()
                cur.execute('update tb_location '
                            "   set CONT_ID = %s,"
                            "       COUNTRY_ID = %s,"
                            "       LOCATION_NAME = '%s'"
                            '   where LOCATION_ID = %s;',
                            (self.currItem.country.continent.id, self.currItem.country.id,
                             self.currItem.name, self.currItem.id))
                self.dbConn.commit()
            else:
                cur.rollback()
                self.dbConn.commit()
                raise

    def read(self, param):
        """
        Recovers and creates a location from the database. Will create a country as well, if required.
        :param param: Search condition.
        :type param: int or Location
        """
        cur = self.dbConn.cursor()
        if type(param) == int:
            cur.execute('SELECT CONT_ID, COUNTRY_ID, LOCATION_ID, LOCATION_NAME FROM TB_LOCATION '
                        ' WHERE LOCATION_ID = %s;', (param,))
        elif type(param) == str:
            cur.execute("SELECT CONT_ID, COUNTRY_ID, LOCATION_ID, LOCATION_NAME FROM TB_LOCATION "
                        " WHERE LOCATION_NAME = '%s';", (param,))
        else:
            raise ValueError
        try:
            theLocation = cur.fetchone()
        except psycopg2.ProgrammingError:
            self.dbConn.commit()
            raise KeyError
        if int(theLocation[1]) not in self.countries:
            theCountry = self.countries.read(int(theLocation[1]))
        theLocation = Location(theCountry, int(theLocation[1]), theLocation[2], '')
        self.integrity(theLocation)
        self.dbConn.commit()
        return theLocation


class dbCountry(dict):
    '''
    Generates a python dict representation of countries table in the database.
    '''

    def __init__(self, dB, conts, truncate=False, persist=True, upSert=True, *args):
        """ Initializes the manager for a tb_country table (which behaves as a dict of countries as well).
        :param dB: the database connection to be used
        :type dB: psycopg2.connection
        :param conts: The continents dict to which the country should be subordinated.
        :type conts: dbContinent
        :param truncate: If true, table will be truncated as object is created. USE WITH CARE!
        :type truncate: bool
        :param upSert: if True, write() will try both an insert and an update if the record exists.
                       Otherwise, a DuplicateValue error may be returned.
        :type upSert: bool
        :param persist: Defines if objects added or altered should be immediately persisted on the database
        :type persist: bool
        """
        self.dbConn = dB
        self.continents = conts
        self.tbExists = False
        self.upSert = upSert
        self.persist = persist
        #  : :type self.currCountry: Country
        self.currCountry = None
        if not self.tableExists():
            self.create()
        elif truncate:
            self.truncate()
        dict.__init__(self, *args)

    def integrity(self, country=None):
        """
        Keeps the integrity between country and continents in the dictionaries. the database part should be ok.
        """

        if country is None:
            country = self.currCountry
        if country.continent.id not in self.continents:
            temp, self.continents.persist = self.continents.persist, False
            self.continents[country.continent.id] = self.continents.read(country.continent.id)
            self.continents.persist = temp
            country.continent = self.continents[country.continent.id]
        if country.id not in self.continents[country.continent.id].countries:
            self.continents[country.continent.id].addCountry(country)

    def __getitem__(self, key):
        """
        Retrieves a country by key. Goes to the database if needed. Behaves just like a dict
        :param key: the country id.
        :type key: int
        """
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        try:
            self.currCountry = dict.__getitem__(self, key)
        except KeyError:
            self.currCountry = self.read(key)
            dict.__setitem__(self, key, self.currCountry)
        self.integrity()
        return self.currCountry

    def __setitem__(self, key, value):
        if type(key) != int:
            raise ValueError('Key must be integer, was "{}"'.format(key))
        if not self.upSert and key in dict:
            raise DuplicateValue(key, "country", value.name, dict.__getitem__(key))
        self.currCountry = value
        self.integrity()
        if self.persist:
            self.write()
        dict.__setitem__(self, key, value)
        return self.currCountry

    def tableExists(self):
        if self.tbExists:
            return True
        cur = self.dbConn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s", ('tb_country',))
        self.tbExists = bool(cur.rowcount)
        self.dbConn.commit()
        return self.tbExists

    def create(self):
        cur = self.dbConn.cursor()
        cur.execute('CREATE TABLE tb_country('
                    '"CONT_ID" integer NOT NULL,'
                    '"COUNTRY_ID" integer NOT NULL,'
                    '"COUNTRY_NAME" character varying(50),'
                    'CONSTRAINT "PK_COUNTRY" PRIMARY KEY ("COUNTRY_ID"));')
        self.dbConn.commit()

    def truncate(self):
        cur = self.dbConn.cursor()
        cur.execute('truncate table TB_COUNTRY;')
        self.dbConn.commit()

    def write(self):
        cur = self.dbConn.cursor()
        try:
            cur.execute('insert into tb_country '
                        '   VALUES (%s, %s, %s);',
                        (self.currCountry.continent.id, self.currCountry.id, self.currCountry.name))
            self.dbConn.commit()
        except psycopg2.IntegrityError:
            if self.upSert:
                cur.rollback()
                cur.execute('update tb_country '
                            "   set CONT_ID = %s,"
                            "       COUNTRY_NAME = '%s'"
                            '   where COUNTRY_ID = %s;',
                            (self.currCountry.continent.id, self.currCountry.name, self.currCountry.id))
                self.dbConn.commit()
            else:
                cur.rollback()
                self.dbConn.commit()
                raise

    def read(self, param):
        """
        Recovers and creates a country from the database. Will create a continent as well, if required.
        :param param: Search condition. Can be either an Id or a Continent name
        :type param: int or Country
        """
        cur = self.dbConn.cursor()
        if (type(param) == int):
            cur.execute('SELECT CONT_ID, COUNTRY_ID, COUNTRY_NAME FROM TB_COUNTRY '
                        ' WHERE COUNTRY_ID = %s;', (param,))
        elif (type(param) == str):
            cur.execute("SELECT CONT_ID, COUNTRY_ID, COUNTRY_NAME FROM TB_COUNTRY "
                        " WHERE COUNTRY_NAME = '%s';", (param,))
        else:
            raise ValueError

        try:
            theCountry = cur.fetchone()
        except psycopg2.ProgrammingError:
            self.dbConn.commit()
            raise KeyError
        if int(theCountry[0]) not in self.continents:
            theContinent = self.continents.read(int(theCountry[0]))
        theCountry = Country(theContinent, int(theCountry[1]), theCountry[2])
        self.integrity(theCountry)
        self.dbConn.commit()
        return theCountry
