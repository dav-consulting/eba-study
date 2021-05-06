""" Assess a DAC criteria """
import os, json, time, random
import click
from spacy.matcher import Matcher
import pandas as pd
from collections import Counter
import operator
from util import (
    db_connect,
    load_jsonl,
    dump_jsonl,
    load_spacy_model,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    get_model_version_path,
    _NLP_FILES_PATH,
    _PARSED_FILES_PATH,
    _PROJECT_PATH,
)
from util import (
    _DAC_CRITERIA_VARIATIONS,
    _DAC_CRITERIA_VALUES_FROM_CODE,
    get_eba_2017_ids,
    get_eba2017,
)
from util import load_spacy_docbin_file as lsd, load_spacy_docbin_folder


_EXCLUDE_REGEX = [
    r"\?",
]
_EXCLUDE_GOALS = [
    [{"LOWER": "purpose"}],
    [{"LOWER": "goal"}],
    [{"LOWER": "objective"}],
    [{"TEXT": "?"}],
]
_EXCLUDE_ALL_CRITERIA_SPANS = [
    [{"LOWER": "relevance"}],
    [{"LOWER": "effectiveness"}],
    [{"LOWER": "efficiency"}],
    [{"LOWER": "sustainability"}],
]


def create_training_data(
    dac_criteria: str, model_version: str, include_sections: tuple = ("all")
):
    """ Prepares a json file of data for training and evaluation. """
    version_path, model_version = get_model_version_path(model_version=model_version)
    outpath = _PROJECT_PATH / f"q17/results/training_data/{dac_criteria}"
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    def exclude_tok(tok):
        exclude_toks = [
            tok.is_space,
            tok.is_bracket,
            tok.is_quote,
            tok.is_punct,
            not tok.is_ascii,
        ]
        return any(exclude_toks)

    patterns = [[{"LOWER": val}] for val in _DAC_CRITERIA_VARIATIONS[dac_criteria]]

    nlp = load_spacy_model(version_path / "meta.json")
    matcher_dac = Matcher(nlp.vocab)
    matcher_exclude = Matcher(nlp.vocab)
    matcher_exclude_all_criteria = Matcher(nlp.vocab)
    matcher_dac.add(dac_criteria, None, *patterns)
    matcher_exclude.add("goals", None, *_EXCLUDE_GOALS)
    matcher_exclude_all_criteria.add(
        "all_criteria", None, *_EXCLUDE_ALL_CRITERIA_SPANS
    )  # excludes sentence if all criteria are mentioned

    full_texts = []
    for pathobj, docbin, nlp in load_spacy_docbin_folder(model_version, nlp=nlp):
        print("Processing file: {}".format(pathobj.name))
        file_id = pathobj.name.replace("_content.bin", "")
        meta_file_path = _PARSED_FILES_PATH / f"{file_id}_meta.json"

        meta_file = load_jsonl(meta_file_path)
        sections = []
        if include_sections != ("all"):
            for midx, row in enumerate(meta_file):
                if any([sect in row.get("category", []) for sect in include_sections]):
                    start_idx = row["toc_match"]["content_idx"]
                    end_idx = (
                        meta_file[midx + 1]["toc_match"]["content_idx"]
                        if midx < len(meta_file) - 1
                        else None
                    )
                    sections.append((start_idx, end_idx))
        if len(sections) == 0:
            if len(meta_file) > 0:
                start_idx = meta_file[0]["toc_match"]["content_idx"]
            else:
                start_idx = 0
            sections.append((start_idx, None))
        docs = []
        for section in sections:
            for doc in docbin[section[0] + 1 : section[1]]:
                if doc._.props["type"] == "text":
                    docs.append(doc)

        match_sents = []
        for doc in docs:
            matches = matcher_dac(doc)
            match_start_ids = []

            for match_id, start, end in matches:
                string_id = nlp.vocab.strings[match_id]
                span = doc[start:end]
                sent = span.sent

                if sent.start not in match_start_ids:

                    exclude_matches = matcher_exclude(sent)
                    exclude_all_criteria_match = matcher_exclude_all_criteria(sent)
                    if (
                        len(exclude_all_criteria_match) < 4
                        and len(exclude_matches) == 0
                    ):
                        match_start_ids.append(sent.start)
                        match_sents.append(
                            " ".join(
                                [tok.lower_ for tok in sent if not exclude_tok(tok)]
                            )
                        )

        full_texts.append((file_id, ". ".join(match_sents)))

    include_sections_str = "_".join(include_sections)
    data_path = (
        outpath
        / f"data_{dac_criteria}_v{model_version}_include_sections_{include_sections_str}.jsonl"
    )
    dump_jsonl(
        full_texts, data_path,
    )
    return data_path


