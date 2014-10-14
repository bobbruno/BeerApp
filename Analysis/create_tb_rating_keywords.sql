
truncate table tb_rating_keywords;
insert into tb_rating_keywords 
select x.beer_id, x.user_id, x.rating_date, array_agg(x.stem_present)
from
(select r.beer_id, r.user_id, r.rating_date, s.word_stem, (s.word_stem = any (r.rating_words))::int as stem_present
    from tb_stem_dict s,
         tb_rating_notes as r
    where s.is_keyword
    order by 1, 2, 3, 4) as x
    group by 1, 2, 3

select array_dims(array_agg) from tb_rating_keywords limit 100

select l.word_stem
   from (select word_stem from tb_stem_dict where is_keyword) l
   where l.word_stem not in (select unnest(rating_words) from tb_rating_notes)

select distinct C."COUNTRY_NAME" from tb_beer B, TB_COUNTRY C where B."COUNTRY_ID" = C."COUNTRY_ID" AND B."BEER_ID" in (select beer_id from tb_beer_features)