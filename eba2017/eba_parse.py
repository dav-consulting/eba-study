import os, json
import pandas as pd
import re
from util import (
    db_connect,
    _PROJECT_PATH,
    _DAC_CRITERIA_VALUES_FROM_CODE,
    _DAC_CRITERIA_VARIATIONS,
    get_eba2017,
)
from .util import convert_eba_country_names, topics
import sqlite3


class ParseEBA(object):
    """ Class contains methods for parsing the results recorded results of applying the analytical framework in EBA2017:12 so 
    that they can be easily compared to results in eba_application_200413. 
    :param table_name: the name of the table where the results of the analytical framework in EBA 2017:12 gets stored
    :param primary_key_name: the name of the table primnary key
    """

    primary_key_name = "Nr"

    def __init__(self, third_party=None, restore_table=False):
        """ Creates a database connection and loads the original file. """
        self.third_party = third_party
        if third_party:
            self.primary_key_name = "f_id"
            self.table_name = "eba2017_third_party"
        else:
            self.primary_key_name = "Nr"
            self.table_name = "eba2017"

        if third_party:
            df_third_party = pd.read_excel(
                os.path.join(
                    _PROJECT_PATH, "eba2017/original_data/eba2017_third_party.xlsx"
                )
            )
            self.df = df_third_party
            self.df_case = df_third_party
        else:
            self.df = pd.read_excel(
                os.path.join(_PROJECT_PATH, "eba2017/original_data/eba2017_12.xlsx")
            )
            self.df_case = pd.read_excel(
                os.path.join(
                    _PROJECT_PATH, "eba2017/original_data/eba2017_12_case.xlsx"
                )
            )
            self.df_case[self.primary_key_name] = self.df_case["Nummer"]
            self.df_case = self.df_case.query('Nr!="Numret i filnamnet"')

        self.conn, self.cur = db_connect()
        self.column_unique_value_set = (
            {}
        )  # dictionary with unique values for each column

        self.create_table()

        # self.extract_unique_column_value_sets()  # extract dictionary with unique values for each column

    def create_table(self):
        """ Creates the table """
        drop_table = "n"
        self.cur.execute(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}' ".format(
                self.table_name
            )
        )
        table_exists = self.cur.fetchone()[0] == 1

        # if the count is 1, then table exists
        if table_exists:
            drop_table = input(
                "Table {} already exists. Do you want to reset it? (y/n)".format(
                    self.table_name
                )
            )

        if drop_table == "y" or not table_exists:
            self.cur.execute("DROP TABLE IF EXISTS {};".format(self.table_name))
            print("Dropping and creating table...")
            if self.third_party:
                self.cur.execute(
                    "CREATE TABLE {}({} TEXT PRIMARY KEY)".format(
                        self.table_name, self.primary_key_name
                    )
                )
            else:
                self.cur.execute(
                    "CREATE TABLE {}({} INTEGER PRIMARY KEY)".format(
                        self.table_name, self.primary_key_name
                    )
                )
            self.add_primary_key()
            self.create_column("eba_title")
            if self.third_party:
                self.cur.execute("SELECT _id, title FROM eba_evaluations;")
            else:
                self.create_column("f_id")
                self.cur.execute(
                    "SELECT _id, eba_match_nr, eba_match_title FROM eba_evaluations WHERE eba_match_nr IS NOT NULL"
                )
            rows = self.cur.fetchall()
            pkeys = self.df[self.primary_key_name].to_list()
            print(pkeys)
            for row in rows:
                if self.third_party:
                    if row[0] not in pkeys:
                        continue
                    self.update_table("eba_title", row[1], row[0])
                else:
                    if row[1] not in pkeys:
                        continue
                    self.update_table("f_id", row[0], row[1])
                    self.update_table("eba_title", row[2], row[1])

    def create_column(self, column_name=""):
        """ Creates a table column """
        try:
            self.cur.execute(
                "ALTER TABLE {} ADD COLUMN {} TEXT;".format(
                    self.table_name, column_name
                )
            )
            print("Successfully created column: {}".format(column_name))
        except sqlite3.OperationalError as e:
            print("Column already exists?! ", str(e))

    def add_primary_key(self):
        """ Adds a primary key """
        key_name = self.primary_key_name
        col_data = self.df[key_name]

        # self.create_column(key_name)
        for _, row in col_data.iteritems():
            try:
                if self.third_party:
                    self.cur.execute(
                        "INSERT INTO {}({}) VALUES ('{}');".format(
                            self.table_name, self.primary_key_name, row
                        )
                    )
                else:
                    self.cur.execute(
                        "INSERT INTO {}({}) VALUES ({});".format(
                            self.table_name, self.primary_key_name, row
                        )
                    )

                self.conn.commit()
            except Exception as e:
                print(e)
                print("Primary key {} already exists!".format(row))

    def update_table(self, column_name="", update_value="", pkey=None):
        """ Updates a table row """
        try:
            # sql_str = "UPDATE {} SET {}='{}' WHERE {}='{}';" # third_party
            # sql_str = "UPDATE {} SET {}='{}' WHERE {}={};"
            sql_str = "UPDATE {} SET {}=? WHERE {}=?;".format(
                self.table_name, column_name, self.primary_key_name
            )
            vals = (
                update_value,
                pkey,
            )
            self.cur.execute(sql_str, vals)
            self.conn.commit()
        except Exception as e:
            print("Exception occured: {}".format(e))

        if self.cur.rowcount < 1:
            print("Could not update table... for pkey={}".format(pkey))
        # else:
        #     print("Updated successfully {} row!".format(self.cur.rowcount))

    # def extract_unique_column_value_sets(self):
    #     """ Extracts a dictionary with a list of unique values for each column.
    #     """
    #     for col_name in self.df.columns[2:]:
    #         if self.df[col_name].dtype != "int64":
    #             col_data = self.df[col_name].str.lower().str.strip()
    #         else:
    #             col_data = self.df[col_name]
    #         self.column_unique_value_set[col_name] = list(set(col_data))

    def parse_Hallbarhet(self):
        """ Parse the hållbarhet column. """

        _value_typos_translation = {
            "det går inte läsa ut ur rapporten": "utvärderarna gör ingen bedömning/det går inte läsa ut ur rapporten",
            "insatsen bedöms i utvärderingen vara i delar hållbar i andra delar inte hållbar": "insatsen bedöms i utvärderingen vara i delar hållbar i andra delar inte hållbar",
            "insatsen bedöms vara hållbar": "insatsen bedöms vara hållbar",
            "insatsen bedöms inte vara hållbar": "insatsen bedöms inte vara hållbar",
        }  # map typos to correct strings

        col_name = "Hållbarhet?"
        new_col_name = "Hallbarhet"

        self.create_column(new_col_name)
        self.create_column(new_col_name + "_id")

        for _, row in self.df.iterrows():
            key_id, content = row["Nr"], row[col_name]
            if not isinstance(content, str):
                continue
            content_clean = content.strip().lower()
            if content_clean in _value_typos_translation.keys():
                content_clean = _value_typos_translation[content_clean]
            if (
                content_clean
                in _DAC_CRITERIA_VALUES_FROM_CODE["sustainability"].values()
            ):
                self.update_table(new_col_name, content_clean, key_id)
                content_id = next(
                    k
                    for k, v in _DAC_CRITERIA_VALUES_FROM_CODE["sustainability"].items()
                    if v == content_clean
                )
                self.update_table(
                    new_col_name + "_id", content_id, key_id,
                )
            else:
                print("Value not found!")

    def parse_Land(self):
        """ Parse the Land? column. """
        col_name = "Land?"
        new_col_name = "_Land"
        self.create_column(new_col_name)
        # self.create_column(new_col_name + "_SWE")
        for _, row in self.df.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if content:
                content = re.sub(r"\(|\)", "", content)
                updated_country_lists = convert_eba_country_names(content.strip())
                self.update_table(
                    new_col_name, updated_country_lists.strip().lower(), key_id
                )
                # self.update_table(
                #     new_col_name + "_SWE", content.strip().lower(), key_id
                # )

    def parse_Region(self):
        """ Parse the Region column. """
        _value_typos_translation = {
            "Central och Östeuropa": "öst- och centraleuropa",
            "Global (mer än en region)": "global",
            "Asien inkl. Centralasien": "öst/syd och centralasien",
            "Afrika SOS": "afrikasos",
        }  # map typos to correct strings

        col_name = "Region"
        new_col_name = "_Region"
        self.create_column(new_col_name)
        for _, row in self.df.iterrows():
            key_id, content = row["Nr"], row.get(col_name)

            if content:
                content = _value_typos_translation.get(content, content)
                content = content.strip().lower()
                self.update_table(new_col_name, content, key_id)

    def parse_Geography(self):
        """ Parse the Geografi column. """
        _value_typos_translation = {
            "Region": "regionalt",
            "region": "regionalt",
            "Global (flera världsdelar)": "global",
            "Land/lokal": "nationellt/lokalt",
        }  # map typos to correct strings
        col_name = "Geografi"
        new_col_name = "_Geografi"
        self.create_column(new_col_name)
        for _, row in self.df.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if content:
                content = _value_typos_translation.get(content, content)
                content = content.strip().lower()
                self.update_table(new_col_name, content, key_id)

    def parse_Sakomrade(self):
        """ Parse the Sakomrade column. """
        _value_typos_translation = {
            "Övrig miljö inkl vatten": "Övrig miljö inkl. vatten",
            "Jordbruk, skogsbruk inkl. fiske": "Jordbruk, skogsbruk, fiske samt landfrågor",
            "Land": "Jordbruk, skogsbruk, fiske samt landfrågor",
        }  # map typos to correct strings
        col_name = "Sakområde"
        new_col_name = "Sakomrade"
        self.create_column(new_col_name)
        for _, row in self.df.iterrows():
            key_id, content = row["Nr"], row.get(col_name)

            if content and isinstance(content, str):
                content = content.strip()
                content = _value_typos_translation.get(content, content)
                assert content in list(topics.keys()), f"Topic '{content}' not found..."
                self.update_table(new_col_name, content, key_id)

    def parse_Tidsperiod(self):
        """ Parse the Tidsperiod column. """
        _value_typos_translation = {}  # map typos to correct strings
        col_name = "Tidsperiod som utvärderas"
        new_col_name = "Tidsperiod"
        self.create_column(new_col_name)
        for _, row in self.df_case.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if isinstance(content, str):
                content = str(row[col_name]).strip()
                content = _value_typos_translation.get(content, content)
                years = []
                for match in re.finditer(
                    "(19[89][0-9](?![\w])|20[01][0-9](?![\w]))", content
                ):
                    start, end = match.span()
                    year = content[start:end]
                    years.append(int(year))
                years = sorted(years)
                if len(years) > 1:
                    try:
                        # key_id = int(key_id)
                        self.update_table(
                            new_col_name, f"{years[0]}-{years[-1]}", key_id
                        )
                    except ValueError:
                        pass

    def parse_Nar_utv(self):
        """ Parse the "När utv?" column. """
        _value_typos_translation = {
            "Precis i slutet på el direkt efter finansierad period": "end-of-phase",
            "Mid-term": "mid-term",
            "Ett tag efter finansierad period": "post-end-of-phase",
            "Övrig": "other",
        }  # map typos to correct strings
        col_name = "När utv?"
        new_col_name = "Nar_utv"
        self.create_column(new_col_name)
        for _, row in self.df_case.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if isinstance(content, str):
                content = content.strip()
                content = _value_typos_translation.get(content, content)
                try:
                    # key_id = int(key_id)
                    self.update_table(new_col_name, content, key_id)
                except ValueError:
                    pass

    def parse_I_sammanfattningen(self):
        """ Parse the 'I sammanfattning' column. """
        _value_typos_translation = {}  # map typos to correct strings
        col_name = "I sammanfattning"
        new_col_name = "I_sammanfattning"
        if self.third_party:
            for dac in _DAC_CRITERIA_VARIATIONS.keys():
                if dac != "sustainability":
                    self.create_column(new_col_name + f"_{dac}")
        self.create_column(new_col_name)

        for _, row in self.df_case.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if isinstance(content, str):
                content = content.strip().lower()
                if self.third_party:
                    for dac in _DAC_CRITERIA_VARIATIONS.keys():
                        upd_column = (
                            new_col_name + f"_{dac}"
                            if dac != "sustainability"
                            else new_col_name
                        )
                        print(upd_column)
                        if dac in content or "alla" in content:
                            self.update_table(
                                upd_column, "ja", key_id,
                            )
                        else:
                            self.update_table(
                                upd_column, "nej", key_id,
                            )
                else:
                    content = _value_typos_translation.get(content, content)
                    try:
                        self.update_table(new_col_name, content, key_id)
                    except ValueError:
                        pass

    def parse_Forslag(self):
        """ Parse the 'Förslag?' column. """
        _value_typos_translation = {}  # map typos to correct strings
        col_name = "Förslag?"
        new_col_name = "Forslag"
        if self.third_party:
            for dac in _DAC_CRITERIA_VARIATIONS.keys():
                if dac != "sustainability":
                    self.create_column(new_col_name + f"_{dac}")
        self.create_column(new_col_name)
        for _, row in self.df_case.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if isinstance(content, str):
                content = content.strip().lower()
                if self.third_party:
                    for dac in _DAC_CRITERIA_VARIATIONS.keys():
                        upd_column = (
                            new_col_name + f"_{dac}"
                            if dac != "sustainability"
                            else new_col_name
                        )
                        print(upd_column)
                        if dac in content or "alla" in content:
                            self.update_table(
                                upd_column, "ja", key_id,
                            )
                        else:
                            self.update_table(
                                upd_column, "nej", key_id,
                            )
                else:
                    content = _value_typos_translation.get(content, content)
                    try:
                        self.update_table(new_col_name, content, key_id)
                    except ValueError:
                        pass

    def parse_Donor(self):
        """ Parse the financier column. (Question 9) """
        col_name = "Ensam finansiär?"
        new_col_name = "_Finansiar"
        self.create_column(new_col_name)
        for _, row in self.df_case.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if isinstance(content, str):
                content = content.strip().lower()
                try:
                    # key_id = int(key_id)
                    if "avser strategi" in content:
                        self.update_table(new_col_name, None, key_id)
                    else:
                        self.update_table(new_col_name, content, key_id)
                except ValueError:
                    pass

    def parse_Sida_imp(self):
        """ Parse the Sidas roll column. (Question 21) """
        col_name = "Sidas roll "
        new_col_name = "_Sida_roll"
        self.create_column(new_col_name)
        for _, row in self.df_case.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if isinstance(content, str):
                content = content.strip().lower()
                try:
                    # key_id = int(key_id)
                    if "analyseras ej" in content:
                        self.update_table(new_col_name, None, key_id)
                    else:
                        self.update_table(new_col_name, content, key_id)
                except ValueError:
                    pass

    def parse_Aid_depend(self):

        """ Parse the Biståndsberoende column. """
        col_name = "Biståndsberoende"
        new_col_name = "_Bistandsberoende"
        self.create_column(new_col_name)
        for _, row in self.df_case.iterrows():
            key_id, content = row["Nr"], row.get(col_name)
            if isinstance(content, str):
                content = content.strip().lower()
                try:
                    # key_id = int(key_id)
                    if (
                        content
                        == "nej, men man skriver explicit att insatsen är beroende av bistånd"
                    ):
                        self.update_table(new_col_name, "ja", key_id)
                    else:
                        self.update_table(new_col_name, content.strip(), key_id)
                except ValueError:
                    pass


def main():
    ## initialize the class and make sure necessary tables and keys …exist.
    pe = ParseEBA()
    # # pe.parse_Hallbarhet()
    pe.parse_Land()
    # # pe.parse_Region()
    # # pe.parse_Geography()
    # # pe.parse_Sakomrade()
    # # pe.parse_I_sammanfattningen()
    # # pe.parse_Tidsperiod()
    # # pe.parse_Forslag()
    # # pe.parse_Tidsperiod()
    # # pe.parse_Nar_utv()
    pe.parse_Donor()
    pe.parse_Sida_imp()
    # # pe.parse_Aid_depend()
    pe.conn.close()

    ptp = ParseEBA(third_party=True)
    # ptp.parse_Hallbarhet()
    ptp.parse_Land()
    # ptp.parse_Region()
    # ptp.parse_Geography()
    # ptp.parse_Sakomrade()
    # ptp.parse_I_sammanfattningen()
    # ptp.parse_Forslag()
    # ptp.parse_Tidsperiod()
    # ptp.parse_Nar_utv()
    ptp.parse_Donor()
    ptp.parse_Sida_imp()
    # ptp.parse_Aid_depend()
    ptp.conn.close()


if __name__ == "__main__":
    # python -m eba2017.eba_parse
    main()
