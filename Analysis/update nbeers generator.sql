SELECT 
  'UPDATE tb_brewery set number_beers = ',count(tb_beer."BEER_ID") as nBeers,
  '   where "BREWERY_ID" = ', tb_brewery."BREWERY_ID", '&'
FROM 
  public.tb_brewery, 
  public.tb_beer
WHERE 
  tb_beer."BREWERY_ID" = tb_brewery."BREWERY_ID"
GROUP BY tb_brewery."BREWERY_ID"