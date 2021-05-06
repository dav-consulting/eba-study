import json, os
import numpy as np

import click
from util import (
    load_spacy_model,
    load_jsonl,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    get_eba2017,
    get_eba_2017_ids,
    get_eba_evaluations,
    get_section_text,
)
from transformers import pipeline
from eba2017.util import topic_similarities, topic_similarity_words
from util import _NLP_FILES_PATH, _EMBEDDINGS_MODEL_PATH
import spacy
import numpy as np
import spacy_sentence_bert


def load_word2vec(model_name="model_w8_m5_i12.kv"):
    w2v_model_path = _EMBEDDINGS_MODEL_PATH / model_name
    word_vectors = kv.load(str(w2v_model_path), mmap="r")
    return word_vectors


def gen_similar_topics(nr_of_topics=20):
    glove = api.load("glove-wiki-gigaword-50")
    topics_sim = {}
    for key, values in topics.items():
        # val_cnts = len(values)
        topic_keywords = [val.lower() for val in values]
        topics_sim[key] = topic_keywords
        similarities = []
        for topic_keyword in topic_keywords:
            topn = glove.most_similar(positive=[topic_keyword], topn=nr_of_topics)
            top_words, _ = zip(*topn)
            similarities.append(list(top_words))

        topic_keyword_idx = 0
        while len(topics_sim[key]) < nr_of_topics:
            i_word = 0
            while similarities[topic_keyword_idx][i_word] in topics_sim[key]:
                continue
            topics_sim[key].append(similarities[topic_keyword_idx][i_word])
            similarities[topic_keyword_idx].pop(0)
            if topic_keyword_idx < len(topic_keywords) - 1:
                topic_keyword_idx += 1
            else:
                topic_keyword_idx = 0

        # topics_per_val = int(nr_of_topics / val_cnts)
        val_cnts
    print(result)


def eba_2017_comparison(predicted_topics):
    rows = get_eba2017("f_id, Sakomrade")
    results = []
    for row in rows:
        f_id = row[0]
        topic = row[1]
        for pt in predicted_topics:
            # print(f_id, topic, pt[0])
            if f_id and pt[0].strip() == f_id.strip():
                results.append((f_id, row[1], pt[1]))
    cnt_correct = 0
    for res in results:
        if res[1] == res[2]:
            cnt_correct += 1
        print(res[1] == res[2], res)
    print(f"Number of correct predictions: {cnt_correct} / {len(results)}")


@click.command()
@click.option(
    "--files_to_run", default="eba2017", prompt="Run eba2017 or all?",
)
def main_v2(files_to_run):
    """ Calculates which of the EBA2017 topics (Sakområden) is most similar to the evaluation title.  
    Note: Requires transformers version > 3.1 which is not compatible with spacy-transformers requirement <2.9
    """

    if files_to_run == "eba2017":
        eval_titles = get_eba_evaluations(
            "_id, title, eba_match_nr", where_clause="eba_match_title IS NOT NULL"
        )
    else:
        eval_titles = get_eba_evaluations("_id, title, eba_match_nr", where_clause=None)
    nlp = spacy_sentence_bert.load_model("en_roberta_large_nli_stsb_mean_tokens")
    predicted_topics = []
    for row in eval_titles:
        file_id = row[0]
        title_doc = nlp(row[1])
        eba_match_nr = row[2]
        sim_scores = []
        for key, topics_words in topic_similarity_words.items():
            for phrase in topics_words:
                topic_doc = nlp(phrase)
                sim_score = topic_doc.similarity(title_doc)
                sim_scores.append((key, sim_score))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        best_topic, best_score = sim_scores[0][0], sim_scores[0][1]

        if (
            abs(sim_scores[0][1] - sim_scores[1][1]) / sim_scores[0][1]
            < 0.2
            # and sim_scores[0][1] < 0.35
        ):
            best_topic = "Flera områden i samma"
        print(
            file_id, eba_match_nr, best_topic, [round(s[1], 4) for s in sim_scores][0:5]
        )
        predicted_topics.append((file_id, best_topic))
    if files_to_run == "eba2017":
        eba_2017_comparison(predicted_topics)

    upd = input("Update eba_evaluations table? (y/n)")
    if upd == "y":
        create_eba_evaluations_column("q11")
        for pred in predicted_topics:
            update_eba_evaluations_column("q11", pred[1], pred[0])


