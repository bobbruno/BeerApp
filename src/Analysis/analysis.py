'''
Created on 07/10/2014

@author: bobbruno
'''

from gensim import utils
from inspect import isgenerator
from itertools import izip, product
import nltk
from nltk.corpus import stopwords
import pandas
import psycopg2
import re

from Scraper.Parser import Continent, Country, Location, Brewery


stemmer = nltk.snowball.EnglishStemmer()

myStemDict = {u'nutty': u'nut',
              u'reddish': u'red',
              u'rotten': u'rot',
              u'rotting': u'rot',
              u'cristaline': u'cristal',
              u'red': u'red',
              u'spicy': u'spices',
              u'spicyness': u'spices',
              u' ': u' ',
              u'cereal': u'cereal'}


def mystem(x):
    try:
        return myStemDict[x]
    except KeyError:
        return stemmer.stem(x)


#  TODO: Deal with words in [u'strong', u'weak', u'touch'] that can show up on any channel
#  TODO: 1- words when tokens as [u'not', u"don't"] show up


stops = {mystem(x) for x in stopwords.words('english')}
punct = set([u',', u'(', u')', u':', u'-', u'...', u'@', u';', u'*', u'!', u'"', u"'", u'[', u']', u'/',
             u'---', u'?', u'&', u'%', u'--'])
containerSizes = set([u'750ml', u'500ml', u'350ml', u'0,5l', u'50cl'])
generalWords = {mystem(x) for x in [u'beer', u'ale', u'brew', u'draft', u'ipa', u'pretty', u'really',
                                    u'buddy', u'iphone', u'oz', u'ml', u'pour', u'one', u'cc', u'cl', u'l',
                                    u'also', u'thank', u'update', u'get', u'sample', u'style', u'would',
                                    u'as', u'well']}
toRemove = stops | punct | containerSizes | generalWords

#  Sentiment attributes
goodSentiment = {mystem(x) for x in [u'balanced', u'big', u'decent', u'fairly', u'nice', u'excellent', u'good',
                                     u'great']}
badSentiment = {mystem(x) for x in [u'bad', u'spare', ]}
unknownSentiment = {mystem(x) for x in [u'almost', u'average', u'bit', u'drinkability', u'like',
                                        u'standard', u'simple', u'basic', u'slightly']}
sentimentWords = goodSentiment | badSentiment | unknownSentiment

#  Appearance Atributes
#  Problem: I may have an n-gram with light brown, dark brown, etc. Deal with that.
#  Also for particles
appColorBase = {mystem(x) for x in [u'color', u'colour', u'bottle', u'label']}
colors = {mystem(x) for x in [u'brown', u'yellow', u'orange', u'amber', u'red', u'ruby',
                              u'tan', u'black', u'tawny', u'beige', u'gold', u'golden', u'copper']}
colorDesignators = {mystem(x) for x in [u'light', u'dark', u'deep', u'cristaline', u'hazy']}
appHeadBase = {mystem(x) for x in [u'head', ]}
appHeadWords = {mystem(x) for x in [u'spare', u'small', u'large', u'huge', u'rocky', u'dense',
                                    u'creamy', u'frothy', u'fizzy', u'white', u'off-white', u'light', u'brown',
                                    u'dark', u'lasting', u'diminishing']}
appLacingBase = {mystem(x) for x in [u'lacing', ]}
appBodyBase = {mystem(x) for x in [u'body', ]}
appBodyWords = {mystem(x) for x in [u'body', u'clear', u'sparkling', u'flat', u'cloudy', u'hazy', u'murky',
                                    u'muddy']}
appParticleBase = {mystem(x) for x in [u'particle', ]}
appParticleWords = {mystem(x) for x in [u'light', u'cloudy', u'heavily', u'particulate', u'chunky']}
appColorNGrams = set([u'{} {}'.format(x, y) for x, y
                     in product(colorDesignators, colors)])
appearanceWords = (appColorBase | appHeadBase | appHeadWords | appLacingBase |
                   appBodyBase | appBodyWords | appParticleBase | appParticleWords |
                   colors | colorDesignators | appColorNGrams)

