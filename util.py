""" Variables and methods applicable to entire repository. """
import os, logging, time
from pathlib import Path, PosixPath
from typing import Union, List
from collections import Counter
import sqlite3
import json
import spacy
from spacy.tokens import DocBin
from spacy.tokens import Doc, Span

_PROJECT_PATH = Path(__file__).parent

_DB_FILE_PATH = _PROJECT_PATH / "processed_output.db"

_FETCHED_FILES_PATH = _PROJECT_PATH / "fetch_evaluations" / "documents" / "evaluations"
_PARSED_FILES_PATH = _PROJECT_PATH / "parse_evaluations" / "results"
_NLP_FILES_PATH = _PROJECT_PATH / "nlp_processing" / "results"

_EBA_FILE_PATH = _PROJECT_PATH / "eba2017" / "original_data" / "eba2017_12.xlsx"
_EBA_CASE_FILE_PATH = (
    _PROJECT_PATH / "eba2017" / "original_data" / "eba2017_12_case.xlsx"
)

_EMBEDDINGS_MODEL_PATH = _PROJECT_PATH / "embeddings/results/models"

_EXECUTIVE_SUMMARY_VARIATIONS = [
    "executive summary",
    "executivesummary",
    "executive",
]
_INTRODUCTION_VARIATIONS = ["introduction"]
_RECOMMENDATION_SECTION_VARIATIONS = ["recommendations", "recommendation"]
_CONCLUDING_SECTION_VARIATIONS = [
    "conclusions",
    "conclusion",
    "discussion",
    "lessons learnt",
    "lessons learned",
    "findings",
]
_DAC_CRITERIA_VARIATIONS = {
    "sustainability": ["sustainability", "sustainable", "sustain"],
    "relevance": ["relevance"],
    "effectiveness": ["effectiveness"],
    "efficiency": ["efficiency"],
    "impacts": ["impacts", "impact"],
}
_TERMS_OF_REFERENCE = ["terms of reference"]

_DAC_CRITERIA_VALUES_FROM_CODE = {
    "sustainability": {
        "sustainable": "insatsen bedöms vara hållbar",
        "subsustainable": "insatsen bedöms i utvärderingen vara i delar hållbar i andra delar inte hållbar",
        "unsustainable": "insatsen bedöms inte vara hållbar",
        "na": "utvärderarna gör ingen bedömning/det går inte läsa ut ur rapporten",
    }
}


def create_eba_evaluations_column(column_name: str, column_type: str = "TEXT") -> None:
    """ Creates a table column """
    conn, cur = db_connect()
    try:
        cur.execute(
            "ALTER TABLE eba_evaluations ADD COLUMN {} {};".format(
                column_name, column_type
            )
        )
        print("Successfully created column: {}".format(column_name))
    except sqlite3.OperationalError as e:
        print("Column already exists?! ", str(e))
    conn.close()


def dump_jsonl(data, output_path, append=False, silenced=True):
    """
    Write list of objects to a JSON lines file.
    """
    mode = "a+" if append else "w"
    if not os.path.exists(output_path.parents[0]):
        os.mkdir(output_path.parents[0])
    with open(output_path, mode, encoding="utf-8") as f:
        for line in data:
            json_record = json.dumps(line, ensure_ascii=False)
            f.write(json_record + "\n")
    if not silenced:
        print("Wrote {} records to {}".format(len(data), output_path))


def dump_json(data, output_path, silenced=True):
    """
    Write dict to a JSON file.
    """
    if not os.path.exists(output_path.parents[0]):
        os.mkdir(output_path.parents[0])
    with open(output_path, mode, encoding="utf-8") as f:
        json_record = json.dumps(line, ensure_ascii=False)
        f.write(json_record)
    if not silenced:
        print("Wrote {} records to {}".format(len(data), output_path))


def db_connect():
    """ Connect to EBA database 
    return: conn, cur """
    conn = sqlite3.connect(_DB_FILE_PATH)
    cur = conn.cursor()
    return conn, cur


