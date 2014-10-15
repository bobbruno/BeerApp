SELECT pid, query, query_start, waiting FROM pg_stat_activity where state = 'active' AND datname = 'BeerDb'


