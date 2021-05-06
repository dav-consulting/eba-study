import scrapy
from scrapy import Request
from scrapy.item import Item
import json
import urllib.request, urllib.parse, urllib.error
from fetch_evaluations.items import FetchEvaluationsItem
import pandas as pd
from fuzzywuzzy import fuzz
from typing import Dict, Any
import os


class FetchSidaEvaluations(scrapy.Spider):
    """ Web scraper (with scrapy package) that collects evaluation documents from www.sida.se. The web scraper is designed to crawl a certain part of Sida's web domain and download
    PDF-documents and metadata of the same.  

    :returns: scrapy item with the following document/evaluation parameters:
    title, publication_data, series, series_number, language, issued, authors, description, doc_url, doc, file_urls.
    """

    name = "fetch_eval"
    # custom_settings = {'LOG_LEVEL':'DEBUG'}#'DEPTH_LIMIT':4}
    allowed_domains = ["sida.se"]
    start_urls = [
        "https://www.sida.se/English/publications/publicationsearch/?subject=Sida%20Decentralised%20Evaluation&page=1&q=%20&fromDate=2011&toDate=2020&language=Engelska&sort=date&count=500"
    ]
    cwd = os.getcwd().split("/")

    # To avoid relative path confilcts for document downloads etc. we make sure scrapy is run in project top level
    assert (
        cwd[-2] == "eba"
    ), "Wrong path! Scrapy must be run in the project’s top level directory..."

    def __init__(self):
        self.drop_table = False

    ## Extract all the hyperlinks for evaluations on one page.
    def parse(self, response):
        for sub in response.xpath("/html/body/main/div/div/div[2]/ul[1]"):
            h_links = sub.xpath("//ul/li/a/h3/parent::*/@href").getall()
            for next_eval in h_links:
                yield Request(
                    response.urljoin(next_eval), callback=self.parse_eval_data
                )

    def parse_eval_data(self, response):
        """
        This function parse web data and downloads the evaluation per se.
        :param text_data: url
        :returns: scrapy item with the following document/evaluation parameters:
        title = str,
        publication_data = str,
        series = tuple,
        series_number = tuple,
        language = tuple,
        issued = tuple,
        authors = list,
        description = tuple,
        doc_url = str,
        doc = pdf,
        file_urls = scrapy item for file handling.
        """

        items = FetchEvaluationsItem()
        data = response.xpath("/html/body/main/div/div")

        ## Extract metadata under each evaluation page
        title = (
            data.xpath("/html/body/main/div/div/div[2]/article/section/h1/text()")
            .extract_first()
            .replace("\n", " ")
            .strip()
        )
        publication_date = data.xpath(
            "/html/body/main/div/div/div[2]/article/section/div/strong[contains(text(),'Publication')]/following-sibling::*/text()"
        ).extract_first()
        series = (
            data.xpath(
                "/html/body/main/div/div/div[2]/article/section/div/strong[contains(text(),'Series')]/following-sibling::*/text()"
            ).extract_first(),
        )
        series_number = (
            data.xpath(
                "/html/body/main/div/div/div[2]/article/section/div/strong[contains(text(),'Series number')]/following-sibling::*/text()"
            ).extract_first(),
        )
        language = (
            data.xpath(
                "/html/body/main/div/div/div[2]/article/section/div/strong[contains(text(),'Language')]/following-sibling::*/text()"
            ).extract_first(),
        )
        issued = (
            data.xpath(
                "/html/body/main/div/div/div[2]/article/section/div/strong[contains(text(),'Issued')]/following-sibling::*/text()"
            ).extract_first(),
        )

        ## add the function that the same name cannot be saved more than once
        authors = json.dumps(
            [
                aut.strip()
                for aut in data.xpath(
                    "/html/body/main/div/div/div[2]/article/section/div/strong[contains(text(),'Author')]/following-sibling::*/text()"
                ).getall()
            ],
            ensure_ascii=False,
            sort_keys=True,
        )
        description = (
            data.xpath(
                "/html/body/main/div/div/div[2]/article/section/div/strong[contains(text(),'Description')]/following-sibling::*/text()"
            ).extract_first(),
        )

        ## Download documents/evaluations to folder
        doc = data.xpath(
            # "/html/body/main/div/div/div[2]/article/section/div/div[1]/a/@href"
            "//div[@class='publist']/div/a/@href"
        ).extract_first()
        doc_url = response.urljoin(doc)

        ## Create unique id for each docuemnt based on url.
        # doc_id = doc_url.split("/")[-1]

        items["file_urls"] = [
            response.urljoin(doc)
        ]  ## scrapy dictated item name to be used for scrapy file handler pipeline
        items["title"] = title
        items["publication_date"] = publication_date
        items["series"] = series
        items["series_number"] = series_number
        items["language"] = language
        items["issued"] = issued
        items["authors"] = authors
        items["description"] = description
        items["doc_url"] = doc_url

        yield items
