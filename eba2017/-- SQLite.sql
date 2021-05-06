-- SQLite
-- SELECT _id,  series_number,  eba_match_nr, q11, Sakomrade
-- FROM eba2017 LEFT JOIN `eba_evaluations` ON eba_match_nr=Nr WHERE f_id IS NOT NULL;

SELECT _id,  series_number,  eba_match_nr, q9, _Finansiar
FROM eba2017 LEFT JOIN `eba_evaluations` ON eba_match_nr=Nr WHERE f_id IS NOT NULL AND _Sida_roll IS NOT NULL;

--SELECT eba2017.f_id,  eba2017._Sida_roll, eba2017_third_party._Sida_roll
--FROM eba2017_third_party LEFT JOIN `eba2017` ON eba2017.f_id=eba2017_third_party.f_id WHERE eba2017.f_id IS NOT NULL;

-- SELECT * FROM eba2017;