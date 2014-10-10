select min("BEER_NRATINGS"), max("BEER_NRATINGS"), avg("BEER_NRATINGS"), stddev("BEER_NRATINGS") from tb_beer

select * from tb_beer where "BEER_NRATINGS" > 3000

select b."BEER_STYLE_NAME", avg("RATING_COMPOUND"), stddev("RATING_COMPOUND")
   from tb_beer B, tb_rating R
   where b."BEER_ID" = r."BEER_ID"
   group by b."BEER_STYLE_NAME"
   order by 3 desc

select b."BEER_ID", r."USER_ID", b."BEER_STYLE_NAME", r."RATING_COMPOUND"
   from tb_beer B, tb_rating R
   where b."BEER_ID" = r."BEER_ID"
   and b."BEER_STYLE_NAME" = 'Malt Liquor'
   order by 1, 4