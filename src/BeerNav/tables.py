'''
Created on 21/10/2014

@author: bobbruno
'''
from django_tables2.utils import Accessor

from BeerNav.models import Beer
import django_tables2 as tables


class MyAcessor(Accessor):
    SEPARATOR = ';'

class BeerTable(tables.Table):
    '''
    Implements (hopefully) a table of beers.
    '''
    class Meta:
        model = Beer
        sequence = ('rank', 'name', 'brewery', 'country', 'style', 'overallRating', 'ABV')
        fields = sequence
        attrs = {'class': 'table'}

    def ranker(self, key):
        return self.table_data[key]
    rank = tables.Column('Rank', self.ranker, visible=True, orderable=True)

