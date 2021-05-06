import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import sqlite3
from util import db_connect, _EBA_FILE_PATH


def main():
    """ Matches SIDA evaluations analyzed in EBA 2017:12 to evaluations downloaded from SIDA's publication platform """

    conn, cur = db_connect()
    cur.execute(
        "SELECT _id, title, series_number FROM eba_evaluations ORDER BY series_number"
    )
    rows = cur.fetchall()
    db_keys, pdf_titles, pdf_series_number = zip(*rows)

    try:
        cur.execute("ALTER TABLE eba_evaluations ADD COLUMN eba_match_nr INTEGER;")
        cur.execute("ALTER TABLE eba_evaluations ADD COLUMN eba_match_title TEXT;")
    except sqlite3.OperationalError as e:
        print("Columns already exists?! ", str(e))
        cur.execute(
            "UPDATE eba_evaluations SET eba_match_title=null, eba_match_nr=null"
        )
        conn.commit()

    assert len(pdf_titles) == len(set(pdf_titles))
    pdf_titles = [title.lower().replace("final report", "") for title in pdf_titles]

    print("Start matching...")
    eba_data = pd.read_excel(_EBA_FILE_PATH)
    cnt_matches = 0
    added_ids = dict()
    for _, row in eba_data.iterrows():
        best_match = True
        eba_title = row[eba_data.columns[0]].replace("\n", " ").strip()
        eba_nr = row[eba_data.columns[1]]
        eba_year = row[eba_data.columns[2]]

        partial_ratio = process.extractOne(
            eba_title.lower().replace("final report", ""),
            pdf_titles,
            scorer=fuzz.partial_ratio,
            score_cutoff=50,
        )
        db_id = db_keys[pdf_titles.index(partial_ratio[0])]
        partial_series_year = int(
            pdf_series_number[pdf_titles.index(partial_ratio[0])].split(":")[0]
        )

        if db_id in added_ids.keys():
            print("Duplicate id found: ", db_id)
            print(partial_ratio[1] < added_ids[db_id][1])
            if partial_ratio[1] < added_ids[db_id][1]:
                best_match = False
            else:
                added_ids[db_id] = (partial_ratio[0], partial_ratio[1])
        else:
            added_ids[db_id] = (partial_ratio[0], partial_ratio[1])

        if partial_ratio and best_match and partial_series_year == eba_year:
            cnt_matches += 1
            sql_str = "UPDATE eba_evaluations SET eba_match_title='{}', eba_match_nr={} WHERE _id='{}'".format(
                eba_title, eba_nr, db_id
            )
            cur.execute(sql_str)
        elif not best_match:
            print(
                "Title {} with score {} has a better match...".format(
                    partial_ratio[0], partial_ratio[1]
                )
            )
        else:
            print("Unable to match: {}".format(eba_title))
            print("partial_ratio: ", partial_ratio)
            print("partial_series_year: ", partial_series_year, eba_year)
        conn.commit()

    print("Number of EBA matches: {}".format(cnt_matches))

    conn.close()


if __name__ == "__main__":
    # Run from project to level
    # python -m match_to_eba_report.eba_match
    main()