#  Aroma Attributes
aromaBase = {mystem(x) for x in [u'aroma', 'nose', u'smell']}
aroDesignators = {mystem(x) for x in [u'toasted', u'roasted', u'burnt', u'light', u'heavy', u'harsh']}
aroMaltWords = {mystem(x) for x in [u'malt', u'malty', u'barley', u'corn', u'bread', u'cookie', u'molasses',
                                    u'caramel', u'grain', u'hay', u'straw', u'cereal', u'chocolate',
                                    u'coffee', u'toffee', u'nutty', u'meal', u'nuts', u'wheat']}

#  Most of these N-Grams don't make much sense, but then they will not be found anyway
aroMaltNGrams = set([u'{} {}'.format(x, y) for x, y in product(aroDesignators, aroMaltWords)])
aroHopsWords = {mystem(x) for x in [u'hops', u'hoppy', u'flowers', u'floral', u'perfume', u'herbs', u'celery',
                                    u'grass', u'pine', u'spruce', u'resin', u'citrus', u'grapefruit',
                                    u'orange', u'lemon', u'lime', u'grassy']}
aroHopsNGrams = set([u'{} {}'.format(x, y)
                     for x, y in product(aroDesignators,
                                         aroHopsWords)]) | set([u'{} bomb'.format(x) for x in aroHopsWords])
aroYeastWords = {mystem(x) for x in [u'yeast', u'bacteria', u'dough', u'sweat', u'horse blanket', u'barnyard',
                                     u'leather', u'soap', u'cheese', u'meat', u'broth', u'earth', u'earthy',
                                     u'musty', u'leaves', u'spiced', u'spicy']}
aroYeastNGrams = set([u'{} {}'.format(x, y) for x, y in product(aroDesignators, aroYeastWords)])
aroMiscWords = {mystem(x) for x in [u'alcohol', u'banana', u'bubblegum', u'clove', u'grape', u'raisin', u'plum',
                                    u'prune', u'date', u'apple', u'pear', u'peach', u'pineapple', u'cherry',
                                    u'berry', u'raspberry', u'cassis', u'wine', u'port', u'cask', u'wood',
                                    u'toffee', u'butter', u'butterscotch', u'smoke', u'tar', u'charcoal',
                                    u'soy', u'sauce', u'licorice', u'cola', u'honey', u'sugar', u'maple',
                                    u'vanilla', u'pepper', u'allspice', u'nutmeg', u'cinnamon', u'coriander',
                                    u'ginger', u'tobacco', u'dust', u'chalk', u'vegetable', u'cooked',
                                    u'cabbage', u'cardboard', u'paper', u'medicine', u'solvent', u'paint',
                                    u'thinner', u'bandage', u'skunk', u'brandy', u'sour', u'milk', u'vinegar',
                                    u'rotten', u'eggs', 'mango', u'blueberry', u'fruit', u'fruity', ]}
aroMiscNGrams = set([u'bubble gum', u'soy sauce', u'brown sugar', u'maple syrup', u'cook cabbag',
                     u'paint thinn', u'sour milk', u'rot egg'])

aromaWords = (aromaBase | aroDesignators | aroMaltWords | aroMaltNGrams | aroHopsWords | aroHopsNGrams |
              aroYeastWords | aroYeastNGrams | aroMiscWords | aroMiscNGrams)

#  Palate Attributes
palateBase = {mystem(x) for x in [u'finish', u'aftertaste', u'palate', u'texture']}
palBodyWords = {mystem(x) for x in [u'light', u'medium', u'full']}
palTextureWords = {mystem(x) for x in [u'thin', u'oily', u'creamy', u'sticky', u'crisp',
                                       u'slick', u'alcoholic', u'thick', u'booze', u'minerals', u'gritty']}
palCarbonationWords = {mystem(x) for x in [u'carbonation', u'fizzy', u'lively', u'average', u'soft', u'flat']}
palFinishWords = {mystem(x) for x in [u'metallic', u'chalky', u'astringent', u'bitter', u'mouthfeel',
                                      u'lingering']}
