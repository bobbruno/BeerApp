INSERT INTO "BeerNav_brewery"
SELECT 
  b."BREWERY_ID", 
  b."CONT_ID", 
  b."COUNTRY_ID", 
  b."LOCATION_ID", 
  b.number_beers, 
  b."BREWERY_NAME", 
  b."BREWERY_TYPE", 
  row_number() over (order by c."COUNTRY_NAME", b."BREWERY_NAME"),
  b.year_established
FROM 
  public.tb_brewery b,
  public.tb_country c
WHERE
  b."COUNTRY_ID" = c."COUNTRY_ID"
