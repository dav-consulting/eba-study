import os, json
import logging

from pathlib import Path
import click

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd
import numpy as np
import spacy
from html import unescape
import time
from util import (
    db_connect,
    load_jsonl,
    dump_jsonl,
    load_spacy_model,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    get_eba_evaluations,
    _NLP_FILES_PATH,
    _PARSED_FILES_PATH,
    _PROJECT_PATH,
)
from util import load_spacy_docbin_file as lsd

_EXCLUDE_ENTS = [
    "DATE",
    "QUANTITY",
    "ORDINAL",
    "CARDINAL",
    "MONEY",
    "PERCENT",
]

# defines a custom vectorizer class
class CustomVectorizer(TfidfVectorizer):
    @staticmethod
    def _exclude_token(tok):
        if (
            tok.is_punct
            or tok.is_left_punct
            or tok.is_right_punct
            or tok.is_bracket
            or tok.is_digit
            or tok.is_alpha == False
            or tok.like_url
            or tok.is_stop
            or tok.like_num
            or tok.like_email
            or tok.is_oov
            or tok.is_space
            or len(tok) < 3
            or tok.ent_type
        ):
            return True
        return False

    # overwrite the build_analyzer method, allowing one to
    # create a custom analyzer for the vectorizer
    def build_analyzer(self):

        # load stop words using CountVectorizer's built in method
        stop_words = self.get_stop_words()

        # create the analyzer that will be returned by this method
        def analyser(docs):
            lemmatized_tokens = []

            for doc in docs:
                # for ent in doc.ents:
                #     if ent.label_ not in _EXCLUDE_ENTS:
                #         lemmatized_tokens.append(ent.text)

                for token in doc:
                    if not self._exclude_token(token):
                        if token.is_alpha:
                            lemmatized_tokens.append(token.lemma_.lower())

                            # print(token, token.is_alpha)
            # if len(docs) == 56:
            #    print("xxxxxx", len(lemmatized_tokens))
            # use CountVectorizer's _word_ngrams built in method
            # to remove stop words and extract n-grams
            return self._word_ngrams(lemmatized_tokens, stop_words)

        return analyser


@click.command()
@click.option(
    "--model_version",
    default=-1,
    prompt="Which version number should be used for storing results?",
)
def main(model_version):
    if model_version > 0:
        version_path = _NLP_FILES_PATH / "v{}".format(model_version)
    else:
        model_version = int(
            sorted(os.listdir(_NLP_FILES_PATH), key=lambda x: int(x[1:]))[-1].replace(
                "v", ""
            )
        )
        version_path = _NLP_FILES_PATH / "v{}".format(model_version)

    meta_file_path = version_path / "meta.json"

    st = time.time()
    nlp = load_spacy_model(meta_file_path)
    file_docs = dict()
    categories = set(["all"])
    evaluation_titles = get_eba_evaluations("_id, title")
    for file_path in version_path.iterdir():
        if file_path.is_file() and file_path.name.endswith(".bin"):
            # if file_path.name not in [
            #     "2011:22_15182_content.bin",
            #     "2011:24_15184_content.bin",
            # ]:
            #     continue

            doc_bin, nlp = lsd(version_file_path=file_path, nlp=nlp)
            file_docs[file_path.name] = dict()
            for ii, doc in enumerate(doc_bin):
                category = doc._.props.get("category", [])
                # if 161 < ii < 165:
                if len(category) > 0:
                    # print(category)
                    categories.union(set(category))
                    file_docs[file_path.name].setdefault(category, []).append(doc)
                file_docs[file_path.name].setdefault("all", []).append(doc)

            file_docs[file_path.name]["title"] = next(
                iter(
                    [
                        [nlp(et[1])]
                        for et in evaluation_titles
                        if et[0] == file_path.name.replace("_content.bin", "")
                    ]
                ),
                "",
            )
    print("time: ", time.time() - st)
    categories.add("title")
    print("categories: ", categories)
    print(file_docs.keys())
    for category in categories:
        print("process: ", category)
        category_tfidf_scores = []
        corpora_docs = [v.get(category, []) for k, v in file_docs.items()]
        try:
            custom_vec = CustomVectorizer(stop_words="english")  # ngram_range=(1, 2),
            cwm = custom_vec.fit_transform(corpora_docs)
        except ValueError as e:
            print(category, e)
            print([len(c) for c in corpora_docs])
            # print(corpora_docs[0][0:4])
            continue
        inverted_vocab = {v: k for k, v in custom_vec.vocabulary_.items()}

        for row_idx, file_name in enumerate(file_docs.keys()):
            tfidf_scores = dict()
            tfidf_scores[file_name] = sorted(
                [
                    (inverted_vocab[col_idx], cwm[row_idx, col_idx])
                    for col_idx in cwm[row_idx].indices
                ],
                key=lambda x: x[1],
                reverse=True,
            )
            category_tfidf_scores.append(tfidf_scores)
        dump_jsonl(
            category_tfidf_scores,
            version_path / "stats/tfidf_{}.jsonl".format(category),
        )

    # print(tfidf_scores)

    # pd.set_option("display.max_columns", None)
    # print(df)

    # print(df["Cultural Heritage"])
    # print(df["programme"])


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    # python -m nlp_processing.add_tfidf
    main()
