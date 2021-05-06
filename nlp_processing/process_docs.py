""" Creat an load SPacy DocBin files """
import functools
import os, json
import logging
from multiprocessing import Pool
import multiprocessing
from pathlib import Path
import click
import spacy
from spacy.tokens import DocBin
from spacy.tokens import Doc
from util import _NLP_FILES_PATH, _PARSED_FILES_PATH
from util import load_spacy_model, get_eba_2017_ids
import time, datetime

_SPACY_MODELS = ["en_core_web_sm", "en_core_web_lg"]


def create_spacy_doc_bins(
    spacy_model: str = "en_core_web_sm", version: int = -1, file_name: str = None
):
    """ Creates Spacy Doc objects, serialize's the information and stores as bytes files. 
    :param spacy_model: Spcay model to use for text processing.
    :param version: Version number to save spacy docbin objects to (default -1 -> add new version number).
    """

    assert isinstance(version, int), "Version number must be an integer!"
    if spacy_model in _SPACY_MODELS:
        print("Loading model '{}'...".format(spacy_model))
        nlp = spacy.load(spacy_model)
    else:
        print(
            "Model {} not available. Loading model 'en_core_web_sm'...".format(
                spacy_model
            )
        )
        nlp = spacy.load("en_core_web_sm")

    doc_bin_attrs = ["TAG", "POS", "LEMMA", "HEAD", "DEP", "ENT_IOB", "ENT_TYPE"]

    Doc.set_extension("props", default=None)

    if not os.path.exists(_NLP_FILES_PATH):
        os.mkdir(_NLP_FILES_PATH)
    if version < 0:
        versions = sorted(
            [
                int(f[1:])
                for f in os.listdir(_NLP_FILES_PATH)
                if os.path.isdir(os.path.join(_NLP_FILES_PATH, f))
            ]
        )
        if versions:
            version = versions[-1] + 1
        else:
            version = 1

    print("Storing as version 'v{}'...".format(version))
    _NLP_RESULTS_PATH = os.path.join(_NLP_FILES_PATH, "v{}/".format(version))
    print(_NLP_RESULTS_PATH)
    if not os.path.exists(_NLP_RESULTS_PATH):
        os.mkdir(_NLP_RESULTS_PATH)

    # Create meta file
    with open(os.path.join(_NLP_RESULTS_PATH, "meta.json"), "w") as f:
        meta = {
            "spacy_model": spacy_model,
            "date": str(datetime.datetime.now()),
            "attrs": doc_bin_attrs,
            "run_type": file_name,
        }
        f.write(json.dumps(meta))

    print("Processing files from: {}".format(_PARSED_FILES_PATH))
    for idx, parsed_filename in enumerate(os.listdir(_PARSED_FILES_PATH)):
        doc_bin = DocBin(attrs=doc_bin_attrs, store_user_data=True)

        # if a file_name is specified create docbin only for that specific file
        if file_name == "eba2017":
            eba2017_ids = [_id for _id in get_eba_2017_ids()]
            if parsed_filename.replace("_content.json", "") not in eba2017_ids:
                continue
        elif file_name:
            if parsed_filename != file_name:
                continue

        if parsed_filename.endswith("_content.json"):
            print("Processing {}: {}".format(idx, parsed_filename))
            start_time = time.time()
            with open(os.path.join(_PARSED_FILES_PATH, parsed_filename)) as f:
                parsed_content, texts = [], []
                for line in f:
                    content = json.loads(line)
                    parsed_content.append(content)
                    texts.append(content["text"])
        else:
            continue

        for ii, doc in enumerate(nlp.pipe(texts)):
            text_attributes = parsed_content[ii]
            del text_attributes["text"]
            doc._.props = text_attributes
            doc_bin.add(doc)

        bin_file_name = parsed_filename.split(".")[0] + ".bin"
        with open(os.path.join(_NLP_RESULTS_PATH, bin_file_name), "wb") as f:
            f.write(doc_bin.to_bytes())

        print(
            "Finished writing: {}; Process time: {} seconds".format(
                bin_file_name, round(time.time() - start_time, 1)
            )
        )
        doc_bin = None

    # yield bin_file, docs, nlp


@click.command()
@click.option(
    "--spacy_model",
    default="en_core_web_lg",
    prompt="Which spacy model should be used?",
)
@click.option(
    "--version",
    default=-1,
    prompt="Which version number should be used for storing results?",
)
@click.option(
    "--file_name",
    default="all",
    prompt="Do you want to process a specific file? ( all / eba2017 / json_file_name)",
)
def main(spacy_model, version, file_name):
    if file_name == "all":
        file_name = None
    create_spacy_doc_bins(spacy_model, int(version), file_name)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    # python -m nlp_processing.process_docs
    main()

