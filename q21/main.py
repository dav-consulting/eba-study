import sqlite3
import click
import spacy
from spacy.matcher import Matcher
from collections import Counter
from util import _NLP_FILES_PATH, _PARSED_FILES_PATH, db_connect, get_eba_evaluations

# from util import load_spacy_docbin_file as lsd
from q21.util import (
    _FUND_WORD_LEMMA_PATTERNS,
    _SUSTAINABILITY_WORD_LEMMA_PATTERNS,
    _IMPORTANCE_WORD_LEMMA_PATTERNS,
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
    eba_rows = get_eba2017("f_id, _Sida_roll")
    evaluations = get_eba_evaluations("_id, q21")
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
    if result > 0.65:
        return True


def check_sida_dependency_to_eba(data=tuple()):
    """Function that normalises the output data (from the function parse_sida_dependency()) to format from EBA 2017-12. Note that the response "Analyseras ej då hållbar alt att hållbarhet ej har analyserats" from EBA 2017-12 has been converted to a "Nej", which is the logical approach - if the evaluation has not analysed it there should be no reference it. 
    :param data: tuple with count/number of unique sentences deemed relevant.
    :returns: string based on response type from EBA 2017-12:
        Ja) The evaluation holds text sections with bearing on Sida's importance for sustainability
        Nej) The evaluation does not hold text sections with bearing on Sida's importance for sustainability
    """
    if data[0] > 0:
        return "ja"
    else:
        return "nej"


class ParseSidaDependency:
    def __init__(self, select_output):
        self.conn, self.cur = db_connect()
        self.select_output = select_output
        if select_output == "eba_responses":
            self.create_column("q21")
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
        """ This function generates estimations to q21 - Does the evaluation assess the importance of Sida's funding relating to the contributions sustainability/lack of sustainability?
        This functions uses tokenized text strings from decentralised Sida evaluations and uses spaCy's Matcher for rules-based matching to identify text passages of relevance (i.e. related to 1."funding", 2."sustainability", 3."importance" of Sida) in the evaluated projects/programmes).
        :param text_data: list of tokinized spacy docs derived from each parsed evaluation.
        :returns: tuple with sentences with contant deemed as positive output. 
        """
        ##Interim storage for idenfitied sida dependency (i.e sentences deemed relevant and docs to give context and follow-up and assess the ouput).
        identified_sida_dependency = []
        identified_sida_dependency_docs = []

        # ? function for processing similarity score on all words in entire corpus to include in spacy matcher.
        # source = nlp("depend")
        # sim_words = []
        # for doc in text_data:
        #    for tok in doc:
        #        test = similarity_test(tok, source)
        #        if test is True:
        #            sim_words.append(tok)

        # * loading of matcher, setting matcher label, and applying matcher patter/list of words/phrases
        matcher = Matcher(nlp.vocab)
        matcher.add("funding_words", None, *_FUND_WORD_LEMMA_PATTERNS)
        matcher_2 = Matcher(nlp.vocab)
        matcher_2.add(
            "sustainability_words", None, *_SUSTAINABILITY_WORD_LEMMA_PATTERNS
        )
        matcher_3 = Matcher(nlp.vocab)
        matcher_3.add("importance_words", None, *_IMPORTANCE_WORD_LEMMA_PATTERNS)

        for doc in text_data:  # .sents: ## apply limitations on docs or sentences
            # * apply matcher for "funding"
            matches = matcher(doc)  # ! entire doc
            for match_id, start, end in matches:
                string_id = nlp.vocab.strings[match_id]  # Get string representation

                if string_id == "funding_words":
                    for sent in doc.sents:  # ! senteces only
                        # * apply matcher for "sustainability"
                        matches_2 = matcher_2(sent)
                        for match_id_2, start_2, end_2 in matches_2:
                            string_id_2 = nlp.vocab.strings[match_id_2]
                            if string_id_2 == "sustainability_words":
                                for sus_sent in doc.sents:
                                    # * apply matcher for "importance"
                                    matches_3 = matcher_3(sus_sent)
                                    for match_id_3, start_3, end_3 in matches_3:
                                        string_id_3 = nlp.vocab.strings[match_id_3]
                                        if string_id_3 == "importance_words":
                                            ## * check if Sida/Sweden are referenced
                                            if (
                                                "Sida" in str(sent)
                                                or "SIDA" in str(sent)
                                                or "Swed" in str(sent)
                                            ):
                                                identified_sida_dependency.append(sent)
                                                identified_sida_dependency_docs.append(
                                                    doc
                                                )
        # * print results
        # print(len(set(identified_sida_dependency)))
        # for case in set(identified_sida_dependency):
        #    print(case, "\n")
        # print("---")
        # for d in set(identified_sida_dependency_docs):
        #    print(d, "\n")
        # print("#####")

        yield (len(set(identified_sida_dependency)),)

    def parse_file(self, docs, bin_file):
        """ Applying functions for q21 processing document/evaluation and inserting into database.
        :param docs: parsed/tokinized document/evaluation
        :param bin_file: bin files from method _nlp_processing
        :returns: inserts string from the function check_sida_dependency_to_eba on index/primay key in eba_evaluations/SQL.
        """
        for itr in self.parse_sida_dependency(docs):
            ## * index number
            doc_id = bin_file.replace("_content.bin", "")
            # * print(doc_id)
            # * evaluate and compile all doc with relevant content. See function check_sida_dependency_to_eba above
            data_for_comparission = check_sida_dependency_to_eba(itr)

            try:
                sql_str_q21 = "UPDATE eba_evaluations SET q21=? WHERE _id=?"
                self.cur.execute(sql_str_q21, (data_for_comparission, doc_id))
            except Exception as e:
                print(sql_str_q21)
                print("SQL error: ", e)
            assert self.cur.rowcount == 1, "No rows where UPDATED!!"
            print(
                "Successfully updated {} with data: {}".format(
                    doc_id, data_for_comparission
                )
            )
            self.conn.commit()


def parse_files(version: str = None, select_output: str = "eba_responses"):
    """ Processing multiple documents/evaluations by using the parse_file function from the ParseSidaDependency class."""

    version_path = _NLP_FILES_PATH / "v{}".format(version)
    with ParseSidaDependency(select_output=select_output,) as pg:
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
    # python -m q21.main
    # ! run program
    main()
    # ! evalute the result
    # eba_2017_comparison()
    pass
