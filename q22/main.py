import sqlite3
import click
import spacy
from spacy.matcher import Matcher
from collections import Counter
from util import _NLP_FILES_PATH, _PARSED_FILES_PATH, db_connect, get_eba_evaluations

# from util import load_spacy_docbin_file as lsd
from q22.util import (
    _ALL_DONORS,
    _DONOR_DEPENDENCY_WORD_LEMMA_PATTERNS,
    _DEPENDENCY_WORD_LEMMA_PATTERNS,
    _DONOR_WORD_LEMMA_PATTERNS,
)

from util import (
    load_spacy_docbin_file as lsd,
    get_eba_evaluations,
    get_eba2017,
)

nlp = spacy.load("en_core_web_lg")


## evaluate with the data from eba 2017
def eba_2017_comparison():
    """Funciton for evaluating method against output from EBA 2017-12."""
    eba_rows = get_eba2017("f_id, _Bistandsberoende")
    evaluations = get_eba_evaluations("_id, q22")
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
    :param source: spaCy token
    :returns: Bolean "True" if spaCy similarity score is above set threashold.
    """
    result = source.similarity(word)
    if result > 0.55:
        return True


def check_donor_dependency_result_to_eba(data=tuple()):
    """Function that normalises the output data (from the function parse_donor_dependency()) to format from EBA 2017-12. Note that the response "Nej, men man skriver explicit att insatsen är beroende av bistånd from EBA 2017-12 has been converted to a "Nej", since it do in fact suggest that the relevant concept is being discussed.
    :param data: tuple with count/number of unique sentences deemed relevant.
    :returns: string based on response type from EBA 2017-12:
        Ja) The evaluation discuss the concept of donor dependency.
        Nej) The evaluation does not discuss the concept of donor dependency.
        """
    if data[0] > 0:
        return "ja"
    else:
        return "nej"


class ParseDonorDependency:
    def __init__(self, select_output):
        self.conn, self.cur = db_connect()
        self.select_output = select_output
        if select_output == "eba_responses":
            self.create_column("q22")
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

    def parse_sida_dependency(self, text_data: list = []):
        """ This function generates estimations to q22 - is donor dependency disscussed in the evaluation?
        The function uses tokenized text strings from decentralised Sida evaluations and uses spaCy's Matcher for rules-based matching to identify text passages of relevance (i.e. related to 1."donor dependency", 2."dependency", 3."donor") in the evaluated projects/programmes).
        :param text_data: list of tokinized spacy docs derived from each parsed evaluation.
        """

        ##Interim storage for idenfitied tokens (i.e words of relevance); identified entities (all entities that are mentioned in the condext of funding); and identified donors or relevance (matched with list of well-known donors and donor countries).
        words_result = []
        sents_result = []
        docs_result = []
        entities_list = []
        identified_donor_list = []
        # ? function for processing similarity score on all words in entire corpus to include in spacy matcher.
        # source = nlp("depend")
        # sim_words = []
        # for doc in text_data:
        #    for tok in doc:
        #        test = similarity_test(tok, source)
        #        if test is True:
        #            sim_words.append(tok)

        # * loading matchers to be used.
        matcher_1 = Matcher(nlp.vocab)
        matcher_1.add(
            "donor_dependency_words", None, *_DONOR_DEPENDENCY_WORD_LEMMA_PATTERNS
        )
        matcher_2 = Matcher(nlp.vocab)
        matcher_2.add("dependency_words", None, *_DEPENDENCY_WORD_LEMMA_PATTERNS)
        matcher_3 = Matcher(nlp.vocab)
        matcher_3.add("donor_words", None, *_DONOR_WORD_LEMMA_PATTERNS)

        for doc in text_data:  # .sents: ## apply limitations on docs or sentences
            if "terms_of_reference" not in doc._.props.get("category", []):
                # if "concluding_sections" in doc._.props.get("category", []):
                # * apply matcher for "donor depedency"
                for fund_doc in doc.sents:  # ! senteces only
                    matches_1 = matcher_1(fund_doc)
                    for match_id_1, start_1, end_1 in matches_1:
                        string_id_1 = nlp.vocab.strings[match_id_1]
                        if string_id_1 == "donor_dependency_words":
                            span_1 = doc[start_1:end_1]  # The matched span
                            words_result.append(span_1)
                            sents_result.append(fund_doc)
                            docs_result.append(doc)
                            # * parse entities
                            for ent in doc.ents:
                                if ent.label_ == "ORG" or ent.label_ == "GPE":
                                    entities_list.append(str(ent))

                # * apply matcher for "dependency"
                for fund_doc in doc.sents:  # ! senteces only
                    matches_2 = matcher_2(fund_doc)
                    for match_id_2, start_2, end_2 in matches_2:
                        string_id_2 = nlp.vocab.strings[match_id_2]
                        if string_id_2 == "dependency_words":
                            span_2 = doc[start_2:end_2]
                            words_result.append(span_2)
                            # * apply matcher for "donor"
                            matches_3 = matcher_3(fund_doc)
                            for match_id_3, start_3, end_3 in matches_3:
                                string_id_3 = nlp.vocab.strings[match_id_3]
                                if string_id_3 == "donor_words":
                                    span_3 = doc[start_3:end_3]  # The matched span
                                    words_result.append(span_3)
                                    sents_result.append(fund_doc)
                                    docs_result.append(doc)
                                    # * parse entities
                                    for ent in doc.ents:
                                        if ent.label_ == "ORG" or ent.label_ == "GPE":
                                            entities_list.append(str(ent))

        # * match identified entities agains list of donors.
        for ent in entities_list:
            if str(ent).lower() in _ALL_DONORS:
                identified_donor_list.append(str(ent).lower())
            else:
                continue

        # print("@@DOCS@@")
        # for doc in set(docs_result):
        #    print(doc)
        #    print("---")
        # print("@@SENTS@@")
        for sents in set(sents_result):
            print(sents)
            print("---")
        print("@@DONORS@@")
        print(set(identified_donor_list))

        print("##OUTPUT##")  # print(set(s_test))
        yield (len(sents_result),)

    def parse_file(self, docs, bin_file):
        """ Applying functions for q9 processing document/evaluation and inserting into database.
        :param docs: parsed/tokinized document/evaluation
        :param bin_file: bin files from method _nlp_processing
        :returns: inserts string from the function check_donor_result_to_eba on index/primay key in eba_evaluations/SQL.
        """
        for itr in self.parse_sida_dependency(docs):
            ## index number
            doc_id = bin_file.replace("_content.bin", "")
            # print(doc_id)
            ## evaluate and compile all doc with relevant content. See function check_donor_dependency_result_to_eba above
            data_for_comparission = check_donor_dependency_result_to_eba(itr)

            try:
                sql_str_q22 = "UPDATE eba_evaluations SET q22=? WHERE _id=?"
                self.cur.execute(sql_str_q22, (data_for_comparission, doc_id))
            except Exception as e:
                print(sql_str_q22)
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
    with ParseDonorDependency(select_output=select_output,) as pg:
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
    # python -m q22.main
    main()
    ## evalute the result
    # eba_2017_comparison()
    pass
