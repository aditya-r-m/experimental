with recursive
substitution_points(s) as (
  select 1 union all select s+1 from substitution_points where s < 81
),
digits(d) as (
  select 1 union all select d+1 from digits where d < 9
),
digits_chars(d) as (
  select d :: text from digits
),
row_pairs(fst, snd) as (
  select fst.s, snd.s from substitution_points as fst, substitution_points as snd
  where fst.s != snd.s
    and (fst.s - 1) / 9 = (snd.s - 1) / 9
),
col_pairs(fst, snd) as (
  select fst.s, snd.s from substitution_points as fst, substitution_points as snd
  where fst.s != snd.s
    and (fst.s - 1) % 9 = (snd.s - 1) % 9
),
box_pairs(fst, snd) as (
  select fst.s, snd.s from substitution_points as fst, substitution_points as snd
  where fst.s != snd.s
    and ((fst.s - 1) / 9) / 3 = ((snd.s - 1) / 9) / 3
    and ((fst.s - 1) % 9) / 3 = ((snd.s - 1) % 9) / 3
),
all_pairs(fst, snd) as (
  select fst, snd from row_pairs
  union select fst, snd from col_pairs
  union select fst, snd from box_pairs
),
sudoku_states(i, puzzle) as (
  select 1, '023450789089023456056789103312805967097310845845097012230574098068201574504908201'
  union all
  select
    i+1,
    case
      when substring(puzzle from i for 1) = '0'
      then overlay(puzzle placing d from i for 1)
      else puzzle
    end
  from sudoku_states, digits_chars
  where i <= 81
    and not exists (select * from all_pairs where fst = i and substring(puzzle from snd for 1) = d)
)
select puzzle from sudoku_states order by i desc limit 1;
-- (PostgreSQL 13.0) 123456789789123456456789123312845967697312845845697312231574698968231574574968231
