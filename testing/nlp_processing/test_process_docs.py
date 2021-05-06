import pytest
import os
import spacy
from util import load_spacy_docbin_file
from util import _NLP_FILES_PATH


def test_load_spacy_doc():
    file_path = None
    for version in _NLP_FILES_PATH.iterdir():
        if version.is_dir():
            for file_path in version.iterdir():
                if file_path.name.endswith(".bin"):
                    break

    docs, nlp = load_spacy_docbin_file(version_file_path=file_path)
    assert isinstance(docs[0], spacy.tokens.doc.Doc)
    assert isinstance(nlp, spacy.lang.en.English)