def eba_2017_comparison(eba2017_col: str, eba_predictions: Union[list, str]):
    """ Method for comparing results to EBA2017 """
    eba_rows = get_eba2017(f"f_id, {eba2017_col}")

    if isinstance(eba_predictions, str):
        evaluations = get_eba_evaluations(f"_id, {eba_predictions}")
    else:
        evaluations = eba_predictions

    results = []
    for row in eba_rows:
        f_id = row[0]
        eba2017_val = row[1]

        if eba2017_val:
            for eval_row in evaluations:
                if eval_row[0] == f_id:
                    results.append((f_id, eba2017_val, eval_row[1]))
                    break
    cnt_correct = 0
    for res in results:
        if res[1] == res[2]:
            cnt_correct += 1
        print(f"{res[0]}: {res[1] == res[2]}, EBA2017 / Pred: {res[1]} / {res[2]}")
    print(f"Number of correct predictions: {cnt_correct} / {len(results)}")


def get_eba2017_adjusted_probability_score(eba2017_col: str) -> dict:
    """ Calculates the theoretical outcome of a random guess where probabilities have been adjusted to match the
    empirical distribution of the dataset categories."""
    eba_rows = get_eba2017(f"f_id, {eba2017_col}")
    _ids, categories = zip(*eba_rows)
    nr_guesses = len(categories)
    category_counts = dict(Counter(categories))
    average_guess = 0
    for k, v in category_counts.items():
        average_guess += v * v / nr_guesses

    return {
        "nr_guesses": nr_guesses,
        "distinct_categories": len(category_counts),
        "random_equal_prob_outcome": round(nr_guesses / len(category_counts), 4),
        "random_freq_adj_prob_outcome": round(average_guess, 4),
        "category_counts": category_counts,
    }


def files_to_exclude():
    """ Returns a list of files to exclude from the eba analyis """
    conn, cur = db_connect()
    rows = conn.execute(
        "SELECT _id FROM eba_evaluations WHERE series!='Sida Decentralised Evaluation' OR series_number LIKE '2008:%' OR series_number LIKE '2009:%'  OR series_number LIKE '2010:%';"
    )
    return [row[0] for row in rows]


def get_file_id(file_path: Union[str, PosixPath]) -> str:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    file_name = file_path.name
    file_id = (
        file_name.replace("_content.bin", "")
        .replace("_content.json", "")
        .replace("_meta.json", "")
    )
    return file_id


def get_section_text(file_ids: tuple, section_name: str = "executive_summary") -> list:
    """ Returns specific section text """

    for path_obj in _PARSED_FILES_PATH.iterdir():
        section_text = []
        if (
            path_obj.is_file()
            and path_obj.name.replace("_content.json", "") in file_ids
        ):
            with open(path_obj, "r") as f:
                for line in f:
                    content = json.loads(line)
                    if section_name in content.get("category", []):
                        section_text.append(content)

        yield section_text


def get_eba_2017_ids() -> List[str]:
    conn, cur = db_connect()
    cur.execute("SELECT _id FROM eba_evaluations WHERE eba_match_nr IS NOT NULL")
    rows = [res[0] for res in cur.fetchall()]
    conn.close()
    return rows


def get_model_version_path(model_version: int = -1) -> Union[PosixPath, int]:
    """ Get model version path """
    if model_version > 0:
        version_path = _NLP_FILES_PATH / "v{}".format(model_version)
    else:
        model_version = int(
            sorted(os.listdir(_NLP_FILES_PATH), key=lambda x: int(x[1:]))[-1].replace(
                "v", ""
            )
        )
        version_path = _NLP_FILES_PATH / "v{}".format(model_version)
    return version_path, model_version


def get_eba_evaluations(str_columns, where_clause=None) -> list:
    """
    Fetch columns from eba_evaluations.
    :param str_columns: string of columns to fetch from database
    """
    conn, cur = db_connect()
    if where_clause:
        cur.execute(
            "SELECT {} FROM eba_evaluations WHERE {}".format(str_columns, where_clause)
        )
    else:
        cur.execute("SELECT {} FROM eba_evaluations".format(str_columns))
    rows = [res for res in cur.fetchall()]
    conn.close()
    return rows


