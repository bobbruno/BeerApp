'''
Created on 21/10/2014

@author: bobbruno
'''
from BeerNav.models import Beer
import django_tables2 as tables


class BeerTable(tables.Table):
    '''
    Implements (hopefully) a table of beers.
    '''
    class Meta:
        model = Beer
        sequence = ('rank', 'name', 'brewery', 'country', 'style', 'overallRating', 'ABV')

    rank = tables.Column('Rank', 'rank', visible=True, orderable=True, order_by=u'rank')