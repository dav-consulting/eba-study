#!/usr/bin/env python
import click
import re
import random
import os
import numpy as np
import json
from pathlib import Path
from collections import Counter
import thinc.extra.datasets
import spacy
import torch
from spacy.util import minibatch
import tqdm
import unicodedata
import wasabi
from spacy_transformers.util import cyclic_triangular_rate
from util import load_jsonl, dump_jsonl, get_eba2017, get_third_party, _PROJECT_PATH

from spacy.util import decaying
from collections import Counter
import operator


def eval_model(
    model_dir=_PROJECT_PATH / "q17/results/training_output/",
    data_dir=_PROJECT_PATH / "q17/results/data/sustainability/",
    kfold="",
    third_party_eval_only=False,
):
    print("Evaluate model from: ", model_dir)
    nlp = spacy.load(model_dir)
    eval_results = dict()
    best_preds = []
    true_cats = []
    if third_party_eval_only:
        eval_data = [
            f"third_party_eval.jsonl",
        ]
    else:
        eval_data = [f"training{kfold}.jsonl", f"evaluation{kfold}.jsonl"]
    for path_obj in data_dir.iterdir():
        if path_obj.name in eval_data:
            correct_preds = 0
            eval_dataset = load_jsonl(path_obj)
            num_rows = len(eval_dataset)
            for row in eval_dataset:
                doc = nlp(row[0])
                labels = row[1]
                best_pred = max(doc.cats, key=doc.cats.get)
                best_preds.append(best_pred)
                true_cat = max(labels["cats"], key=labels["cats"].get)
                if true_cat == best_pred:
                    correct_preds += 1
                true_cats.append(true_cat)
            eval_results[path_obj.name] = {
                "correct_preds": correct_preds,
                "total_preds": num_rows,
            }
            print(f"`{path_obj.name}` prediction score: {correct_preds} / {num_rows} ")
    correct_preds, total_preds = zip(
        *[(r["correct_preds"], r["total_preds"]) for r in eval_results.values()]
    )
    print(f"Total score all files: {sum(correct_preds)} / {sum(total_preds)} ")
    print("Prediction_dist: ", Counter(best_preds))
    print("Actual_dist: ", Counter(true_cats))
    print("")
    return eval_results


def cross_fold_eval(
    model_dir=_PROJECT_PATH / "q17/results/training_output/",
    eval_dir=_PROJECT_PATH / "q17/results/data/sustainability/",
    third_party_eval_only=False,
):
    """ Perform cross-fold evaluation """
    for i in range(5):
        eval_model(
            model_dir=model_dir / f"v{i}",
            data_dir=eval_dir,
            kfold=i,
            third_party_eval_only=third_party_eval_only,
        )


@click.command()
@click.option(
    "--model_dir",
    default=_PROJECT_PATH / "q17/results/training_output/",
    prompt="Model directory.",
    type=str,
)
@click.option(
    "--eval_dir",
    default=_PROJECT_PATH / "q17/results/data/sustainability/",
    prompt="Evaluation file directory.",
    type=str,
)
@click.option(
    "--third_party_eval_only",
    default=1,
    prompt="Evaluate only based on third party results.",
    type=int,
)
def main(model_dir, eval_dir, third_party_eval_only):
    """ Evaluate model on evaluation and training data. """
    cross_fold_eval(
        model_dir=model_dir,
        eval_dir=eval_dir,
        third_party_eval_only=bool(third_party_eval_only),
    )


if __name__ == "__main__":
    main()