def create_gold_data_sustainability(data_path=None, seed=None):
     """ Prepares data for 5 fold cross evaluation. Stores each fold for training and evaluation in json files.  """
    print("Praparing training and test data for cross evaluation ")
    data = load_jsonl(data_path)
    data = {row[0]: row[1] for row in data}
    eba2017 = get_eba2017("f_id, Hallbarhet_id")
    texts = []
    cats = []
    cnt = {"sustainable": 0, "unsustainable": 0, "subsustainable": 0, "na": 0}
    for f_id, Hallbarhet_id in eba2017:
        cat = {"sustainable": 0, "unsustainable": 0, "subsustainable": 0, "na": 0}
        cat[Hallbarhet_id] = 1
        text = data.get(f_id) if len(data.get(f_id)) > 0 else "none"
        texts.append(text)
        cats.append(cat)

    data = list(zip(texts, cats))
    if seed:
        random.Random(seed).shuffle(data)

    train_data, test_data = [], []

    train, test = (
        {0: [], 1: [], 2: [], 3: [], 4: [],},
        {0: [], 1: [], 2: [], 3: [], 4: [],},
    )
    cnt = dict(Counter([k for d in cats for k, v in d.items() if v == 1]))

    test_bin_idx = {
        "sustainable": 0,
        "unsustainable": 0,
        "subsustainable": 0,
        "na": 0,
    }
    for d in data:
        category = max(d[1].items(), key=operator.itemgetter(1))[0]

        if len(test[test_bin_idx[category]]) < 27:
            test[test_bin_idx[category]].append(d)

        for key in train:
            if key != test_bin_idx[category] and len(test[key]) < 27:
                train[key].append(d)

        test_bin_idx[category] = (
            test_bin_idx[category] + 1 if test_bin_idx[category] < 4 else 0
        )

    for key in train:
        dump_jsonl(
            zip([t[0] for t in train[key]], [{"cats": t[1]} for t in train[key]]),
            data_path.parent / f"training{key}.jsonl",
        )
        dump_jsonl(
            zip([t[0] for t in test[key]], [{"cats": t[1]} for t in test[key]]),
            data_path.parent / f"evaluation{key}.jsonl",
        )

    # Calculate the performance of an algorithm which quesses based on the frequency of a labels occurence
    train_thresholds = {k: int(v * 0.8) for k, v in cnt.items()}
    for d in data:
        category = max(d[1].items(), key=operator.itemgetter(1))[0]
        if train_thresholds[category] > 0:
            train_data.append(d)
            train_thresholds[category] -= 1
        else:
            test_data.append(d)
    test_texts, test_cats = zip(*test_data)
    train_data_size = len(train_data)
    test_cnt = dict(Counter([k for d in test_cats for k, v in d.items() if v == 1]))
    print("Test count: ", test_cnt)

    train_texts, train_cats = zip(*train_data)
    train_cnt = dict(Counter([k for d in train_cats for k, v in d.items() if v == 1]))
    print("Train count: ", train_cnt)
    theoretical_correct_guess = sum(
        [
            test_cnt[tr_key] * tr_cnt / train_data_size
            for tr_key, tr_cnt in train_cnt.items()
        ]
    )
    print("Gold standard correct guess: ", theoretical_correct_guess)



def create_eval_data_sustainability_tp(data_path=None,):
    """ Create test data from third party evaluation """

    print("Creating test data from third party evals... ")
    data = load_jsonl(data_path.parent)
    data = {row[0]: row[1] for row in data}
    data_third_party = get_third_party("f_id, Hallbarhet_id")
    cnt = {"sustainable": 0, "unsustainable": 0, "subsustainable": 0, "na": 0}
    formated_data = []
    eba2017 = [row[0] for row in get_eba2017("f_id")]

    for f_id, Hallbarhet_id in data_third_party:
        if f_id in eba2017:
            continue
        cat = {"sustainable": 0, "unsustainable": 0, "subsustainable": 0, "na": 0}
        cat[Hallbarhet_id] = 1
        text = data.get(f_id) if len(data.get(f_id)) > 0 else "none"
        formated_data.append((text, {"cats": cat}))
    dump_jsonl(
        formated_data, input_dir.parent / f"third_party_eval.jsonl",
    )

@click.command()
@click.option(
    "--dac_criteria",
    default="sustainability",
    prompt="Input DAC criteria to assess.",
    type=click.Choice(["sustainability"]),
)
@click.option(
    "--model_version",
    default="-1",
    prompt="Which model version should be used?",
    type=int,
)
@click.option(
    "--include_sections",
    default="all",
    prompt="Which sections should be included?",
    type=str,
)
def main(dac_criteria, model_version, include_sections):
    """ Creates training data and stores from spaCy processed docs and stores. Data is prepared for a five fold cross validation by storing them in bins labelled training{kfold}.json and evaluation{kfold}.json. Also prepares a json file for third party evaluation.

    Note: currently the script is prepared towards the DAC criteria sustainability but can be modified to handle other DAC criteria. 
     """
    include_sections = include_sections.split(",")
    data_path = create_training_data(dac_criteria, model_version, include_sections)
    create_gold_data_sustainability(
        data_path=data_path, seed=None,
    )
    create_eval_data_sustainability_tp(data_path=data_path)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter

    main()
