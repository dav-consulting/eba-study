import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
import sqlite3
import os, sys
from urllib.parse import urlparse
from fuzzywuzzy import fuzz
import pandas as pd

print(sys.path)
sys.path.append("..")
print(sys.path)
from util import db_connect


from typing import (
    Dict,
    ItemsView,
)  ### object for securing the in- and output of functions, see below.


class FetchEvaluationsPipeline(object):
    """Scrapy pipeline to handle scraped data/ scrapy items and organise the data for SQL storage"""

    def __init__(self):
        self.drop_table = None
        self.create_connection()
        self.create_table()

        # self.df_eba2017_12 = pd.read_excel("../../../eba2017_12.xlsx",)
        # _id INTEGER PRIMARY KEY AUTOINCREMENT,

    def create_connection(self):
        self.conn, self.curr = db_connect()
        # self.conn = sqlite3.connect("./documents/eba_scraped_evaluations.db")
        # self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='eba_evaluations' "
        )
        table_exists = self.curr.fetchone()[0] == 1

        # if the count is 1, then table exists
        if table_exists:
            self.drop_table = input(
                "Table eba_evaluations already exists. Do you want to delete it? (y/n)"
            )

        if self.drop_table == "y" or not table_exists:
            self.curr.execute("DROP TABLE IF EXISTS eba_evaluations")
            self.curr.execute(
                """CREATE TABLE eba_evaluations(
                _id TEXT PRIMARY KEY,
                web_title TEXT,
                web_publication_date TEXT,
                web_series TEXT,
                web_series_number TEXT,
                web_language TEXT,
                web_issued TEXT,
                web_authors TEXT,
                web_description TEXT,
                web_doc_url TEXT
                )"""
            )
        # elif self.drop_table == "n" or not table_exists:
        #     print("--- Crawl deactivated ----")
        #     sys.exit()

    def store_db(self, item):
        doc_id = "{}_{}".format(
            item["series_number"][0].strip(),
            item["doc_url"].split("/")[-1].strip().replace(".pdf", ""),
        )
        try:
            self.curr.execute(
                "INSERT INTO eba_evaluations(_id,web_title,web_publication_date,web_series,web_series_number,web_language,web_issued,web_authors,web_description,web_doc_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    doc_id,
                    item["title"],
                    item["publication_date"],
                    item["series"][0],
                    item["series_number"][0],
                    item["language"][0],
                    item["issued"][0],
                    item["authors"],
                    item["description"][0],
                    item["doc_url"],
                ),
            )
        except Exception as e:
            print("Exception occured: ", e)
            self.curr.execute(
                "UPDATE eba_evaluations SET web_title=?, web_publication_date=?, web_series=?, web_series_number=?, web_language=?, web_issued=?, web_authors=?, web_description=?, web_doc_url=? WHERE _id=?",
                (
                    item["title"],
                    item["publication_date"],
                    item["series"][0],
                    item["series_number"][0],
                    item["language"][0],
                    item["issued"][0],
                    item["authors"],
                    item["description"][0],
                    item["doc_url"],
                    doc_id,
                ),
            )
        self.conn.commit()

    def process_item(self, item, spider) -> dict:
        """ This function processes items and store them in SQLite3 database. """
        self.store_db(item)
        # https://realpython.com/python-type-checking/#annotations
        return item


class NameMyFilesPipeline(FilesPipeline):
    """Function for renaming dowloaded evaluations and adding unique filenames based on the url address and series number"""

    def file_path(self, request, response=None, info=None):
        doc_name = "{}_{}".format(
            request.meta["series_number"], os.path.basename(urlparse(request.url).path)
        )
        doc_path = "documents/evaluations/{}".format(doc_name)
        return doc_path

    def get_media_requests(self, item, info):
        file_url = item["doc_url"]
        series_number = (
            item["series_number"][0].strip() if len(item["series_number"]) > 0 else None
        )
        meta = {"series_number": series_number}
        yield Request(url=file_url, meta=meta)
