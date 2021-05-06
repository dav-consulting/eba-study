import os, json
import pandas as pd
import re
from collections import Counter
from util import db_connect, _PROJECT_PATH, get_eba2017

column_translate = {
    "Hallbarhet_id": "q17",
    "_Land": "q3",
    "_Region": "q4",
    "_Geografi": "q5",
    "Sakomrade": "q11",
    "I_sammanfattning": "q23",
    "Tidsperiod": "q6",
    "Forslag": "q24_q25",
    "Nar_utv": "q14",
    "_Sida_roll": "q21",
    "_Finansiar": "q9",
    "_Bistandsberoende": "q22",
    "I_sammanfattning_relevance": "q23_relevance",
    "I_sammanfattning_effectiveness": "q23_effectiveness",
    "I_sammanfattning_efficiency": "q23_efficiency",
    "I_sammanfattning_impacts": "q23_impacts",
    "Forslag_relevance": "q24_q25_relevance",
    "Forslag_effectiveness": "q24_q25_effectiveness",
    "Forslag_efficiency": "q24_q25_efficiency",
    "Forslag_impacts": "q24_q25_impacts",
}
reverse_column_translate = {
    "q17": "Hallbarhet_id",
    "q3": "_Land",
    "q4": "_Region",
    "q5": "_Geografi",
    "q11": "Sakomrade",
    "q23": "I_sammanfattning",
    "q6": "Tidsperiod",
    "q24_q25": "Forslag",
    "q14": "Nar_utv",
    "q21": "_Sida_roll",
    "q9": "_Finansiar",
    "q22": "_Bistandsberoende",
    "q23_relevance": "I_sammanfattning_relevance",
    "q23_effectiveness": "I_sammanfattning_effectiveness",
    "q23_efficiency": "I_sammanfattning_efficiency",
    "q23_impacts": "I_sammanfattning_impacts",
    "q24_q25_relevance": "Forslag_relevance",
    "q24_q25_effectiveness": "Forslag_effectiveness",
    "q24_q25_efficiency": "Forslag_efficiency",
    "q24_q25_impacts": "Forslag_impacts",
}

eba_columns = [
    "f_id",
    "Nr",
    "Hallbarhet_id",
    "_Land",
    "_Region",
    "_Geografi",
    "Sakomrade",
    "I_sammanfattning",
    "Tidsperiod",
    "Forslag",
    "Nar_utv",
    "_Finansiar",
    "_Sida_roll",
    "_Bistandsberoende",
]
eba_eval_columns = [
    "_id",
    "q3",
    "q4",
    "q5",
    "q6",
    "q9",
    "q11",
    "q14",
    "q17",
    "q21",
    "q22",
    "q23",
    "q24_q25",
]

geografi_translate = {
    "Country/local": "nationellt/lokalt",
    "Region": "regionalt",
    "Global": "global",
}


region_lookup = {
    "afrikasos": [
        "Middle Africa",
        "Western Africa",
        "Southern Africa",
        "Eastern Africa",
    ],
    "öst/syd och centralasien": [
        "Southern Asia",
        "Polynesia",
        "Australia and New Zealand",
        "South-Eastern Asia",
        "Eastern Asia",
        "Melanesia",
        "Micronesia",
        "Central Asia",
    ],
    "öst- och centraleuropa": [
        "Northern Europe",
        "Southern Europe",
        "Western Europe",
        "Eastern Europe",
        "Western Asia",
    ],
    "syd - och latinamerika": ["Caribbean", "South America", "Central America"],
    "mena": ["Northern Africa"],
}

reverse_region_lookup = {
    "Northern Europe": "öst- och centraleuropa",
    "Southern Europe": "öst- och centraleuropa",
    "Western Europe": "öst- och centraleuropa",
    "Eastern Europe": "öst- och centraleuropa",
    "Western Asia": "öst- och centraleuropa",
    "Middle Africa": "afrikasos",
    "Western Africa": "afrikasos",
    "Southern Africa": "afrikasos",
    "Eastern Africa": "afrikasos",
    "Southern Asia": "öst/syd och centralasien",
    "Polynesia": "öst/syd och centralasien",
    "Australia and New Zealand": "öst/syd och centralasien",
    "South-Eastern Asia": "öst/syd och centralasien",
    "Eastern Asia": "öst/syd och centralasien",
    "Melanesia": "öst/syd och centralasien",
    "Micronesia": "öst/syd och centralasien",
    "Central Asia": "öst/syd och centralasien",
    "Caribbean": "syd - och latinamerika",
    "South America": "syd - och latinamerika",
    "Central America": "syd - och latinamerika",
    "Northern Africa": "mena",
}