palateWords = palateBase | palBodyWords | palTextureWords | palCarbonationWords | palFinishWords

#  Flavor attributes
#  Most of these usually are the same or additional to aroma. Actual flavor is very limited.
flvDurationWords = {mystem(x) for x in [u'short', u'average', u'long']}
flvDescriptors = {mystem(x) for x in [u'light', u'moderate', u'heavy', u'harsh']}
flvTypeWords = {mystem(x) for x in [u'sweet', u'acidity', u'acidic', u'dry', u'bitter', u'vinegar', u'salty',
                                    u'minerals', u'sour', u'tart']}
flvGeneralWords = {mystem(x) for x in [u'flavor', u'flavour', u'taste']}
flvNgrams = set([u'{} {}'.format(x, y) for x, y in product(flvDescriptors, flvTypeWords)])
flavorWords = flvDurationWords | flvDescriptors | flvTypeWords | flvNgrams

beerVocab = appearanceWords | aromaWords | palateWords | flavorWords | sentimentWords
beerNGrams = appColorNGrams | aroMaltNGrams | aroHopsNGrams | aroYeastNGrams | aroMiscNGrams | flvNgrams


def loadDF(conn=None, continent=None, country=None, location=None, brewery=None, nLimit=None, sample=False):
    """ Loads a pandas dataframe with data from the db connection specified. If any
        restrictions are passed, they will be applied to the query.
    :param conn: the database connection object to be used
    :type conn: psycopg2.connection
    :param continent: a continent or list of continents, either by id or object. If
                      not specified, all continents will be loaded
    :type continent: int or Continent or list or None
    :param country: a country or list of countries, either by id or object. If
                      not specified, all countries will be loaded
    :type country: int or Country or list or None
    :param location: a location or list of locations, either by id or object. If
                      not specified, all locations will be loaded
    :type location: int or Location or list or None
    :param brewery: a brewery or list of breweries, either by id or object. If
                      not specified, all breweries will be loaded
    :type brewery: int or Brewery or list or None
    :param nLimit: an integer limiting the number of rows to load. If not specified,
                   the function will try to load all rows returned from the query.
    :type nLimit: int
    :param sample: if set, will take a random (as defined by postgres) sample. Ignored if nLimit is not set
    :type sample: bool"""

    if conn is None:
        conn = psycopg2.connect(database='BeerDb', user='postgres',
                                password='postgres', host='localhost',
                                port=5432)

    def writeCondition(field, fieldValue, fieldType, pName):
        retField = fieldValue
        if type(fieldValue) == int:
            logicOper = ' = '
        elif type(fieldValue) == fieldType:
            logicOper = ' = '
            retField = fieldValue.id
        elif (isinstance(fieldValue, list) or
              isinstance(fieldValue, tuple)):
            logicOper = ' in '
            if type(fieldValue[0]) == int:
                retField = tuple(fieldValue)
            elif isinstance(continent[0], fieldType):
                retField = tuple([x.id for x in fieldValue])
            else:
                raise TypeError("{fType} list must be ints, or {fType}".format(fType=str(fieldType)))
        else:
            raise TypeError("{fType} must be int, str or {fType}".format(fType=str(fieldType)))
        return '         and {} {} %({})s'.format(field, logicOper, pName), retField

    #  Deal with parameters
    conditions = {}
    sql = ('select R."BEER_ID" as "beerId", R."USER_ID" as "userId", R."RATING_COMPOUND" as "ratingCompound",'
           '       R."RATING_AROMA" as "ratingAroma", R."RATING_APPEARANCE" as "ratingAppearance",'
           '       R."RATING_TASTE" as "ratingTaste", R."RATING_PALATE" as "ratingPalate",'
           '       R."RATING_OVERALL" as "ratingOverall", R."RATING_LOCATION" as "ratingLocation",'
           '       date(R."RATING_DATE") as "ratingDate", '
           '       convert_to(trim(both  from lower(unaccent(R."RATING_NOTES"))), \'utf8\') as "ratingNotes",'
           '       C."CONT_ID" as "contId", C."COUNTRY_ID" as "countryId", L."LOCATION_ID" as "locationId",'
           '       BR."BREWERY_ID" as "breweryId", B."BEER_NAME" as "beerName", B."BEER_STYLE_ID" as "beerStyleId",'
           '       B."BEER_STYLE_NAME" as "beerStyleName", B."BEER_CITY_ID" as "beerCityId",'
           '       B."BEER_CITY_NAME" as "beerCityName", B."BEER_ABV" as "beerAbv", B."BEER_IBU" as "beerIbu",'
           '       B."BEER_CALORIES" as "beerCalories", B."BEER_AVAIL_BOTTLE" as "beerAvailBottle",'
           '       B."BEER_AVAIL_TAP" as "beerAvailTap", B."BEER_SEASONAL" as "beerSeasonal",'
           '       B."BEER_OVERALL_RATING" as "beerOverallRating", B."BEER_AVG_RATING" as "beerAvgRating",'
           '       B."BEER_STYLE_RATING" as "beerStyleRating", B."BEER_NRATINGS" as "beerNratings",'
           '       B."BEER_DISTRIBUTION" as "beerDistribution", BR."BREWERY_NAME" as "breweryName",'
           '       BR."BREWERY_TYPE" as "breweryType", BR.NUMBER_BEERS as "numberBeers",'
           '       BR.YEAR_ESTABLISHED as "yearEstablished",'
           '       L."LOCATION_NAME" as "locationName", C."COUNTRY_NAME" as "countryName"'
           '   from tb_rating R,'
           '        tb_beer B,'
           '        tb_brewery BR,'
           '        tb_location L,'
           '        tb_country C'
           '   where C."COUNTRY_ID" = L."COUNTRY_ID"'
           '         and L."LOCATION_ID" = BR."LOCATION_ID"'
           '         and BR."BREWERY_ID" = B."BREWERY_ID"'
           '         and B."BEER_ID" = R."BEER_ID"')
    if continent is not None:
        cond, condValue = writeCondition('C."CONT_ID"', continent, Continent, 'p1')
        if cond is not None:
            sql = sql + cond
            conditions['p1'] = condValue
    if country is not None:
        cond, condValue = writeCondition('C."COUNTRY_ID"', country, Country, 'p2')
        if cond is not None:
            sql = sql + cond
            conditions['p2'] = condValue
    if location is not None:
        cond, condValue = writeCondition('L."LOCATION_ID"', location, Location, 'p3')
        if cond is not None:
            sql = sql + cond
            conditions['p3'] = condValue
    if brewery is not None:
        cond, condValue = writeCondition('BR."BREWERY_ID"', brewery, Brewery, 'p4')
        if cond is not None:
            sql = sql + cond
            conditions['p4'] = condValue
    if nLimit is not None:
        if sample:
            sql = sql + '   order by random()'
        sql = sql + '   limit %(p5)s'
        conditions['p5'] = nLimit

    sql = sql + ';'
    cur = conn.cursor()
    sql = cur.mogrify(sql, conditions)
    df = pandas.read_sql_query(sql, conn, coerce_float=True, params=None)
    df.set_index(['beerId', 'userId', 'ratingDate'], drop=False,
                 inplace=True, verify_integrity=True)
    return df


