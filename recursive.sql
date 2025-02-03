-- PostgreSQL 15.10 (Debian 15.10-0+deb12u1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit


-- Bellman–Ford implementation for finding all shortest paths, including negative cost cycles.
WITH RECURSIVE
  edge_costs AS (
    SELECT 'u' AS source, 'v' AS target, 10 AS edge_cost
    UNION ALL
    SELECT 'v' AS source, 'w' AS target, 5 AS edge_cost
    UNION ALL
    SELECT 'u' AS source, 'w' AS target, 20 AS edge_cost
    UNION ALL
    SELECT 'x' AS source, 'y' AS target, -10 AS edge_cost
    UNION ALL
    SELECT 'y' AS source, 'x' AS target, -10 AS edge_cost
  ),
  nodes AS (
    SELECT DISTINCT node
    FROM
      (
        SELECT DISTINCT source AS node FROM edge_costs
        UNION ALL
        SELECT DISTINCT target AS node FROM edge_costs
      ) AS node_list
  ),
  path_costs AS (
    SELECT 0 AS i, source, target, edge_cost AS path_cost FROM edge_costs
    UNION ALL
    SELECT
      0 AS i,
      source.node AS source,
      target.node AS target,
      CASE
        WHEN source.node = target.node THEN CAST(0 AS float)
        ELSE CAST('Infinity' AS float)
        END
        AS path_cost
    FROM nodes AS source
    CROSS JOIN nodes AS target
    UNION ALL
    SELECT
      path_costs.i + 1 AS i,
      edge_costs.source AS source,
      path_costs.target AS target,
      edge_costs.edge_cost + path_costs.path_cost AS path_cost
    FROM edge_costs
    JOIN path_costs
      ON edge_costs.target = path_costs.source
    WHERE path_costs.i <= (SELECT COUNT(*) FROM nodes)
  ),
  aggregated_path_costs AS (
    SELECT
      source,
      target,
      MIN(
        CASE
          WHEN path_costs.i < (SELECT COUNT(*) FROM nodes) THEN path_cost
          ELSE CAST('Infinity' AS float)
          END)
        AS previous_path_cost,
      MIN(path_cost) AS path_cost
    FROM path_costs
    GROUP BY 1, 2
  )
SELECT
  source,
  target,
  CASE
    WHEN previous_path_cost = path_cost THEN path_cost
    ELSE -CAST('Infinity' AS float)
    END
    AS path_cost
FROM aggregated_path_costs
ORDER BY 1, 2;

/*
 source | target | path_cost
--------+--------+-----------
 u      | u      |         0
 u      | v      |        10
 u      | w      |        15
 u      | x      |  Infinity
 u      | y      |  Infinity
 v      | u      |  Infinity
 v      | v      |         0
 v      | w      |         5
 v      | x      |  Infinity
 v      | y      |  Infinity
 w      | u      |  Infinity
 w      | v      |  Infinity
 w      | w      |         0
 w      | x      |  Infinity
 w      | y      |  Infinity
 x      | u      |  Infinity
 x      | v      |  Infinity
 x      | w      |  Infinity
 x      | x      | -Infinity
 x      | y      | -Infinity
 y      | u      |  Infinity
 y      | v      |  Infinity
 y      | w      |  Infinity
 y      | x      | -Infinity
 y      | y      | -Infinity
(25 rows)
*/


-- BFS implementation for solving sudoku
WITH RECURSIVE
  substitution_points(s) AS (SELECT 1 UNION ALL SELECT s + 1 FROM substitution_points WHERE s < 81),
  digits(d) AS (SELECT 1 UNION ALL SELECT d + 1 FROM digits WHERE d < 9),
  digits_chars(d) AS (SELECT d::text FROM digits),
  row_pairs(fst, snd)
  AS (
    SELECT fst.s, snd.s
    FROM substitution_points AS fst, substitution_points AS snd
    WHERE fst.s != snd.s AND (fst.s - 1) / 9 = (snd.s - 1) / 9
  ),
  col_pairs(fst, snd)
  AS (
    SELECT fst.s, snd.s
    FROM substitution_points AS fst, substitution_points AS snd
    WHERE fst.s != snd.s AND (fst.s - 1) % 9 = (snd.s - 1) % 9
  ),
  box_pairs(fst, snd)
  AS (
    SELECT fst.s, snd.s
    FROM substitution_points AS fst, substitution_points AS snd
    WHERE
      fst.s != snd.s
      AND ((fst.s - 1) / 9) / 3 = ((snd.s - 1) / 9) / 3
      AND ((fst.s - 1) % 9) / 3 = ((snd.s - 1) % 9) / 3
  ),
  all_pairs(fst, snd)
  AS (
    SELECT fst, snd
    FROM row_pairs UNION
    SELECT fst, snd
    FROM col_pairs UNION
    SELECT fst, snd
    FROM box_pairs
  ),
  sudoku_states(i, puzzle)
  AS (
    SELECT 1, '023450789089023456056789103312805967097310845845097012230574098068201574504908201'
    UNION ALL
    SELECT
      i + 1,
      CASE
        WHEN substring(puzzle FROM i FOR 1) = '0' THEN overlay(puzzle placing d FROM i FOR 1)
        ELSE puzzle
        END
    FROM sudoku_states, digits_chars
    WHERE
      i <= 81
      AND NOT EXISTS(SELECT * FROM all_pairs WHERE fst = i AND substring(puzzle FROM snd FOR 1) = d)
  )
SELECT puzzle AS solved_puzzle FROM sudoku_states ORDER BY i DESC LIMIT 1;

/*
                                   solved_puzzle
-----------------------------------------------------------------------------------
 123456789789123456456789123312845967697312845845697312231574698968231574574968231
(1 row)
*/