def get_eba2017(str_columns, where_clause="f_id IS NOT NULL"):
    """
    Fetch columns from eba_evaluations.
    :param str_columns: string of columns to fetch from database
    """
    conn, cur = db_connect()
    if where_clause:
        cur.execute("SELECT {} FROM eba2017 WHERE {}".format(str_columns, where_clause))
    else:
        cur.execute("SELECT {} FROM eba2017".format(str_columns))
    rows = [res for res in cur.fetchall()]
    conn.close()
    return rows


def get_third_party(str_columns, where_clause="f_id IS NOT NULL"):
    """
    Fetch columns from eba_evaluations.
    :param str_columns: string of columns to fetch from database
    """
    conn, cur = db_connect()
    if where_clause:
        cur.execute(
            "SELECT {} FROM eba2017_third_party WHERE {}".format(
                str_columns, where_clause
            )
        )
    else:
        cur.execute("SELECT {} FROM eba2017_third_party".format(str_columns))
    rows = [res for res in cur.fetchall()]
    conn.close()
    return rows


def load_jsonl(input_path: Union[str, PosixPath], silenced=True) -> list:
    """
    Read list of objects from a JSON lines file.
    """
    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.rstrip("\n|\r")))
    if not silenced:
        print("Loaded {} records from {}".format(len(data), input_path))
    return data


def load_spacy_model(version_file_path: Union[PosixPath, str]) -> spacy.lang:
    """ Loads a Spacy model and props from a version folder. """
    # Make sure we load the same Spacy model which was used to save the doc
    if isinstance(version_file_path, str):
        version_file_path = Path(version_file_path)
    version_path = (
        version_file_path.parent if version_file_path.is_file() else version_file_path
    )
    with open(version_path / "meta.json", "r") as f:
        meta_data = json.loads(f.read())
    spacy_model = meta_data["spacy_model"]

    print(f"Loading spacy model: {spacy_model}")
    nlp = spacy.load(spacy_model)

    # We need to set the properties extension
    if not Doc.has_extension("props"):
        Doc.set_extension("props", default=None)
        print("Doc set_extension: props")

    return nlp


def load_spacy_docbin_file(version_file_path: str, nlp: spacy.lang = None):
    """ Load sa spacy docbin file and returns list of doc and nlp model used to generate it.
    If language model not given it loads the model specified in the meta file in the file path.
    :param version_file_path: full path to spacy doc_bin file.
    :param nlp: spacy model """
    version_file_path = Path(version_file_path)
    if nlp is None:
        nlp = load_spacy_model(version_file_path)

    logging.info("Loading: %s", version_file_path)
    st = time.time()
    with open(version_file_path, "rb") as fb:
        doc_bin = DocBin(store_user_data=True).from_bytes(fb.read())
        docs = list(doc_bin.get_docs(nlp.vocab))
    logging.info("Loaded in %s seconds ", round(time.time() - st, 1))
    return docs, nlp


def load_spacy_docbin_folder(
    version: int = None, nlp: spacy.lang = None, include_only_ids: list = []
):
    """ Loads all spacy docbin files in a folder.
    :param version: Version number to load spacy docbin objects from.
    :param nlp: spaCy lang model 
    :param include_only_ids: include only these ids
    :return: dict with keys corresponding to file names
    """
    version_path = _NLP_FILES_PATH / "v{}".format(version)

    for path_obj in version_path.iterdir():
        if get_file_id(path_obj) not in include_only_ids and len(include_only_ids) > 0:
            continue
        if path_obj.name.endswith(".bin"):
            docs, nlp = load_spacy_docbin_file(path_obj, nlp)
            yield path_obj, docs, nlp


def update_eba_evaluations_column(
    column_name="", update_value="", primary_key=None, silence=False
):
    """ Updates a table row """
    conn, cur = db_connect()
    try:
        if primary_key:
            cur.execute(
                "UPDATE eba_evaluations SET {}=? WHERE _id=?".format(column_name),
                (update_value, primary_key),
            )
        else:
            cur.execute(
                "UPDATE eba_evaluations SET {}=? ".format(column_name), (update_value,),
            )
        conn.commit()
    except Exception as e:
        print("Exception occured: {}".format(e))

    if not silence:
        if cur.rowcount < 1:
            print("Could not update table...")
        else:
            print("Updated successfully {} row!".format(cur.rowcount))
    conn.close()