def usesVocab(wordList, vocabSet=beerVocab, cutOff=0.1, minGoodWords=3):
    """ Checks if a word list is actually using a specific vocabulary. If at least cutOff
    words in the list are contained in that vocabulary.
    :param wordList: The actual list of words to be checked
    :type wordList: list
    :param cutOff: the cutOff point. If the % of words in the list is >= cutOff, the list
                   is said to use that vocabulary
    :type cutOff: float
    :param vocabSet: the vocabulary to be checked against. Should be a set of strings
    :type vocabSet: set
    :param minGoodWords: the minimum number of words in the wordList that match the vocabulary
    :type minGoodWords: int
    :rtype bool """
    if not isinstance(wordList, list):
        if isgenerator(wordList):
            theList = list(wordList)
        else:
            raise ValueError
    else:
        theList = wordList
    lSize = len(theList)
    nRelevant = lSize - sum([1 for x in theList if x not in vocabSet])
    if lSize and nRelevant >= minGoodWords and float(nRelevant) / lSize >= cutOff:
        return True
    else:
        return False

numRE = re.compile(r'(\$?\d+(\.|,))?\d+(ml|oz|in|cm|cl|l|%)?')


def removeVocab(wordList, vocab=toRemove):
    """ Remove all the words on vocab from the wordList.
    :param wordList: the text to process, as a list of strings
    :type wordList: list of unicode
    :param vocab: the vocabulary to be removed, as a set of tokens
    :type vocab: set
    :rtype list  of unicode  """

    def isQuantityOrAmount(w):
        """ Determines if a token is a quantity or amount
        :param w: the word to be checked
        :type w: unicode
        """
        return numRE.match(w) is not None

    if isinstance(wordList, tuple):
        return [w for w in wordList if (w[0] not in vocab or isQuantityOrAmount(w[0]))]
    else:
        return [w for w in wordList if (w not in vocab or isQuantityOrAmount(w))]


