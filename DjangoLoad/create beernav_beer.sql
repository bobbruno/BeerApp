-- Needs to change beer_city_id to 0 where name is 'None' (maybe create city_id 0, too).
INSERT INTO "BeerNav_beer"
SELECT 
  B."BEER_ID", 
  B."BEER_ABV", 
  B."BEER_IBU", 
  B."BEER_AVAIL_BOTTLE", 
  B."BEER_AVAIL_TAP", 
  B."BEER_AVG_RATING", 
  B."BEER_CALORIES", 
  B."BEER_CITY_ID", 
  B."CONT_ID", 
  B."COUNTRY_ID", 
  B."BEER_DISTRIBUTION", 
  B."LOCATION_ID", 
  B."BEER_NRATINGS", 
  B."BEER_NAME", 
  B."BEER_OVERALL_RATING", 
  B."BEER_SEASONAL", 
  B."BEER_STYLE_ID", 
  B."BEER_STYLE_RATING", 
  B."BREWERY_ID",
  row_number() over (order by br."BREWERY_NAME", b."BEER_STYLE_ID", b."BEER_NAME")
FROM 
  public.tb_beer B,
  public.tb_brewery BR
WHERE
  B."BREWERY_ID" = BR."BREWERY_ID";
