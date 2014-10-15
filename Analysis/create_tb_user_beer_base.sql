create table features.tb_user_beer_base as 
SELECT 
  tb_rating."USER_ID" as user_id,
  avg(tb_beer."BEER_ABV") as beer_abv,
  avg(tb_beer."BEER_IBU") as beer_ibu, 
  avg(tb_beer."BEER_CALORIES") as beer_calories
FROM 
  public.tb_beer, 
  public.tb_rating, 
  public.tb_user_style_percent
WHERE 
  tb_beer."BEER_ID" = tb_rating."BEER_ID" AND
  tb_user_style_percent.user_id = tb_rating."USER_ID" AND
  tb_rating."RATING_COMPOUND" >= 3.5
GROUP BY
  1