@click.command()
@click.option(
    "--model_version",
    default=-1,
    prompt="Which version number should be used for storing results?",
)
@click.option(
    "--files_to_run", default="eba2017", prompt="Run eba2017 or all?",
)
def main_v1(model_version, files_to_run):
    """ This solution version computes similaritires between the topics and document keywords exttracted using TF-IDF vectors. """
    if model_version > 0:
        version_path = _NLP_FILES_PATH / "v{}".format(model_version)
    else:
        model_version = int(
            sorted(os.listdir(_NLP_FILES_PATH), key=lambda x: int(x[1:]))[-1].replace(
                "v", ""
            )
        )
        version_path = _NLP_FILES_PATH / "v{}".format(model_version)
    eba2017_ids = get_eba_2017_ids()
    nlp = spacy.load("en_core_web_lg")
    topics_lang = {k: nlp(" ".join(v)) for k, v in topic_similarities.items()}
    evaluations_tfidf_keywords = load_jsonl(version_path / "stats/tfidf_all.jsonl")
    evaluations_title_tfidf_keywords = load_jsonl(
        version_path / "stats/tfidf_title.jsonl"
    )
    evaluations_tfidf_keywords = {
        key: val for d in evaluations_tfidf_keywords for key, val in d.items()
    }
    evaluations_title_tfidf_keywords = {
        key: val for d in evaluations_title_tfidf_keywords for key, val in d.items()
    }

    tfidf_threshold = 100
    predicted_topics = []
    for ii, (filename, file_tfidfs) in enumerate(evaluations_tfidf_keywords.items()):
        # filename = list(evaluation_keywords.keys())[0]
        file_id = filename.replace("_content.bin", "")
        # file_tfidfs = list(evaluation_keywords.values())[0]
        if files_to_run == "eba2017":
            if file_id not in eba2017_ids:
                continue

        file_tfidfs = evaluations_title_tfidf_keywords.get(filename, []) + file_tfidfs

        if len(file_tfidfs) == 0:
            continue

        best_score = 0
        sim_scores = []
        for topic_key, synonyms in topics_lang.items():
            keywords, tf_idf_scores = zip(*file_tfidfs)
            if len(keywords) > tfidf_threshold:
                keywords_lang = nlp(" ".join(keywords[0:tfidf_threshold]))
            else:
                keywords_lang = nlp(" ".join(keywords[0:None]))

            sim_score = sum(
                [
                    synonyms.similarity(keyword)  # * tf_idf_scores[ii]
                    for ii, keyword in enumerate(keywords_lang)
                ]
            ) / len(keywords_lang)
            sim_scores.append((topic_key, sim_score))
            # print(key, sim_score, best_score)

            if sim_score > best_score:
                best_topic, best_score = topic_key, sim_score
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        best_topic, best_score = sim_scores[0][0], sim_scores[0][1]

        if abs(sim_scores[0][1] - sim_scores[1][1]) / sim_scores[0][1] < 0.2:
            best_topic = "Flera områden i samma"
        print(filename, best_topic, [round(s[1], 4) for s in sim_scores][0:5])
        predicted_topics.append((file_id, best_topic))
        # if ii > 4:
        #     break
    print(predicted_topics)
    eba_2017_comparison(predicted_topics)

    create_eba_evaluations_column("q11")
    for pred in predicted_topics:
        update_eba_evaluations_column("q11", pred[1], pred[0])


if __name__ == "__main__":
    # python -m q11.main
    approach = input("Which approach should be used (1/2)?")
    if approach == "1":
        main_v1()
    else:
        main_v2()
