import sqlite3
import click
import re
import logging

logging.basicConfig(level=logging.CRITICAL)
from collections import Counter
import pycountry
import country_converter

from util import _NLP_FILES_PATH, _PARSED_FILES_PATH, db_connect, get_eba_evaluations
from util import load_spacy_docbin_file as lsd
from q3_q5.util import (
    _DAC_DONORS,
    _UN_REGION,
    _PY_COUNTRIES,
    _PY_COUNTRIES_EX_SWE,
)


class ParseGeo:
    def __init__(self, select_output):
        self.conn, self.cur = db_connect()
        self.select_output = select_output
        if select_output == "recipients":
            self.create_column("q3")
            self.create_column("q4")
            self.create_column("q5")
        else:
            self.create_column("q3_" + select_output)

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

    def parse_country(self, text_data: list = []):
        """ Response to question 3 and input to question 4 and 5. Parsing countries based on the packages pycountry and contry-converter. Tokenized text strings from decentralised Sida evaluations
        are parsed using spaCy's English NER model. A threshold is set to a minimum of 5 mentions of a country if it is to be registered as a positive observation (this is dictated in the parse_file
        function below). 

        :param text_data: list of tokinized spacy sentences.
        :param output: list of string/s relating to context-based categories and meta data:
            'recipients' for recipient countries;
            'donors' for donor countries;
            'evaluation_result' for meta data on conducted matches;
            'non_matches' for entities that did not match.
        
        :returns: List of tuples (strings for non-matches) for the various context-based catagories (see output parameter).
        """

        cc = country_converter.CountryConverter()
        evaluation_result = []
        errors = []
        counter = []
        for doc in text_data:
            ## using spaCy NER for extracting countries
            # doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    # print(ent)
                    ent_text = re.sub(
                        r"^[\+\-\[\]\(\)\{\}\#\.!0-9]+", "", ent.text
                    )  ## for adjusting entities with various non-alphabetic characters as a first character.
                    standard_name = cc.convert(names=ent_text, to="name_short")

                    ## evaluation 1 - check against pycountry name
                    if ent.text in [country.name for country in pycountry.countries]:
                        # print("a", ent_text)
                        evaluation_result.append(("a", ent.text))
                        counter.append(ent.text)

                    ## evaluation 2 - check against pycountry Aplha2
                    elif standard_name in [
                        country.name for country in pycountry.countries
                    ]:
                        # print("b", standard_name)
                        evaluation_result.append(("b", standard_name))
                        counter.append(standard_name)

                    ## evaluation 3 - check against pycountry fuzzy match
                    else:
                        if (
                            len(ent.text) < 4
                        ):  ## inserted to avoid abbrivations to me included and be mapped against Pycountry aplha3/ country abbrivations
                            continue
                        else:
                            try:
                                evaluation_result.append(
                                    (
                                        "c",
                                        pycountry.countries.search_fuzzy(ent.text)[
                                            0
                                        ].name,
                                    )
                                )
                                # print("c", ent_text)
                                counter.append(
                                    pycountry.countries.search_fuzzy(ent.text)[0].name
                                )
                            except:
                                errors.append(None)

        ## sorting recipients, donors and meta-data
        recipients = []
        donors = []
        for c in Counter(counter).most_common():
            if c[0] in _DAC_DONORS:
                donors.append(c)
            else:
                recipients.append(c)

        results = {
            "recipients": recipients,
            "donors": donors,
            "evaluation_result": evaluation_result,
            "non_matches": errors,
        }
        # print(results)
        yield results.get(self.select_output)

    def country_to_unregion(self, input_q3):
        """Response to question 4.
        UNregions from coco map countries from estimation output from q3/parse_country function.
        Note that the UNregions do not corresponde with the arbitraty regions in EBA2017-12. In order to assess the accuracy the UNregions have been mapped against the EBA2017-12 categories.  - need to convert in ebaparse_2017? 

        :param input_q3: first element in tuple - output from q3/parse_country function
        :returns: string for estimated geographical focus

        """

        results = []
        for country in input_q3:
            try:
                if country in _PY_COUNTRIES:
                    _to_region = [v for k, v in _UN_REGION.items() if country == k][0]
                    results.append(_to_region)
                else:
                    _lookup_country = pycountry.countries.search_fuzzy(country)[0].name
                    _to_region_2 = [
                        v for k, v in _UN_REGION.items() if _lookup_country == k
                    ][0]
                    results.append(_to_region_2)
            except:
                pass
        # print(results)

        return set(results)

    def geo_focus_est(self, input_q3, input_q4, bin_file):
        """Response to question 5. Output from q3 and q4 are utilized to estimate geo focus with general logic: 
        Country/local - A) if a single recipent country is part of evaluation title; B) if A=None - only one country in q3 output; 
        Region - if more than one country in q3 output and less than two regions q4 output; 
        Global - if more than two regions in q4 output;

        :param input_q3: first element in tuple - output from q3/parse_country function
        :param input_q4: set - output from q4/country_to_region

        :returns: string for estimated geographical focus
        """
        doc_id = bin_file.replace("_content.bin", "")
        country_in_title = []
        for title in get_eba_evaluations("_id, title"):
            if title[0] == doc_id:
                for c in _PY_COUNTRIES_EX_SWE:
                    if c in title[1]:
                        country_in_title.append(c)
        if len(country_in_title) == 1:
            return "Country/local"
        elif len(input_q3) == 1:
            return "Country/local"
        elif (len(input_q3) > 1) & (len(input_q4) <= 2):
            return "Region"
        elif len(input_q4) > 2:
            return "Global"
        else:
            return None

    def parse_file(self, docs, bin_file):
        """ Applying functions for q3, q4 and q5 and processing document/evaluation and inserting into database.

        :param docs: parsed/tokinized document/evaluation
        :param bin_file: bin files from method _nlp_processing

        :returns: inserts string with countries/entities that has been identified based on threshold values and inserting the string on index/primay key in eba_evaluations/SQL.
        """
        for itr in self.parse_country(docs):
            ## Response output to q3 - single out countries mentioned 5 times or more.
            list_common_countries = [
                result[0] for result in itr if result[1] > 4
            ]  # threshold more than 5
            final_countries = "; ".join([ii for ii in list_common_countries])

            ## Response output to q4 - convert countries into unique list of UN regions.
            interim_regions = [
                result[0] for result in itr if result[1] > 10
            ]  # note that the countries have the threshold more than 11
            un_regions_set = self.country_to_unregion(interim_regions)
            final_un_regions_str = "; ".join(un_regions_set)

            ## index number
            doc_id = bin_file.replace("_content.bin", "")

            ## Response output to q5 - estimate geo focus based on output from q3-4
            geo_focus = self.geo_focus_est(interim_regions, un_regions_set, doc_id)

            ## inserting q3 results/countries into database
            try:
                sql_str_q3 = "UPDATE eba_evaluations SET q3=? WHERE _id=?"
                self.cur.execute(sql_str_q3, (final_countries, doc_id))
            except Exception as e:
                print(sql_str_q3)
                print("SQL error: ", e)
            assert self.cur.rowcount == 1, "No rows where UPDATED!!"
            print(
                "Successfully updated {} with data: {}".format(doc_id, final_countries)
            )

            ## inserting q4 results/regions into database
            try:
                sql_str_q4 = "UPDATE eba_evaluations SET q4=? WHERE _id=?"
                self.cur.execute(sql_str_q4, (final_un_regions_str, doc_id))
            except Exception as e:
                print(sql_str_q4)
                print("SQL error: ", e)
            assert self.cur.rowcount == 1, "No rows where UPDATED!!"
            print(
                "Successfully updated {} with data: {}".format(
                    doc_id, final_un_regions_str
                )
            )

            ## inserting q5 geo estimate into database
            try:
                sql_str_q5 = "UPDATE eba_evaluations SET q5=? WHERE _id=?"
                self.cur.execute(sql_str_q5, (geo_focus, doc_id))
            except Exception as e:
                print(sql_str_q5)
                print("SQL error: ", e)
            assert self.cur.rowcount == 1, "No rows where UPDATED!!"
            print("Successfully updated {} with data: {}".format(doc_id, geo_focus))
            self.conn.commit()


def parse_files(version: str = None, select_output: str = "recipients"):
    """ Processing multiple documents/evaluations by using the parse_file function from the parseGeo class."""
    version_path = _NLP_FILES_PATH / "v{}".format(version)
    with ParseGeo(
        select_output=select_output,
    ) as pg:  ### KOLLA DENNA TÄNK PÅ JOBBA MED FILER.
        nlp = None
        for bin_file in version_path.iterdir():

            if bin_file.name.endswith(".bin"):
                version_file_path = version_path / bin_file

                # if bin_file.name == "2012:18_15186_content.bin":
                docs, nlp = lsd(version_file_path, nlp)

                pg.parse_file(docs, bin_file.name)


@click.command()
@click.option(
    "--version", default="1", prompt="Which version number should be assessed?",
)
@click.option(
    "--select_output",
    default="recipients",
    prompt="Choose output type:",
    type=click.Choice(["recipients", "donors"]),
)
def main(version, select_output):
    parse_files(version, select_output)


if __name__ == "__main__":
    # python -m q3.[filename]
    main()
    pass
