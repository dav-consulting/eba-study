import json, os
import numpy as np

import click
from util import (
    load_jsonl,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    get_eba2017,
    get_eba_2017_ids,
    get_eba_evaluations,
    get_section_text,
    get_eba2017_adjusted_probability_score,
)
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")


from eba2017.util import topic_similarities, topic_similarity_words
from util import (
    _NLP_FILES_PATH,
    _PARSED_FILES_PATH,
    _EMBEDDINGS_MODEL_PATH,
    load_jsonl,
    eba_2017_comparison,
)

import numpy as np



@click.command()
@click.option(
    "--files_to_run", default="eba2017", prompt="Run eba2017 or all?",
)
def main_v3(files_to_run):
    """ Calculates which of the EBA2017 topics (Sakområden) is most similar to the evaluation title using the Zero-shot learning algorithm.  

    Note: Requires transformers version > 3.1 which is not compatible with spacy-transformers requirement <2.9
    """

    if files_to_run == "eba2017":
        eval_titles = get_eba_evaluations(
            "_id, title, eba_match_nr", where_clause="eba_match_title IS NOT NULL"
        )
    else:
        eval_titles = get_eba_evaluations("_id, title, eba_match_nr", where_clause=None)

    predicted_topics = []
    classifier = pipeline("zero-shot-classification", tokenizer=tokenizer, model=model)
    topics_key_word_pairs = {
        item: key
        for key, topics_words in topic_similarity_words.items()
        for item in topics_words
    }
    topics_words = list(topics_key_word_pairs.keys())
    print(topics_words)
    for row in eval_titles:
        file_id = row[0]
        title_doc = row[1]
        eba_match_nr = row[2]
        sim_scores = []

        sequence = title_doc  # + " ".join(sequence_data)
        res = classifier(sequence, topics_words, multi_class=True)
        best_topic, best_score = (
            topics_key_word_pairs[res["labels"][0]],
            res["scores"][0],
        )
        if best_score < 0.4:
            best_topic = "Flera områden i samma"
        print(file_id, eba_match_nr, best_topic, round(best_score, 3))
        predicted_topics.append((file_id, best_topic))

    if files_to_run == "eba2017":
        eba_2017_comparison("Sakomrade", predicted_topics)

    upd = input("Update eba_evaluations table? (y/n)")
    if upd == "y":
        create_eba_evaluations_column("q11")
        for pred in predicted_topics:
            update_eba_evaluations_column("q11", pred[1], pred[0], silence=True)


if __name__ == "__main__":
    # Run: python -m q11.zero_shot

    # Probability adjusted theoretical scores can be calculated using:
    # theoretical_outcomes = get_eba2017_adjusted_probability_score("Sakomrade")
    # print(theoretical_outcomes)

    main_v3()

    