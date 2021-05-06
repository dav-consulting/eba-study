""" Assess a DAC criteria """
import os, json, time
import click
import operator
from collections import Counter
from transformers import pipeline
import random
from util import (
    db_connect,
    load_jsonl,
    load_spacy_model,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    _NLP_FILES_PATH,
    _PARSED_FILES_PATH,
    _PROJECT_PATH,
)
from util import (
    _DAC_CRITERIA_VARIATIONS,
    _DAC_CRITERIA_VALUES_FROM_CODE,
    update_eba_evaluations_column,
    get_eba_2017_ids,
    get_eba2017,
    get_eba_evaluations,
    eba_2017_comparison,
)


@click.command()
@click.option(
    "--file_name",
    default=_PROJECT_PATH
    / "q17/results/data/sustainability/data_sustainability_v11_include_sections_all.jsonl",
    prompt="Input data path.",
    type=str,
)
def main(file_name):
    """ Evaluate sentiment of text extracts of sentences mentioning sustainability, sustainable or similar for the EBA2017:12 dataset. """
    classifier = pipeline("sentiment-analysis")
    data = load_jsonl(file_name)
    for row in data:
        _id = row[0]
        text = row[1]
        sentiment = classifier(text)

        assert len(sentiment) == 1
        label = sentiment[0]["label"]
        score = sentiment[0]["score"]
        if score < 0.75:
            category = "na"
        elif score > 0.9 and label == "POSITIVE":
            category = "sustainable"
        elif score > 0.9 and label == "NEGATIVE":
            category = "unsustainable"
        else:
            category = "subsustainable"

        update_eba_evaluations_column(
            "q17", update_value=category, primary_key=_id, silence=True
        )

    eba_2017_comparison("Hallbarhet_id", "q17")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()

