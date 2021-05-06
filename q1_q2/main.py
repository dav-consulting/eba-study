import pandas as pd
import os, json
from pathlib import Path
import re
import sqlite3
from util import _PARSED_FILES_PATH, db_connect


_SERIES_NUM_PATTERN = r"[2][0][0-2][0-9][\:][0-9]+([:][\w]+)?"
_YEAR_NUM_PATTERN = r"^[2][0][0-2][0-9]"
_SERIES_TYPES = ["Sida Review", "Sida Decentralised Evaluation", "Sida Evaluation"]


def main():
    """ Extracts title and series number from parsed pdf's. """
    cnt_no_eval = 0
    extracted_results = {}
    for idx, file in enumerate(
        sorted(os.listdir(_PARSED_FILES_PATH), key=lambda x: x[-3:], reverse=True)
    ):
        if file.endswith("_content.json"):
            print("{}: {}".format(idx, file))
            data = []
            valid_json = False
            with open(os.path.join(_PARSED_FILES_PATH, file), "r") as f:
                for line in f:
                    line = line.rstrip("\n|\r")
                    try:
                        data.append(json.loads(line))
                        valid_json = True
                    except json.decoder.JSONDecodeError as e:
                        print("invalid json: {}".format(file))
                        valid_json = False
                        break

                if valid_json:
                    eval_title = ""
                    eval_strings = []
                    eval_string = ""

                    # Iterate over the contents of the first page in the pdf
                    for _, row in enumerate(data):
                        if row.get("page_id", -1) > 0:
                            break

                        # Get eval type
                        # Note: Almots all evaluations start with defining type. Exceptions do occur see e.g. 2017:08_22155_pdf.pdf
                        if row["text"] in _SERIES_TYPES:
                            extracted_results[file] = {"series": row["text"]}
                            continue

                        # Join all text strings on first page excluding the authors which have color code: 16777215
                        if file in extracted_results.keys():
                            if 16777215 != row.get("color"):
                                eval_string += row["text"]
                                eval_strings.append(row["text"])
                            else:
                                eval_strings.append(None)

                    # Extract series number using regex
                    series_match = re.search(_SERIES_NUM_PATTERN, eval_string)
                    series_number = series_match.group()
                    series_number_list = series_number.split(":")

                    # Locate title based on where series_number was found
                    match_idx = (
                        None  # idx where series number is found or author list starts
                    )
                    for ii, text in enumerate(eval_strings):
                        if text:
                            if series_number in text:
                                match_idx = ii
                            elif re.search(
                                r"^{}(:|$)".format(series_number_list[0]), text
                            ):
                                match_idx = ii
                        else:
                            match_idx = ii

                        if not match_idx is None:
                            break

                    # if match_idx == 0 then the series number appears first in the string else last
                    if match_idx == 0 and text:
                        eval_title = " ".join([e for e in eval_strings[1:] if e])
                    else:
                        eval_title = " ".join(eval_strings[:match_idx])

                    extracted_results[file]["eval_title"] = eval_title
                    extracted_results[file]["series_num"] = series_number
                    if eval_string:  # year_num_text:
                        # print(file, series_number, eval_title)
                        pass
                    else:
                        print(file, "NO EVAL NUM!")
                        cnt_no_eval += 1
    print("Num of files without eval number:", cnt_no_eval)

    conn, curr = db_connect()
    try:
        curr.execute("ALTER TABLE eba_evaluations ADD COLUMN title TEXT;")
    except sqlite3.OperationalError as e:
        print("Column already exists?! ", str(e))

    try:
        curr.execute("ALTER TABLE eba_evaluations ADD COLUMN series TEXT;")
    except sqlite3.OperationalError as e:
        print("Column already exists?! ", str(e))

    try:
        curr.execute("ALTER TABLE eba_evaluations ADD COLUMN series_number TEXT;")
    except sqlite3.OperationalError as e:
        print("Column already exists?! ", str(e))

    for k, val in extracted_results.items():
        doc_id = k.replace("_content", "").replace(".json", "")
        try:
            sql_str = "UPDATE eba_evaluations SET title='{}', series='{}', series_number='{}' WHERE _id='{}'".format(
                val["eval_title"], val["series"], val["series_num"], doc_id
            )
            curr.execute(sql_str)
        except Exception as e:
            print(val)
            print(e)
        assert curr.rowcount == 1, "No rows where UPDATED!!"
        print("Successfully updated: {}".format(doc_id))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Run from project to level
    # python -m q1_q2.extract_titles_and_series_numbers
    main()
