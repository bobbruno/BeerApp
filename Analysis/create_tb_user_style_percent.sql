DROP TABLE TB_USER_STYLE_PERCENT;
create unlogged table features.tb_user_style_percent1 as
select  R."USER_ID" as user_id,
        B."BEER_STYLE_ID" as style_id,
        avg(R."RATING_COMPOUND")/5 as pct_style
from tb_beer B, tb_rating R
where B."BEER_ID" = R."BEER_ID" AND
--      R."USER_ID" = 144019
      R."USER_ID" IN (SELECT user_id from tb_user_stem_percent)
group by R."USER_ID", B."BEER_STYLE_ID";

insert into features.tb_user_style_percent1
select user_id, style_id, 0.5 from 
(
	select sp.user_id, sl.style_id
	   from (select distinct user_id from features.tb_user_style_percent1) sp,
		(SELECT UNNEST(array[  2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,
		15,  16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,
		28,  29,  31,  35,  36,  37,  39,  40,  41,  42,  44,  45,  48,
		52,  53,  54,  55,  56,  57,  58,  59,  60,  61,  62,  63,  64,
		65,  71,  72,  73,  74,  75,  76,  77,  78,  79,  80,  81,  82,
	       100, 101, 102, 103, 105, 106, 107, 113, 114, 115, 116, 117, 118, 121]) style_id) sl
	except
	select user_id, style_id from features.tb_user_style_percent1
) s;