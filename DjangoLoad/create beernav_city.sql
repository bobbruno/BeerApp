INSERT INTO "BeerNav_city"
SELECT 
  min(b."BEER_CITY_ID"), 
  b."BEER_CITY_NAME", 
  b."CONT_ID", 
  b."COUNTRY_ID", 
  b."LOCATION_ID",
  row_number() over(order by c."COUNTRY_NAME", b."BEER_CITY_NAME")
FROM 
  public.tb_beer b,
  public.tb_country c
WHERE 
  b."BEER_CITY_NAME" != 'None' and
  b."COUNTRY_ID" = c."COUNTRY_ID"
group by   b."BEER_CITY_NAME", 
  b."CONT_ID", 
  b."COUNTRY_ID", 
  c."COUNTRY_NAME",
  b."LOCATION_ID"
order by 6;

insert into "Beernav_city" values (0, 'Unknown', 0, 0, 0);
