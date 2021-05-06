import sqlite3
import click
import spacy
from spacy.matcher import Matcher
from collections import Counter
from util import _NLP_FILES_PATH, _PARSED_FILES_PATH, db_connect, get_eba_evaluations

# from util import load_spacy_docbin_file as lsd
from q9.util import _STOP_WORDS, _ALL_DONORS, _FUND_WORD_LEMMA_PATTERNS

from util import (
    load_spacy_docbin_file as lsd,
    get_eba_evaluations,
    get_eba2017,
)

nlp = spacy.load("en_core_web_lg")


## evaluate with the data from eba 2017
def eba_2017_comparison():
    """Funciton for evaluating method against output from EBA 2017-12."""
    eba_rows = get_eba2017("f_id, _Finansiar")
    evaluations = get_eba_evaluations("_id, q9")
    results = []
    for row in eba_rows:
        f_id = row[0]
        eba_phase = row[1]
        if eba_phase:
            for eval_row in evaluations:
                # print(f_id, topic, pt[0])
                if eval_row[0] == f_id:
                    results.append((f_id, eba_phase, eval_row[1]))
    cnt_correct = 0
    for res in results:
        print(res)
        if res[1] in res[2]:
            cnt_correct += 1
        print(res[1] == res[2], res)
    print(f"Number of correct predictions: {cnt_correct} / {len(results)}")


def similarity_test(word, source):
    """Assessment function using spaCy similarity/word2vec for identifying words associated with "source"-word (need to be nlp("source")). This is used to determine each spaCy-docs relevance and single out sentences to analyse.
    :param word: string
    :returns: Bolean "True" if spaCy similarity score is above set threashold.
    """
    result = source.similarity(word)
    if result > 0.55:
        return True


def check_donor_result_to_eba(data=tuple()):
    """Sorting function for response to q9 - if Sida/Sweden is the sole financier. This function is normalising the output data to format from EBA 2017-12.
    :param data: tuple with dicts/counter containing A) identified tokens, B) identified donors.
    :returns: string based on type and number of identified donors:
        a) Only Sida and/or Sweden identified returns - "Ja"
        b) Sida and/or Sweden and at least one other relevant donor returns - "Nej"
        c) No identified donor returns - "Ingen finansiär hittad".
    """
    donors = data[0]  ## sigle out dict/counter with identified donors
    if "sida" in donors.keys() and "sweden" in donors.keys():
        if len(donors.keys()) <= 1:
            return "ja"
        elif len(donors.keys()) > 1:
            return "nej"
    elif "sida" in donors.keys() or "sweden" in donors.keys():
        if len(donors.keys()) <= 1:
            return "ja"
        elif len(donors.keys()) > 1:
            return "nej"
    else:
        return "oklart, framgår ej"


