CREATE TABLE features.tb_beer_style_percent1
(
   LIKE public.tb_beer_style_percent INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES INCLUDING STORAGE
) 
WITH (
  OIDS = FALSE,
  autovacuum_enabled = false
)
;
ALTER TABLE features.tb_beer_style_percent1
  OWNER TO "Django_beer";

insert into features.tb_beer_style_percent1
   select * from public.tb_beer_style_percent;

select * from features.tb_user_style_percent1 where user_id = 144019 order by style_id