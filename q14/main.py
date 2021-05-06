import os, json, time, re
from collections import Counter
import operator
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
    eba_rows = get_eba2017("f_id, Nar_utv")
    evaluations = get_eba_evaluations("_id, q14")
    results = []
    for row in eba_rows:
        f_id = row[0]
        eba_phase = row[1]
        if eba_phase:
            for eval_row in evaluations:
                # print(f_id, topic, pt[0])
                if eval_row[0] == f_id:
                    results.append((f_id, eba_phase, eval_row[1]))
    cnt_correct = 0
    for res in results:
        print(res)
        if res[1] in res[2]:
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
    matcher = Matcher(nlp.vocab)
    mid_term_patterns = [
        [{"LOWER": "midterm"},],
        [{"LOWER": "mid"}, {"LOWER": "term"},],
        [{"LOWER": "mid"}, {"LOWER": "-"}, {"LOWER": "term"},],
    ]
    matcher.add("mid_term", None, *mid_term_patterns)
    end_term_patterns = [
        [
            {"LOWER": "end"},
            {"LOWER": "-"},
            {"LOWER": "of"},
            {"LOWER": "-"},
            {"LOWER": "phase"},
        ],
        [{"LOWER": "end"}, {"LOWER": "of"}, {"LOWER": "phase"}],
        [
            {"LOWER": "end"},
            {"LOWER": "-"},
            {"LOWER": "of"},
            {"LOWER": "-"},
            {"LOWER": "term"},
        ],
        [{"LOWER": "end"}, {"LOWER": "of"}, {"LOWER": "term"}],
        [
            {"LOWER": "end"},
            {"LOWER": "-"},
            {"LOWER": "of"},
            {"LOWER": "-"},
            {"LOWER": "project"},
        ],
        [{"LOWER": "end"}, {"LOWER": "of"}, {"LOWER": "project"}],
    ]
    matcher.add("mid_term", None, *mid_term_patterns)

    eba2017 = get_eba_2017_ids()
    print(f"Loading model version: {model_version}")
    create_eba_evaluations_column("q14")
    silence_updates = True
    for _, (file_path, docs, nlp) in enumerate(
        load_spacy_docbin_folder(model_version, nlp=nlp)
    ):
        file_id = get_file_id(file_path)
        midterm_match_found = False
        endphase_match_found = False
        # include_only_ids=["2014:43_15480"]
        title, eval_time_period, report_publ_date = get_eba_evaluations(
            "title, q6, publ_date", where_clause=f"_id = '{file_id}'"
        )[0]
        report_publ_year = re.search("[2][0][012][0-9]", report_publ_date)
        if report_publ_year:
            report_publ_year = report_publ_year.group(0)
        if eval_time_period:
            eval_year0, eval_year1 = eval_time_period.split("-")
        doc_title = nlp(title)

        # print(file_id, title)

        for doc_id, doc in enumerate(chain([doc_title], docs)):
            if (
                doc_id == 0
                or "executive_summary" in doc._.props.get("category", [])
                or "introduction" in doc._.props.get("category", [])
                or "terms_of_reference" in doc._.props.get("category", [])
            ):
                matches = matcher(doc)
                for match_id, start, end in matches:
                    string_id = nlp.vocab.strings[match_id]  # Get string representation
                    if string_id == "mid_term" and doc_id == 0:
                        print(0, string_id, doc)
                        update_eba_evaluations_column(
                            "q14",
                            "mid-term",
                            primary_key=file_id,
                            silence=silence_updates,
                        )
                        midterm_match_found = True
                        break
                    elif string_id == "mid_term":
                        if report_publ_year and eval_time_period:
                            if (
                                int(eval_year0)
                                <= int(report_publ_year)
                                <= int(eval_year1)
                            ):
                                print(string_id, doc)
                                update_eba_evaluations_column(
                                    "q14",
                                    "mid-term",
                                    primary_key=file_id,
                                    silence=silence_updates,
                                )
                                midterm_match_found = True
                                break
                    elif string_id == "end_of_phase":
                        print(string_id, doc)
                        update_eba_evaluations_column(
                            "q14",
                            "end-of-phase",
                            primary_key=file_id,
                            silence=silence_updates,
                        )
                        endphase_match_found = True
            if midterm_match_found or endphase_match_found:
                break
        if not any([midterm_match_found, endphase_match_found]):
            if report_publ_year and eval_time_period:
                if int(eval_year0) < int(report_publ_year) < int(eval_year1):
                    update_eba_evaluations_column(
                        "q14", "mid-term", primary_key=file_id, silence=silence_updates
                    )
                    midterm_match_found = True
                else:
                    update_eba_evaluations_column(
                        "q14",
                        "end-of-phase",
                        primary_key=file_id,
                        silence=silence_updates,
                    )
            else:
                update_eba_evaluations_column(
                    "q14", "end-of-phase", primary_key=file_id, silence=silence_updates,
                )


if __name__ == "__main__":
    main()
    # eba_2017_comparison()