class ParseFinancier:
    def __init__(self, select_output):
        self.conn, self.cur = db_connect()
        self.select_output = select_output
        if select_output == "eba_responses":
            self.create_column("q9")
        else:
            pass

    def create_column(self, col_name):
        try:
            self.cur.execute(
                "ALTER TABLE eba_evaluations ADD COLUMN {} TEXT;".format(col_name)
            )

        except sqlite3.OperationalError as e:
            print("Column already exists?! ", str(e))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def parse_financiers(self, text_data: list = []):
        """ Response to question 9 - if Sida/Sweden is sole financier. This functions uses tokenized text strings from decentralised Sida evaluations and uses spaCy's Matcher for rules-based matching to identify text passages of relevance (i.e. related to funding of the evaluated projects/programmes). In a second step the funciton uses spaCy's English NER model to single out countries and organisations that are mentioned as financers/donors besides Sweden/Sida.
        Identified donors have been singled by matching identified entites (ORG and GPE) in text passages that related to funding and matching the entities with a list of well known donor organistaion and donor countries. 
        :param text_data: list of tokinized spacy sentences derived from each parsed evaluation.
        :returns: tuple with identified tokens and identified donors. 
        """
        ##Interim storage for idenfitied tokens (i.e words of relevance); identified entities (all entities that are mentioned in the condext of funding); and identified donors or relevance (matched with list of well-known donors and donor countries).
        identified_token_list = []
        entities_list = []
        identified_donor_list = []
        ## for producing simantic similar word for the matcher.
        # source = nlp("donor")
        ## loading of matcher, setting matcher label, and applying matcher patter/list of words/phrases
        matcher = Matcher(nlp.vocab)
        matcher.add("donor_words", None, *_FUND_WORD_LEMMA_PATTERNS)

        for all_docs in text_data:
            ## filter out executive summary/intro
            # if "executive_summary" in doc._.props.get(
            #    "category", []
            # ) or "introduction" in doc._.props.get("category", []):
            ## iterate over sentencces
            for doc in all_docs.sents:
                matches = matcher(doc)
                ## apply matcher
                for match_id, start, end in matches:
                    string_id = nlp.vocab.strings[match_id]  # Get string representation
                    span = doc[start:end]  # The matched span
                    ## store lemma words with bearing on matcher
                    if string_id == "donor_words":
                        identified_token_list.append(str(span.text))
                        ## identify entities in relevant sentences and store them
                        for ent in doc.ents:
                            if ent.label_ == "ORG" or ent.label_ == "GPE":
                                entities_list.append(str(ent))
                                ## print relevant sentences.
                                # if str(ent).lower() in _ALL_DONORS:
                                #    print(doc)
                                #    print("---")
        ## match identified entities agains list of donors.
        for ent in entities_list:
            if str(ent).lower() in _ALL_DONORS:
                identified_donor_list.append(str(ent).lower())
            else:
                continue

        # print("IDENTIFIED TOKENS: ", Counter(identified_token_list))
        # print("IDENTIFIED DONORS: ", Counter(identified_donor_list))
        # print("IDENTIFIED ENTITES: ", Counter(entities_list))

        yield (Counter(identified_donor_list),)

    def parse_file(self, docs, bin_file):
        """ Applying functions for q9 processing document/evaluation and inserting into database.
        :param docs: parsed/tokinized document/evaluation
        :param bin_file: bin files from method _nlp_processing
        :returns: inserts string from the function check_donor_result_to_eba on index/primay key in eba_evaluations/SQL.
        """
        for itr in self.parse_financiers(docs):
            ## index number
            doc_id = bin_file.replace("_content.bin", "")
            # print(doc_id)
            ## evaluate and compile all doc with relevant content. See function check_donor_result_to_eba above
            data_for_comparission = check_donor_result_to_eba(itr)

            try:
                sql_str_q9 = "UPDATE eba_evaluations SET q9=? WHERE _id=?"
                self.cur.execute(sql_str_q9, (data_for_comparission, doc_id))
            except Exception as e:
                print(sql_str_q9)
                print("SQL error: ", e)
            assert self.cur.rowcount == 1, "No rows where UPDATED!!"
            print(
                "Successfully updated {} with data: {}".format(
                    doc_id, data_for_comparission
                )
            )
            self.conn.commit()


def parse_files(version: str = None, select_output: str = "eba_responses"):
    """ Processing multiple documents/evaluations by using the parse_file function from the ParseFinancier class."""

    version_path = _NLP_FILES_PATH / "v{}".format(version)
    with ParseFinancier(select_output=select_output,) as pg:
        nlp = None
        for bin_file in version_path.iterdir():
            if bin_file.name.endswith(".bin"):
                version_file_path = version_path / bin_file
                docs, nlp = lsd(version_file_path, nlp)
                pg.parse_file(docs, bin_file.name)


@click.command()
@click.option(
    "--version", default="1", prompt="Which version number should be assessed?",
)
@click.option(
    "--select_output",
    default="eba_responses",
    prompt="Choose output type:",
    type=click.Choice(["eba_responses"]),
)
def main(version, select_output):
    parse_files(version, select_output)


if __name__ == "__main__":
    # python -m q9.main
    main()
    ## evalute the result
    # eba_2017_comparison()
    pass
