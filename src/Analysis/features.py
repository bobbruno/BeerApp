'''
Created on 14/10/2014

@author: bobbruno
'''

from collections import defaultdict
import psycopg2
import pylab
from random import randint
from scipy import ndimage
from skimage.io import imread
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud

from Analysis.analysis import appearanceWords, aromaWords, palateWords, flavorWords
from Analysis.analysis import loadDF, tokenizer2, tokenizer, toRemove, mystem
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def my_color_func(word, font_size, position, orientation, random_state=None):
    if random_state is None:
        random_state = randint
    word = mystem(word)
    if word in appearanceWords:
        hue = random_state(10, 41)
    elif word in aromaWords:
        hue = random_state(62, 93)
    elif word in palateWords:
        hue = random_state(114, 145)
    elif word in flavorWords:
        hue = random_state(166, 197)
    else:
        hue = random_state(218, 245)
    return "hsl(%d, 80%%, 50%%)" % hue


def readDb(minBeer, maxBeer):
    with psycopg2.connect(database='BeerDb', user='postgres', password='postgres', host='localhost', port=5432) as conn:
        sql = '''select r.beer_id, s.word_stem,
           sum((s.word_stem = any (r.rating_words))::int)::float / count(*)  as stemPercent
        from tb_stem_dict s,
             (select * from tb_rating_notes where beer_id between %s and %s) as r
        where s.is_keyword
        group by 1, 2
        order by 1, 2'''
        return pd.read_sql_query(sql, conn, coerce_float=True,
                                 params=(minBeer, maxBeer))

if __name__ == '__main__':

    #  Load basic data
    dfsub = loadDF()
    documents = [unicode(str(note).decode('utf8')) for note in dfsub.ratingNotes]

    from multiprocessing import Process, Queue, Pool, cpu_count

    #  Tokenize texts
    texts = []
    allWordCount = 0

    n = cpu_count() + 2
    pool = Pool(processes=n)
    results = []
    for d in documents:
        results.append(pool.apply_async(tokenizer2, args=(d,)))
    for i, r in enumerate(results):
        try:
            texts.append(r.get())
            allWordCount += len(texts[-1])
        except:
            print i
            pool.close()
            pool.join()
            pool.terminate()
            raise
    pool.close()
    pool.join()
    pool.terminate()

    #  Count frequent words
    vect = CountVectorizer(decode_error=u'ignore', lowercase=False, tokenizer=tokenizer,
                           stop_words=list(toRemove), min_df=0.02, max_df=0.96)
    countMatrix = vect.fit_transform(documents)
    wordList = np.array(vect.get_feature_names())
    countMatrix2 = countMatrix / float(countMatrix.max())
    counts = []
    maxCount = countMatrix.sum(axis=0).max()
    for i, w in enumerate(wordList):
        c = countMatrix[:, vect.vocabulary_.get(w)].sum()
        for t in texts:
            if w in t:
                w2 = t[w][0]
                break
        print '{}: {}'.format(w2, c)
        counts.append((w2, c / maxCount))

    #  Save the Results
    #  Rating Notes
    with psycopg2.connect(database='BeerDb', user='postgres', password='postgres', host='localhost', port=5432) as conn:
        cur = conn.cursor()
        cur.execute('truncate table tb_rating_notes')
        ratingNotes = []
        allWords = defaultdict(lambda: set())
        blockSize = 10000
        for i, index in enumerate(dfsub.index.values):
            ratingNotes.append(index + (texts[i].keys(),))
            for k, v in texts[i].iteritems():
                allWords[k] = allWords[k].union(set(v))
            if i and not i % blockSize:
                cur.executemany('insert into tb_rating_notes values(%s, %s, %s, %s)', ratingNotes)
                ratingNotes = []
                conn.commit()
        if len(ratingNotes):
            cur.executemany('insert into tb_rating_notes values(%s, %s, %s, %s)', ratingNotes)
            ratingNotes = []
            conn.commit()
    #  Stem and word dictionaries
    with psycopg2.connect(database='BeerDb', user='postgres', password='postgres', host='localhost', port=5432) as conn:
        cur = conn.cursor()
        cur.execute('truncate table tb_stem_dict')
        toWrite = []
        for i, (k, v) in enumerate(allWords.iteritems()):
            toWrite += [(k, list(v))]
            if i and not i % blockSize:
                cur.executemany('insert into tb_stem_dict values(%s, %s)', toWrite)
                toWrite = []
                conn.commit()
        if len(toWrite):
            cur.executemany('insert into tb_stem_dict values(%s, %s)', toWrite)
            conn.commit()
        myList = [(w,) for w in wordList]
        cur.executemany('update tb_stem_dict set is_keyword = true where word_stem = %s', myList)
        myList = []
        conn.commit()
        cur.execute('truncate table tb_word_dict')
        cur.execute('insert into tb_word_dict select distinct unnest(word_list) as word, word_stem from tb_stem_dict')
        conn.commit()

    nBlocks = 30
    nBeers = 286806
    blockSize = nBeers // nBlocks
    dfList = Parallel(n_jobs=10)(delayed(readDb)(i * blockSize, (i + 1) * blockSize - 1) for i in xrange(nBlocks + 1))
    dfBeer = pd.concat(dfList)
    dfBeer = dfBeer.pivot(index='beer_id', columns='word_stem', values='stempercent')
    with psycopg2.connect(database='BeerDb', user='postgres', password='postgres', host='localhost', port=5432) as conn:
        cur = conn.cursor()
        try:
            sql = u'CREATE TABLE TB_BEER_STEM_PERCENT (BEER_ID integer not null,\n\t' + \
                  ' double precision,\n\t'.join(dfBeer.columns) + ' double precision)'
            cur.execute(sql)
        except:
            conn.commit()
            sql = 'truncate table TB_BEER_STEM_PERCENT'
            cur.execute(sql)
            conn.commit()
        blockSize = 10000
        record = []
        sql = u'%s,' * 207
        sql = u'insert into TB_BEER_STEM_PERCENT values(' + sql
        sql = sql[:-1] + u')'
        for i in dfBeer.index.values:
            record.append((i,) + tuple(dfBeer.loc[i]))
            if i and not i % blockSize:
                #  print sql
                cur.executemany(sql, record)
                record = []
                conn.commit()
        if len(record):
            cur.executemany(sql, record)
            record = []
            conn.commit()    #  Generate a word cloud
    beer_mask = imread("/home/bobbruno/BeerApp/Analysis/beer-glass-mask.png", as_grey=True)
    beer_mask.shape
    pylab.rcParams['figure.figsize'] = (30.0, 40.0)
    wc = WordCloud(width=800, height=500, background_color='white', ranks_only=False,
                   #  font_path='/usr/share/fonts/truetype/msttcorefonts/Verdana.ttf',
                   color_func=my_color_func, mask=beer_mask, prefer_horizontal=0.1)
    wc.fit_words(counts)
    wc2 = ndimage.rotate(wc, -60, cval=255)
    plt.imshow(wc2)
    plt.tight_layout()
    plt.axis("off")
    plt.show()