def processBiGrams(stemList, wordList=None, biGramSet=beerNGrams):
    """ Transforms all BiGrams in word list from pairs of tokens into single tokens.
    :param stemList: the list of tokens
    :type stemList: list of unicode
    :param wordList: the list of words
    :type wordList: list of unicode
    :param biGramSet: the set of biGrams to evaluate against. They are strings, not tuples
    :type biGramSet: set of unicode
    :rtype tuple """
    newSList = []
    newWList = []
    consumed = False
    if wordList is None:
        wordList = stemList
    if isgenerator(stemList):
        stemList = list(stemList)
    if isgenerator(wordList):
        wordList = list(wordList)
    if len(stemList):
        for s1, s2, w1, w2 in izip(stemList[:-1], stemList[1:], wordList[:-1], wordList[1:]):
            if consumed:
                consumed = False
                continue
            if u'{} {}'.format(s1, s2) in biGramSet:
                newSList.append(u'{} {}'.format(s1, s2))
                newWList.append(u'{} {}'.format(w1, w2))
                consumed = True
            else:
                newSList.append(s1)
                newWList.append(w1)
        if not consumed:
            newSList.append(stemList[-1])
            newWList.append(wordList[-1])
    return newSList, newWList


def isQuantityOrAmount(w):
    """ Determines if a token is a quantity or amount
    :param w: the word to be checked
    :type w: unicode
    """
    return numRE.match(w) is not None


def tokenizer(d):
    """ Returns a list of stemmed tokens based on the text passed to the function.
        :param d: the text to be tokenized
        :type d: unicode
        :rtype list of unicode """
    if not len(d):
        return []
    l = [mystem(x.strip()) for x in utils.tokenize(d) if len(x.strip())]
    if usesVocab(l):
        l, _ = processBiGrams(l)
        return removeVocab(l)
    else:
        return []


def tokenizer2(d):
    """ Tokenizer that returns a dictionary of the stemmed tokens, with the list of words that were
        transformed into that token.
        :param d: the document (text) to be tokenized
        :type d: unicode
        :rtype dict of tuple """
    def myreducer(d, t):
        """ Receives a dictionary and a tuple of stem and word list. Adds {stem: [currList] + word list} to it.
        :param d: the dictionary
        :type d: dict
        :param t: the tuple, which should be (stem, word list)
        :type t: tuple
        :rtype dict """
        try:
            d[t[0]] += [t[1]]
        except KeyError:
            d[t[0]] = [t[1]]
        except:
            print t
            raise
        return d

    dic = {}
    if len(d):
        lW = [re.sub('[ _]*', ' ', w).strip() for w in utils.tokenize(d) if len(re.sub('[ _]*', ' ', w).strip())]
        print lW
        lS = [mystem(w) for w in lW]
        print lS
        lS, lW = processBiGrams(lS, lW)
        l = [(s, w) for s, w in  zip(lS, lW)]
        print l
        if len(l) and usesVocab([w[0] for w in l]):
            l2 = removeVocab(l)
            if len(l2):
                dic = reduce(myreducer, l2, {})
    return dic
