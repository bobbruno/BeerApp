DROP TABLE TB_USER;
CREATE UNLOGGED TABLE TB_USER as
insert into tb_user
SELECT 
  tb_rating."USER_ID" as user_id, 
  tb_rating."USER_NAME" as user_name, 
  max(substring(substring(tb_rating."RATING_LOCATION" from ' \S+$') from 2)) as user_country,
  min(tb_rating."RATING_COMPOUND") min_compound,
  max(tb_rating."RATING_COMPOUND") max_compound,
  avg(tb_rating."RATING_COMPOUND") avg_compound,
  stddev(tb_rating."RATING_COMPOUND") std_compound,
  min(tb_rating."RATING_OVERALL") min_overall, 
  max(tb_rating."RATING_OVERALL") max_overall, 
  avg(tb_rating."RATING_OVERALL") avg_overall, 
  stddev(tb_rating."RATING_OVERALL") std_overall, 
  min(tb_rating."RATING_AROMA") min_aroma, 
  max(tb_rating."RATING_AROMA") max_aroma, 
  avg(tb_rating."RATING_AROMA") avg_aroma,
  stddev(tb_rating."RATING_AROMA") std_aroma,
  min(tb_rating."RATING_APPEARANCE") min_appearance, 
  max(tb_rating."RATING_APPEARANCE") max_appearance, 
  avg(tb_rating."RATING_APPEARANCE") avg_appearance, 
  stddev(tb_rating."RATING_APPEARANCE") std_appearance, 
  min(tb_rating."RATING_TASTE") min_taste, 
  max(tb_rating."RATING_TASTE") max_taste, 
  avg(tb_rating."RATING_TASTE") avg_taste, 
  stddev(tb_rating."RATING_TASTE") std_taste, 
  min(tb_rating."RATING_PALATE") min_palate, 
  max(tb_rating."RATING_PALATE") max_palate, 
  avg(tb_rating."RATING_PALATE") avg_palate, 
  stddev(tb_rating."RATING_PALATE") std_palate, 
  min(tb_rating."RATING_DATE") min_date,
  max(tb_rating."RATING_DATE") max_date,
  COUNT(*) as n_ratings,
  sum(("RATING_COMPOUND">3.5)::int) as n_good_ratings
FROM 
  public.tb_rating
GROUP BY
  1, 2;
ALTER TABLE tb_user
  OWNER TO "Django_beer";
alter table tb_user add constraint pk_user PRIMARY KEY(user_id) USING INDEX tablespace "Beer_ix";