import os, json, time, re
from collections import Counter
import operator
from collections import defaultdict
import click
from itertools import chain
from spacy.matcher import Matcher
from util import (
    load_spacy_docbin_folder,
    load_spacy_model,
    get_model_version_path,
    get_eba_evaluations,
    get_file_id,
    get_eba_2017_ids,
    get_eba2017,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    _DAC_CRITERIA_VARIATIONS,
)


def eba_2017_comparison():
    """ Method for comparing results to EBA2017 """
    eba_rows = get_eba2017("f_id, Tidsperiod")
    evaluations = get_eba_evaluations("_id, q6")
    results = []
    for row in eba_rows:
        f_id = row[0]
        eba_tidsperiod = row[1]
        if eba_tidsperiod:
            for eval_row in evaluations:
                # print(f_id, topic, pt[0])
                if eval_row[0] == f_id:
                    results.append((f_id, eba_tidsperiod, eval_row[1]))
    cnt_correct = 0
    for res in results:
        if res[1] == res[2]:
            cnt_correct += 1
        print(res[1] == res[2], res)
    print(f"Number of correct predictions: {cnt_correct} / {len(results)}")


@click.command()
@click.option(
    "--model_version",
    default="-1",
    prompt="Which model version should be used?",
    type=int,
)
def main(model_version):
    version_path, model_version = get_model_version_path(model_version=model_version)
    nlp = load_spacy_model(version_path / "meta.json")
    eba2017 = get_eba_2017_ids()
    print(f"Loading model version: {model_version}")
    create_eba_evaluations_column("q6")
    evaluation_years = {}
    for _, (file_path, docs, nlp) in enumerate(
        load_spacy_docbin_folder(
            model_version, nlp=nlp  # , include_only_ids=eba2017  # ["2017:13_22211"]
        )
    ):

        file_id = get_file_id(file_path)
        title, report_publ_date = get_eba_evaluations(
            "title, publ_date", where_clause=f"_id = '{file_id}'"
        )[0]
        if report_publ_date:
            report_publ_year = re.search("[2][0][012][0-9]", report_publ_date)
        doc_title = nlp(title)
        print(file_id, title)
        evaluation_years[file_id] = []

        doc_years, doc_year_intervalls = [], []
        intervall_in_title = False
        for doc_id, doc in enumerate(chain([doc_title], docs)):
            if (
                doc_id == 0
                or "executive_summary" in doc._.props.get("category", [])
                # or "introduction" in doc._.props.get("category", [])
                or "terms_of_reference" in doc._.props.get("category", [])
            ):
                sent_matches = []

                for sent_id, sent in enumerate(doc.sents):
                    prev_year = ()

                    for match in re.finditer(
                        "(19[89][0-9](?![\w])|20[01][0-9](?![\w]))", sent.text
                    ):
                        start, end = match.span()
                        year = sent.text[start:end]

                        # Capture also some year intervalls which are written as 2011-14
                        year_with_shorthand_dash = re.findall(
                            "(19[89][0-9][\s]*[\-][\s]*[0-9][0-9](?![\w])|20[01][0-9][\s]*[\-]*[0-9][0-9](?![\w]))",
                            sent.text[start:],
                        )
                        if year_with_shorthand_dash:
                            doc_years.append(
                                year_with_shorthand_dash[0][0:2]
                                + year_with_shorthand_dash[0][-2:]
                            )

                        doc_years.append(year)

                        if len(prev_year) > 0 and prev_year[1] - start > -20:
                            doc_year_intervalls.append((int(prev_year[0]), int(year)))
                            if doc_id == 0:
                                intervall_in_title = True
                                break
                            # print(doc._.props.get("category", []), doc_year_intervalls)

                        prev_year = (year, end)
                        sent_matches.append((doc_id, sent_id))
                if intervall_in_title:
                    break

        if len(doc_year_intervalls) > 1:
            year_intervall_cnt = dict(Counter(doc_year_intervalls))
            print(year_intervall_cnt)
            year_cnt = Counter(doc_years).most_common()
            _, year_cnts = zip(*year_cnt)
            print(year_cnt)

            year_counts_in_intervall = {
                year_intervall: 0
                for year_intervall, year_cnt in dict(year_intervall_cnt).items()
            }
            year_counts_in_intervall = defaultdict(int)
            for val in year_cnt:
                for year_intervall, year_cnt in year_intervall_cnt.items():
                    year_intervall = tuple(sorted(year_intervall))
                    if year_intervall[0] <= int(val[0]) <= year_intervall[1]:
                        year_counts_in_intervall[year_intervall] += val[1]

            most_common_year_intervalls = [
                k
                for k, v in sorted(
                    year_counts_in_intervall.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            ]
            print(most_common_year_intervalls)
            # most_common_year_cnts = sorted(set(year_cnts), reverse=True)[0:2]
            # print("most_common_year_cnts", most_common_year_cnts)
            # most_common_years = sorted(
            #     [int(y[0]) for y in year_cnt if y[1] in most_common_year_cnts]
            # )
            # print(most_common_years)
            # most_common_year_intervalls = sorted(
            #     [
            #         interv
            #         for interv in doc_year_intervalls
            #         if interv[0] in most_common_years and interv[1] in most_common_years
            #     ],
            #     key=lambda x: x[1] - x[0],
            #     reverse=True,
            # )
            # if len(most_common_year_intervalls) == 0:
            #     most_common_year_intervalls = [
            #         max(doc_year_intervalls, key=lambda x: x[1] - x[0])
            #     ]
            # # print(year_intervall_cnt, "---", year_cnt)

        else:
            most_common_year_intervalls = doc_year_intervalls
        print("most_common_year_intervalls: ", most_common_year_intervalls)
        if len(most_common_year_intervalls) > 0:
            final_year = (
                min(int(report_publ_year.group(0)), most_common_year_intervalls[0][1])
                if report_publ_year
                else most_common_year_intervalls[0][1]
            )
            most_common_year_intervall_str = (
                f"{most_common_year_intervalls[0][0]}-{final_year}"
            )
            update_eba_evaluations_column(
                "q6", most_common_year_intervall_str, primary_key=file_id
            )
        print("")
    eba_2017_comparison()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter

    main()
    #

    # eba_2017_comparison()