def compare_land(eval_data, source_data):
    """ Computes the correlation between the two categories"""
    matches = []
    if eval_data and source_data:
        d1 = [e.lower() for e in eval_data.split("; ") if e.lower() != "none"]
        d2 = [s.lower() for s in source_data.split("; ") if s.lower() != "none"]
        eval_data = d1 if len(d1) < len(d2) else d2
        source_data = d1 if len(d1) >= len(d2) else d2

        # eval_data = eval_data + (len(source_data) - len(eval_data)) * ["none"]
        for e in eval_data:
            if e in source_data:
                matches.append(1)
            else:
                matches.append(0)

        return sum(matches) / len(source_data)
    else:
        return 0


def get_region(eval_data):
    # subregions = region_lookup.get(source_region)
    eval_data = eval_data.split(";")

    source_regions = set()
    for e in eval_data:
        region = reverse_region_lookup.get(e)
        if region and len(region) > 0:
            source_regions.add(region)
    if len(source_regions) > 2:
        return ["global"]
    elif len(source_regions) == 1:
        return list(source_regions)
    else:
        return [None]


def print_averages(avg):
    df = pd.DataFrame(columns=["q", "name", "val"])
    for idx, row in avg.iteritems():
        if idx == "Nr" or idx == "_id":
            continue

        if "q" == idx[0]:
            df = df.append(
                {
                    "q": column_translate.get(idx, idx),
                    "name": reverse_column_translate.get(idx, idx),
                    "val": round(100 * row, 2),
                },
                ignore_index=True,
            )
        else:
            df = df.append(
                {
                    "q": column_translate.get(idx, idx),
                    "name": reverse_column_translate.get(idx, idx),
                    "val": round(100 * row, 2),
                },
                ignore_index=True,
            )
    print(df)


