from multiprocessing import Process, Queue, Pool
from gensim import corpora, models, similarities, utils
from Analysis.analysis import *

texts=[]
def getText(l):
    texts += l

def tokenizer(d):
    l = list(utils.tokenize(d))
    if usesVocab(l):
        return l

if __name__ == '__main__':
    n = 6
    my_results = Queue()
    
    pool =  Pool(processes=n)
    for d in documents:
        texts = pool.apply_async(tokenizer, args=(d,), callback=getText)
    pool.close()
    pool.join
    print texts[:100]