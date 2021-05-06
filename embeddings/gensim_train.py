import json, time
import click
import gensim, logging, multiprocessing
from gensim.test.utils import get_tmpfile
from gensim.models.word2vec import LineSentence, PathLineSentences
from gensim.models import Word2Vec


from util import (
    _PROJECT_PATH,
    _NLP_FILES_PATH,
    dump_jsonl,
    load_jsonl,
    get_model_version_path,
)

from util import (
    load_spacy_docbin_file as lsd,
    load_spacy_docbin_folder as lsdf,
    load_spacy_model as lsm,
)

_training_data_path = _PROJECT_PATH / "embeddings/results/training_data/"
_model_path = _PROJECT_PATH / "embeddings/results/models/"


def exclude_token(tok):
    exclude_toks = [
        tok.is_space,
        tok.is_bracket,
        tok.is_quote,
        tok.like_num,
        tok.like_url,
        tok.is_currency,
        tok.like_email,
        tok.is_punct,
        tok.is_upper,
        not tok.has_vector,
        not tok.is_alpha,
    ]
    return any(exclude_toks)


def create_corpus(model_version=-1):
    """ Create corpus from  evaluations """

    version_path, model_version = get_model_version_path(model_version)

    nlp = lsm(version_path)
    cnt = 0
    _training_data_filepath = _training_data_path / f"data_v{model_version}.jsonl"
    for idx, (file_name, docs, nlp) in enumerate(lsdf(model_version, nlp)):
        print(file_name)
        sents = []
        for doc in docs:
            if doc._.props["type"] == "text":
                for sent in doc.sents:
                    sentence = [tok.lower_ for tok in sent if not exclude_token(tok)]
                    tok_one_length = [len(w) == 1 for w in sent]
                    if len(sentence) > 1 and sum(tok_one_length) < 0.8 * len(sentence):
                        sents.append(sentence)

        if len(sents) > 0:
            dump_jsonl(sents, _training_data_filepath, append=(cnt > 0))
            cnt += 1
    return model_version


# def get_latest_model():
#     for file in _model_path.iterdir():
#         file.name


@click.command()
@click.option(
    "--create_new_corpus", default="n", prompt="Do you want to create a new corpus?"
)
@click.option(
    "--model_version",
    default=-1,
    prompt="If create new corpus. Which model version shoould be used?",
)
def train_w2v(create_new_corpus, model_version):
    """ Train a word2vec model with gensim."""
    if create_new_corpus == "y":
        model_version = create_corpus(model_version=model_version)
    data_set = None
    for file in _training_data_path.iterdir():
        if f"v{model_version}.jsonl" in file.name:
            _training_data_filepath = (
                _training_data_path / f"data_v{model_version}.jsonl"
            )
            data_set = load_jsonl(_training_data_filepath)
            break
    assert data_set, f"Dataset fro model version v{model_version} not found!!"

    print("Num sentences: ", len(data_set))
    st = time.time()
    w, m, i = 10, 5, 12
    model = Word2Vec(
        data_set,
        size=300,
        window=w,
        min_count=m,
        sg=1,
        workers=multiprocessing.cpu_count(),
        iter=i,
    )
    print("Time to train: ", time.time() - st)
    _model_filepath = _model_path / f"model_w{w}_m{m}_i{i}.kv"
    model.wv.save(str(_model_filepath))  # save vectors into KeyedVectors
    print(model.wv.most_similar(positive="national"))


if __name__ == "__main__":

    train_w2v()