def main():
    # eba2017 = get_eba2017("*")
    conn, cur = db_connect()
    df = pd.read_sql_query("SELECT * FROM eba2017 WHERE f_id IS NOT NULL", conn)
    df_tp = pd.read_sql_query("SELECT * FROM eba2017_third_party;", conn)

    # Dataframe for comparing eba2017 and third party results (should contains all rows present in both eba2017 and eba2017_third_party)
    df_eba_vs_tp = pd.DataFrame(columns=eba_columns)

    # Dataframe for comparing eba2017 and machine based results (should contain all rows present in both eba2017 and eba_evaluations)
    df_eba_vs_ee = pd.DataFrame(columns=eba_eval_columns)

    # Dataframe for comparing third party and machine based results
    df_tp_vs_ee = pd.DataFrame(columns=eba_eval_columns)

    df_random = pd.DataFrame(columns=["q", "name", "empiric. random", "pure random"])
    for col in eba_columns:
        if col in ["f_id", "Nr", "_Land", "Tidsperiod"]:
            continue
        cnt = dict(Counter(df[col].dropna().tolist()))
        sum_cnt = sum(cnt.values())
        size = len(cnt)
        exp_val = 0
        for _, v in cnt.items():
            exp_val += v * v / sum_cnt
        df_random = df_random.append(
            {
                "q": column_translate[col],
                "name": col,
                "empiric. random": round(100 * exp_val / sum_cnt, 2),
                "pure random": round(100 / size, 2),
            },
            ignore_index=True,
        )
        # print(col, cnt, sum_cnt, round(exp_val, 2), round(exp_val / sum_cnt, 3))
    print(df_random)

    pd.set_option("display.max_columns", 99)
    pd.set_option("display.max_rows", 30)

    # compare EBA2017 to Third party + Machine
    for idx, row in df.iterrows():
        _id = row["f_id"]
        df_tp = pd.read_sql_query(
            "SELECT * FROM eba2017_third_party WHERE f_id='{}'".format(_id), conn
        )
        df_ee = pd.read_sql_query(
            "SELECT * FROM eba_evaluations WHERE _id='{}'".format(_id), conn
        )
        eba_vs_tp = {"f_id": _id, "Nr": row["Nr"]}
        eba_vs_ee = {"_id": _id, "Nr": row["Nr"]}
        for q in column_translate:

            # Compares EBA to Third Party
            if len(df_tp) > 0 and q in df_tp.columns and q in df.columns:
                if q == "_Land":
                    eba_vs_tp[q] = compare_land(df_tp[q].iloc[0], row[q])
                else:
                    eba_vs_tp[q] = (
                        df_tp[q].iloc[0] == row[q] if row[q] is not None else None
                    )

            # Compares EBA to Machine (note: Comparison with machine results require column translation)
            if (
                len(df_ee) > 0
                and column_translate[q] in df_ee.columns
                and q in df.columns
            ):
                # Hallbarhet is evaluated based on test data so not included in comparison
                if q == "Hallbarhet_id":
                    continue
                if q == "_Geografi":
                    eba_val = geografi_translate.get(df_ee[column_translate[q]].iloc[0])

                    eba_vs_ee[column_translate[q]] = (
                        row[q] == eba_val if row[q] is not None else None
                    )
                elif q == "_Land":
                    eba_vs_ee[column_translate[q]] = compare_land(
                        df_ee[column_translate[q]].iloc[0], row[q]
                    )
                elif q == "_Region":
                    eval_regions = get_region(df_ee[column_translate[q]].iloc[0])
                    score = sum([row[q] == er for er in eval_regions]) / len(
                        eval_regions
                    )
                    eba_vs_ee[column_translate[q]] = score

                else:
                    eba_val = row[q]
                    eba_vs_ee[column_translate[q]] = (
                        df_ee[column_translate[q]].iloc[0] == eba_val
                        if row[q] is not None
                        else None
                    )

        if len(df_tp) > 0:
            # Note: None values denote data not available
            df_eba_vs_tp = df_eba_vs_tp.append(eba_vs_tp, ignore_index=True)

        if len(df_ee) > 0:
            # Note: None values denote data not available
            df_eba_vs_ee = df_eba_vs_ee.append(eba_vs_ee, ignore_index=True)

    print("Compare EBA to Third Party")
    print_averages(df_eba_vs_tp.mean())
    print("")
    print("Compare EBA to Machine")
    print_averages(df_eba_vs_ee.mean())

    # Compare Third party to Machine
    c9, c21 = 0, 0
    df_tp = pd.read_sql_query("SELECT * FROM eba2017_third_party;", conn)
    for idx, row in df_tp.iterrows():
        _id = row["f_id"]
        df_ee = pd.read_sql_query(
            "SELECT * FROM eba_evaluations WHERE _id='{}'".format(_id), conn
        )
        ee_vs_tp = {"f_id": _id}

        for q in column_translate:

            if len(df_ee) > 0 and column_translate[q] in df_ee.columns:
                if q == "_Geografi":
                    eba_val = geografi_translate.get(df_ee[column_translate[q]].iloc[0])

                    ee_vs_tp[column_translate[q]] = (
                        row[q] == eba_val if row[q] is not None else None
                    )
                elif q == "_Land":
                    ee_vs_tp[column_translate[q]] = compare_land(
                        df_ee[column_translate[q]].iloc[0], row[q]
                    )
                elif q == "_Region":
                    eval_regions = get_region(df_ee[column_translate[q]].iloc[0])
                    score = sum([row[q] == er for er in eval_regions]) / len(
                        eval_regions
                    )
                    ee_vs_tp[column_translate[q]] = score

                else:

                    eba_val = row[q]
                    # if column_translate[q] in ["q9", "q21"]:
                    #     print(
                    #         column_translate[q],
                    #         _id,
                    #         eba_val,
                    #         df_ee[column_translate[q]].iloc[0],
                    #         df_ee[column_translate[q]].iloc[0] == eba_val,
                    #     )
                    #     c9 += df_ee[column_translate[q]].iloc[0] == eba_val
                    #     c21 += df_ee[column_translate[q]].iloc[0] == eba_val

                    ee_vs_tp[column_translate[q]] = (
                        df_ee[column_translate[q]].iloc[0] == eba_val
                        if row[q] is not None
                        else None
                    )
        if len(df_ee) > 0:
            # Note: None values denote data not available
            df_tp_vs_ee = df_tp_vs_ee.append(ee_vs_tp, ignore_index=True)

    print(c9, c21)
    print("")
    print("Compare Third party to Machine")
    print_averages(df_tp_vs_ee.mean())


if __name__ == "__main__":
    main()
