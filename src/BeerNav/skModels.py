'''
Created on 21/10/2014

@author: bobbruno
'''

import psycopg2
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

import cPickle as pickle
import numpy as np
import pandas as pd


def loadBeerData():
    with psycopg2.connect(database='BeerDb', user='django_beer', password='MyNextBeer',
                          host='localhost', port=5432) as conn:
        sql = 'select * from features.tb_beer_pca'
        dfBeer = pd.read_sql_query(sql, conn, coerce_float=True)
        dfBeer.set_index('beer_id', inplace=True)
        knn = NearestNeighbors(10).fit(dfBeer)
        return dfBeer, knn


def get_nearest(userPos, nBeers=10):
    """ Returns the nBeers nearest to the userPos set of coordinates.
    :param userPos: The set of coordinates on the PCA space that the user chose.
    :type userPos: dict
    :param nBeers: The number of nearest beers to be returned
    :type nBeers: int """
    userPCA = np.ones(20)
    for k, v in userPos.iteritems():
        userPCA[int(k[1:]) - 1] = float(v)
    _, theBeers = knn.kneighbors(userPCA, nBeers)
    return list(dfBeerData.index[theBeers[0]])

beerPCA = pickle.load(open('static/pca.pkl'))
beerKM = pickle.load(open('static/kmeans.pkl'))
dfBeerData, knn = loadBeerData()