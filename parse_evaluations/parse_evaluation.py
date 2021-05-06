from operator import itemgetter
import fitz  # PyMuPDF package for reading pdf's
import os
from pathlib import Path
import json
import click
from urllib import request
from collections import Counter
from typing import Any, Mapping, Optional, Sequence, Tuple, Union, List, Dict
import re
from fuzzywuzzy import fuzz
from itertools import product

from util import (
    _PARSED_FILES_PATH,
    _FETCHED_FILES_PATH,
    _PROJECT_PATH,
    load_jsonl,
    dump_jsonl,
)


_ROMAN_NUMERAL_PATTERN = (
    r"^(?=\b[MDCLXVI]+\b)M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})"
)
_SECTION_DIGIT_PATTERN = r"^([0-9]+[\.]?)+"
_SECTION_DIGIT_DOT_SPACE_PATTERN = r"^([0-9]+[\.])+[\s]+"
_SPECIAL_CHAR_PATTERNS = r"[\n\r\t]"
_CHAR_TO_REMOVE = [
    "\u00a0",
    "\u00ad",
    "\u2010",
    "\u2013",
    "\u2022",
    "\u201c",
    "\u201d",
]


class ParseDoc:
    """
    Parsing of SIDA evaluation PDF documents (https://www.sida.se/English/publications/publicationsearch/). 

    Uses Python package 'PyMuPDF' to extract text from pdf file. The extracted text contains info on e.g. font size, text color
    and position on page for all content identified as text string. Based on this info the ParseDoc class contains methods for parsing 
    the content for auxillary meta data. This includes identifying whether an extracted text string belongs to a footnote, page number, 
    table of content, header or main text (paragraphs). The class also contains methods for structuring the table of contents and
    linking each reference to its header so that it can be verified to which header each paragraph in the text belongs. 

    All extracted and structured text is outputed to a json file where the last lines contain the meta an summary stats.

    """

    def __init__(
        self,
        doc_path,
        font_size_remainder: int = None,
        granularity: bool = False,
        pageNumberStyleMatch=None,
    ):
        """
        Initializes parsing class. 
        :param doc_path: location of PDF file to be parsed.
        :param font_size_remainder: level of parsing detail for font size.
        :param granularity: include font type in parsing.
        :param pageNumberStyleMatch: granularity of page numbers can be set to rough or exact or any (exact: font and size must be equal; rough: size must be equal, font must almost match; else: match on font size only)

        """
        self.doc = fitz.open(doc_path)
        self.filename = doc_path.split("/")[-1]
        self.doc_length = len(self.doc)
        self.styles = None
        self.font_counts = None
        self.parsed_content = []
        self.font_size_remainder = font_size_remainder
        self.pageNumberStyleMatch = pageNumberStyleMatch
        self.granularity = granularity
        self.page_numbers = None
        self.max_page_num_bbox = None  # Max of all bbox coordinates for page numbers
        self.footnotes = None
        self.size_tags = None
        self.toc = []

    @staticmethod
    def romanToInt(s: str) -> int:
        """ Convert Roman numeral to int"""
        roman = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50,
            "C": 100,
            "D": 500,
            "M": 1000,
            "IV": 4,
            "IX": 9,
            "XL": 40,
            "XC": 90,
            "CD": 400,
            "CM": 900,
        }
        i = 0
        num = 0
        while i < len(s):
            if i + 1 < len(s) and s[i : i + 2].upper() in roman:
                num += roman[s[i : i + 2].upper()]
                i += 2
            else:
                num += roman[s[i].upper()]
                i += 1
        return num

    @staticmethod
    def clean_text(text):
        for rep in _CHAR_TO_REMOVE:
            text = text.replace(rep, "")
        return text.strip()

    @staticmethod
    def _remove_rowbreak_dashes(
        prev_s: dict,
        s_text: str,
        block_text: str,
        line_id: int,
        no_space_between_spans: bool,
    ) -> str:
        """If long words at the end of a sentence are cutoff with a dash then we remove it before joining it with the previous line."""
        if prev_s.get("text")[-1] == "-" and prev_s["line_id"] < line_id:
            prev_span_words = prev_s["text"][0:-1].split()
            span_words = s_text.split()
            if len(prev_span_words) > 0 and len(span_words) > 0:
                block_text = block_text[0:-1] + s_text
                removed_dash = True
            else:
                block_text += " " + s_text
        else:
            block_text += s_text if no_space_between_spans else " " + s_text
        return block_text

    @staticmethod
    def _max_bbox(a: tuple, c: tuple) -> tuple:
        """ Get outer bounds of two bboxes. """
        return (min(a[0], c[0]), min(a[1], c[1]), max(a[2], c[2]), max(a[3], c[3]))

    def extract_page_numbers(self, potential_page_numbers: List[Tuple]) -> List[Dict]:
        """ Method for extracting page numbers. Takes list of potential page numbers 
        (digits on page smaller than the number pages present in doc). Looks for the longest sequence of 
        numbers in doc with one number per page and incremented by 1.

        :returns: List of dicts potential page numbers (text), corresponding (bbox) and page_id.
        """
        pageNumberStyleMatch = self.pageNumberStyleMatch
        potential_page_numbers = sorted(
            potential_page_numbers, key=lambda x: x[2]
        )  # sort by page_id
        potential_page_numbers_by_page_id = {}

        for (
            ppn,
            bbox,
            pageId,
            styles,
            verticalPage,
            numeral_type,
        ) in potential_page_numbers:
            potential_page_numbers_by_page_id.setdefault(pageId, []).append(
                (ppn, bbox, styles, verticalPage, numeral_type)
            )

        cnt_ppn = len(potential_page_numbers)
        potential_page_sequence = {}
        for idx, val in enumerate(potential_page_numbers):
            numeral_style = "arabic" if val[0].isdigit() else "roman"
            ppn = int(val[0]) if val[0].isdigit() else self.romanToInt(val[0])
            _, y0, _, y1 = val[1]
            pageId = val[2]
            styles = val[3]
            verticalPage = val[4]

            for ii in range(1, cnt_ppn + 1):
                nextPageCandidate = ()
                nextPageIdNumbers = potential_page_numbers_by_page_id.get(
                    pageId + ii, []
                )

                for (
                    _ppn,
                    bbox,
                    _styles,
                    _verticalPage,
                    numeral_type,
                ) in nextPageIdNumbers:
                    # Next page number must equal the previous number + 1
                    _numeral_style = "arabic" if _ppn.isdigit() else "roman"
                    _ppn_str = _ppn
                    _ppn = int(_ppn) if _ppn.isdigit() else self.romanToInt(_ppn)

                    if _ppn == ppn + ii and numeral_style == _numeral_style:
                        error_sum = abs(bbox[1] - y0) + abs(bbox[3] - y1)

                        if pageNumberStyleMatch == "exact":
                            style_match = all(
                                [_styles.get(k) == v for k, v in styles.items()]
                            )
                        elif pageNumberStyleMatch == "rough":
                            style_match = any(
                                [
                                    x == y
                                    for x, y in product(
                                        _styles["font"].split("+"),
                                        styles["font"].split("+"),
                                    )
                                ]
                            ) * (_styles["size"] == styles["size"])
                        else:
                            style_match = _styles["size"] == styles["size"]

                        # if page direction is the same as start page and error_sum is high then it is likely not a page number
                        if verticalPage == _verticalPage and error_sum > 200:
                            continue

                        if nextPageCandidate:
                            prev_bbox = nextPageCandidate[1]
                            nextPageCandidate = (
                                (
                                    _ppn_str,
                                    bbox,
                                    pageId + ii,
                                    styles,
                                    _verticalPage,
                                    error_sum,
                                    style_match,
                                    numeral_type,
                                )
                                if error_sum
                                < (abs(prev_bbox[1] - y0) + abs(prev_bbox[3] - y1))
                                and style_match
                                else nextPageCandidate
                            )
                        elif style_match:
                            nextPageCandidate = (
                                _ppn_str,
                                bbox,
                                pageId + ii,
                                styles,
                                _verticalPage,
                                error_sum,
                                style_match,
                                numeral_type,
                            )

                if len(nextPageCandidate) > 0:
                    potential_page_sequence[idx] = potential_page_sequence.get(
                        idx, [val]
                    ) + [nextPageCandidate]
                else:
                    break

        page_numbers = []
        added_page_number_sequence_start = []
        for idx, val in sorted(
            potential_page_sequence.items(), key=lambda item: len(item[1]), reverse=True
        ):

            # if idx == 0:
            page_number_sequence = []
            for v in val:
                id_str = v[0] + str(v[1])
                if id_str in added_page_number_sequence_start:
                    break
                else:
                    page_number_sequence.append(
                        {
                            "text": v[0],
                            "bbox": v[1],
                            "page_id": v[2],
                            "verticalpage": v[4],
                        }
                    )
                    added_page_number_sequence_start.append(id_str)
            if (
                len(page_number_sequence) > 4
            ):  # page number sequences are assumed to be at least 5
                page_numbers += page_number_sequence

        # Calculate max bounding box for vertical page numbers
        for ii, p in enumerate(page_numbers):
            if ii == 0:
                self.max_page_num_bbox = p["bbox"]
            if self.max_page_num_bbox and p["verticalpage"]:
                self.max_page_num_bbox = self._max_bbox(
                    p["bbox"], self.max_page_num_bbox
                )

        return page_numbers

    def font_tags(self) -> dict:
        """Returns dictionary with font sizes as keys and tags as value.

        Note: fonts_and_page_numbers() must be run beforehand.

        :return: all element tags based on font-sizes
        """
        granularity = self.granularity
        font_counts, styles = self.font_counts, self.styles
        p_style = styles[
            font_counts[0][0]
        ]  # get style for most used font by count (paragraph)
        p_size = p_style["size"]  # get the paragraph's size
        p_font = p_style["font"]  # get the paragraph's font

        # sorting the font sizes high to low, so that we can append the right integer to each tag
        font_sizes = []
        if granularity:
            for (font_size, count) in font_counts:
                font_sizes.append(font_size.split("_"))
            font_sizes.sort(key=lambda x: float(x[0]), reverse=True)
        else:
            for (font_size, count) in font_counts:
                font_sizes.append(float(font_size))
            font_sizes.sort(reverse=True)

        # aggregating the tags for each font size
        idx, p_idx = 0, None
        size_tags = {}
        for size in font_sizes:
            idx += 1
            if isinstance(size, list):
                identifier = "{0}_{1}".format(size[0], size[1])
                font = size[1]
                size = float(size[0])
            else:
                identifier = size
                size = float(size)
                font = None
            if size == p_size:
                if granularity:
                    if p_font == font:
                        size_tags[identifier] = "<p>"
                        p_idx = idx
                        idx = 0
                    else:
                        size_tags[identifier] = (
                            "<h{0}>".format(p_idx) if p_idx else "<h{0}>".format(idx)
                        )
                        p_idx += 1
                else:
                    size_tags[identifier] = "<p>"
            if size > p_size:
                size_tags[identifier] = "<h{0}>".format(idx)
            elif size < p_size:
                size_tags[identifier] = "<s{0}>".format(idx)
        if granularity:
            size_tags = dict(
                sorted(size_tags.items(), key=lambda kv: float(kv[0].split("_")[0]))
            )
        else:
            size_tags = dict(sorted(size_tags.items(), key=lambda kv: float(kv[0])))
        self.size_tags = size_tags
        return size_tags

    def fonts_and_page_numbers(
        self, granularity: bool = False
    ) -> Tuple[List, Dict, List]:
        """Extracts fonts and their usage in PDF documents. Also extracts page numbers if exists. 

        Caveats: Page numbers assume a sequence incremented by 1 for every new page. Hence if page numbering starts over at end of document (e.g. in the TOR/ANNEX) these page numbers will not be included.

        :param granularity: also use 'font', 'flags' and 'color' to discriminate text
        :returns: Most used Fonts sorted by count, List of font style information according to granularity, List of Page numbers and bbox info
        """
        doc = self.doc
        doc_length = len(doc)

        styles = {}
        font_counts = {}
        potential_page_numbers = []
        font_size_remainder = self.font_size_remainder
        granularity = self.granularity
        page_numbers = None

        for page_id, page in enumerate(doc):
            page_dict = page.getText("dict")
            blocks = page_dict["blocks"]
            for b in blocks:  # iterate through the text blocks
                if b["type"] == 0:  # block contains text
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            font_size = (
                                round(s["size"], font_size_remainder)
                                if font_size_remainder
                                else s["size"]
                            )
                            if granularity:
                                identifier = "{0}_{1}".format(font_size, s["font"])
                                styles[identifier] = {
                                    "size": font_size,
                                    "font": s["font"],
                                }
                            else:
                                identifier = "{0}".format(font_size)
                                styles[identifier] = {
                                    "size": font_size,
                                    "font": s["font"],
                                }
                            bbox = s["bbox"]
                            text = s["text"].strip()

                            # if text str is digit and digit is smaller than doc length + increment (some docs have more pages than numbered)
                            if (
                                len(text) < 6 and text.count("+") == 0
                            ):  # page numbers must be smaller than 10000
                                try:
                                    arabic_page_number = (
                                        0 <= int(text) < (doc_length + 50)
                                    )
                                except ValueError:  # raises ValueError f text cannot be converted to int
                                    arabic_page_number = False

                                roman_numeral = re.search(
                                    _ROMAN_NUMERAL_PATTERN, text.upper()
                                )

                                if arabic_page_number or (
                                    roman_numeral
                                    and (
                                        roman_numeral.span()[1]
                                        - roman_numeral.span()[0]
                                    )
                                    == len(text)
                                ):
                                    verticalPage = int(page_dict["height"]) > int(
                                        page_dict["width"]
                                    )
                                    potential_page_numbers.append(
                                        (
                                            text,
                                            bbox,
                                            page_id,
                                            styles[identifier],
                                            verticalPage,
                                            "digit" if text.isdigit() else "roman",
                                        )
                                    )

                            font_counts[identifier] = (
                                font_counts.get(identifier, 0) + 1
                            )  # count the fonts usage

        page_numbers = self.extract_page_numbers(potential_page_numbers)

        # print("potential_page_numbers: ", potential_page_numbers)
        # print("page_numbers: ", page_numbers)

        font_counts = sorted(
            font_counts.items(), key=itemgetter(1), reverse=True
        )  # returns list [(font, frequency),...] sorted by frequency

        if len(font_counts) < 1:
            raise ValueError("Zero discriminating fonts found!")

        self.styles = styles
        self.font_counts = font_counts
        self.page_numbers = page_numbers

        return font_counts, styles, page_numbers

    def get_footnotes(self) -> List[Dict]:
        """Identifies footnotes (numbers) in PDF document. 

        Caveats: Broken footnotes (i.e. footnote continues to next page is not capture.)

        :return: list of identified footnotes in text and at page bottom.
        """
        assert self.size_tags, "Size tags need to be calculated first"

        doc = self.doc
        doc_length = len(doc)
        prev_s = {}
        potential_footnotes = []
        font_size_remainder = self.font_size_remainder
        size_tags = self.size_tags
        granularity = self.granularity
        added_potential_footnote = False
        for page_id, page in enumerate(doc):
            page_dict = page.getText("dict")
            blocks = page_dict["blocks"]
            potential_page_footnotes = []
            for b in blocks:  # iterate through the text blocks
                if b["type"] == 0:  # block contains text
                    for line_id, l in enumerate(
                        b["lines"]
                    ):  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            font_size = (
                                round(s["size"], font_size_remainder)
                                if font_size_remainder
                                else s["size"]
                            )
                            s["line_id"] = line_id

                            bbox = s["bbox"]
                            text = s["text"].strip()
                            font = s["font"]

                            if added_potential_footnote:
                                if len(potential_page_footnotes) > 0:
                                    potential_page_footnotes[-1]["next_s"] = {
                                        "bbox": bbox,
                                        "size": font_size,
                                    }
                                added_potential_footnote = False

                            if text.isdigit():
                                potential_page_footnotes.append(
                                    {
                                        "text": text,
                                        "page_id": page_id,
                                        "bbox": bbox,
                                        "size": font_size,
                                        "font": font,
                                        "is_page_bottom": False,
                                        "prev_s": {
                                            "bbox": prev_s.get("bbox"),
                                            "size": prev_s.get("size"),
                                        },
                                        "next_s": None,
                                    }
                                )
                                added_potential_footnote = True

                        prev_s = s

            # count page frequency identified potential footnote digits
            ppf_count = dict(Counter([pf["text"] for pf in potential_page_footnotes]))

            # add ppf_count key to dict (counts number of occurences of potential footnote digit on page)
            potential_page_footnotes = [
                {**ppf, **{"ppf_count": ppf_count[ppf["text"]]}}
                for ppf in potential_page_footnotes
            ]

            # Create a list of invalid potential page footnotes
            # Footnotes are invalid if tag is paragraph or header or if not subscripted
            invalid_footnotes = []

            for idx, pf in enumerate(potential_page_footnotes):
                size_tag = (
                    size_tags["{}_{}".format(pf["size"], pf["font"])]
                    if granularity
                    else size_tags[pf["size"]]
                )

                if "<h" in size_tag or "<p" in size_tag:
                    invalid_footnotes.append(idx)
                elif not (
                    pf["next_s"] == None
                    or pf["prev_s"]["size"] > pf["size"]
                    or pf["next_s"]["size"] > pf["size"]
                ):
                    invalid_footnotes.append(idx)

            # Delete all invalid footnotes
            for idx in sorted(invalid_footnotes, reverse=True):
                del potential_page_footnotes[idx]

            # Create a new count page frequency of identified potential footnotes
            ppf_count = dict(Counter([pf["text"] for pf in potential_page_footnotes]))

            # Add potential page footnotes to potential document footnotes (sort using frequency counts)
            added_page_footnotes = []
            for ppf in potential_page_footnotes:
                pf_count = dict(Counter([pf["text"] for pf in potential_footnotes]))
                if len(potential_footnotes) > 0:
                    if (
                        ppf_count[ppf["text"]] == 2
                        and int(ppf["text"]) == int(potential_footnotes[-1]["text"]) + 1
                        and ppf["text"] not in added_page_footnotes
                    ):

                        ppf["ppf_count"] = 2
                        potential_footnotes.append(ppf)
                        added_page_footnotes.append(ppf["text"])
                    elif (
                        ppf_count[ppf["text"]] == 2
                        and pf_count.get(ppf["text"], 10) < 2
                    ):
                        ppf["ppf_count"] = 2
                        ppf["is_page_bottom"] = True
                        potential_footnotes.append(ppf)
                        added_page_footnotes.append(ppf["text"])
                elif ppf_count[ppf["text"]] == 2:
                    ppf["ppf_count"] = 2
                    potential_footnotes.append(ppf)
                    added_page_footnotes.append(ppf["text"])

        self.footnotes = potential_footnotes
        return potential_footnotes

    def parse_content(self) -> List[Dict]:
        """Extracts headers & paragraphs from PDF and return texts with element tags.
        Identifies also if text excerpt is a page number or a footnote.

        :param write_files: if True outputs a markdown and text file of parsed document.
        :return: List of text blocks with pre-prended element tags, type (footnote, page_number,...).
        """
        doc, size_tag = self.doc, self.size_tags
        parsed_content = []  # list with headers and paragraphs
        prev_s, ps = (
            {},
            {},
        )  # prev_s: previous span / ps: previous non empty string span
        prev_line_id, prev_block_id, prev_line_length = 0, 0, 0
        s_footnote = {}
        prev_page_id = 0
        cnt_spans = 0
        last_footnote_id_pos = -1
        block_dict = {}
        granularity = self.granularity
        font_size_remainder = self.font_size_remainder
        potential_header = ""
        toc = ""  # temporary table of content holder
        toc_numbers = []
        toc_page_ids = set()  # temporary table of content page_ids holder
        for page_id, page in enumerate(doc):
            is_new_footnote = False
            blocks = page.getText("dict")["blocks"]
            page_number = next(
                (p for p in self.page_numbers if p.get("page_id") == page_id), None
            )
            page_footnotes = [f for f in self.footnotes if f.get("page_id") == page_id]
            for block_id, b in enumerate(blocks):  # iterate through the text blocks
                if b["type"] == 0:  # this block contains text

                    # REMEMBER: multiple fonts and sizes are possible IN one block
                    for line_id, l in enumerate(
                        b["lines"]
                    ):  # iterate through the text lines
                        spans_length = len(l["spans"])
                        line_length = l["bbox"][2] - l["bbox"][0]

                        for span_id, s in enumerate(
                            l["spans"]
                        ):  # iterate through the text spans
                            # s["text"] = s["text"].encode("ascii", "ignore").decode()

                            # s_text = self.clean_text(
                            #    s["text"]
                            # )  # removing whitespaces and unicode chars
                            s_text = "{}".format(s["text"].strip())
                            s["size"] = (
                                round(s["size"], font_size_remainder)
                                if font_size_remainder
                                else s["size"]
                            )
                            s_size = s["size"]
                            s_bbox = s["bbox"]

                            # whether to distinguish between font type in tags
                            if granularity:
                                s_tag = size_tag["{}_{}".format(s_size, s["font"])]
                            else:
                                s_tag = size_tag[s_size]
                            s["tag"] = s_tag

                            # Is the span a page number?
                            is_page_number = False
                            if page_number and page_number["bbox"] == s_bbox:
                                is_page_number = True

                            # create a temporary table of content text storage for header identification below
                            if page_id < 20:
                                if "..." in s_text or page_id in toc_page_ids:

                                    if is_page_number == False:
                                        toc += s["text"]
                                        toc_number = re.search(
                                            _SECTION_DIGIT_PATTERN[1:], s_text
                                        )
                                        if toc_number and not re.search(
                                            r"[\.]{2,}[\s]?[0-9]+", s_text
                                        ):
                                            toc_numbers.append(toc_number.group())
                                        toc_page_ids.add(page_id)

                            # if line contains only one span and this span only contains whitespace then we assume a new paragraph has started -> store and commence new block
                            if spans_length == 1 and len(s_text) == 0:
                                if block_dict:
                                    parsed_content.append(block_dict)
                                block_dict = {}
                                last_new_paragraph_line = (block_id, line_id)
                                break

                            s_color = s["color"]
                            s["line_id"] = line_id
                            s["block_id"] = block_id

                            if s_text:
                                cnt_spans += 1
                                for footnote in page_footnotes:
                                    if (
                                        s_text == footnote["text"]
                                        and s_bbox == footnote["bbox"]
                                    ):
                                        is_new_footnote = True
                                        s_footnote = footnote
                                        break

                                font_type_changed = s["font"] != ps.get("font")
                                block_or_line_change = line_id != ps.get(
                                    "line_id"
                                ) or block_id != ps.get("block_id")

                                # A new paragraph should imply a switch either a new line_id or block_id.
                                # The difference between current span y0 and previous span y1 should also be close to previous text size.
                                # Current span y0 and y1 should also differ significantly
                                if (
                                    ps
                                    and block_or_line_change
                                    and abs(s_bbox[1] - ps["bbox"][3])
                                    > ps.get("size", 5) * 0.85
                                    and abs(s_bbox[1] - ps["bbox"][1]) > 2
                                    and abs(s_bbox[3] - ps["bbox"][3]) > 2
                                ):
                                    plausible_new_paragraph = True
                                else:
                                    plausible_new_paragraph = False

                                # Short lines may also signify plausible new paragraphs or lines starting with e.g. 3.1.
                                if not plausible_new_paragraph:
                                    if (
                                        ps
                                        and (
                                            line_id != ps.get("line_id")
                                            or block_id != ps.get("block_id")
                                        )
                                        and (
                                            (
                                                font_type_changed
                                                and line_length * 0.7 > prev_line_length
                                            )
                                            or re.search(
                                                _SECTION_DIGIT_DOT_SPACE_PATTERN,
                                                s["text"],
                                            )
                                        )
                                    ):
                                        plausible_new_paragraph = True

                                # Is there a space between spans
                                no_space_between_spans = False
                                if (
                                    prev_s
                                    and block_or_line_change == False
                                    and prev_s.get("text")[-1] != " "
                                ) and s["text"][0] != " ":
                                    no_space_between_spans = True

                                # header detection
                                # if page_id == 31 and re.search(
                                #     _SECTION_DIGIT_PATTERN[1:], s_text
                                # ):
                                #     print(
                                #         "potential_header",
                                #         s_text,
                                #         s_text.lower() in toc.lower(),
                                #     )
                                #     # print(toc)

                                end_of_header = False
                                if (
                                    potential_header == ""
                                    and re.search(_SECTION_DIGIT_PATTERN[1:], s_text)
                                    and s["text"].lower() in toc.lower()
                                ):
                                    potential_header = s["text"].lower()
                                elif (
                                    potential_header
                                    and (potential_header + s["text"].lower()).strip()
                                    in toc.lower()
                                ):
                                    potential_header += s["text"].lower()
                                elif (
                                    len(potential_header) > 10
                                    and potential_header.lower() in toc.lower()
                                ):
                                    end_of_header = True
                                    potential_header = ""
                                else:
                                    potential_header = ""

                                # if (
                                #     potential_header
                                #     and font_type_changed == False
                                #     and is_page_number == False
                                #     and potential_header.lower() in toc.lower()
                                #     # and s_size == ps.get("size", 0)
                                # ):
                                #     if page_id == 31:
                                #         print(
                                #             "xxxx", potential_header, font_type_changed
                                #         )
                                #     potential_header += s["text"]
                                # elif (
                                #     len(potential_header) > 10
                                #     and potential_header.lower() in toc.lower()
                                # ):
                                #     end_of_header = True
                                #     potential_header = ""
                                # else:
                                #     potential_header = ""

                                # if not plausible_new_paragraph:
                                #     if ps and (
                                #         line_id != ps.get("line_id")
                                #         or block_id != ps.get("block_id")
                                #     ):
                                #         if (
                                #             ps.get("font") != s["font"]
                                #             and line_length * 0.4 > prev_line_length
                                #         ) or re.search(_SECTION_DIGIT_PATTERN, s_text):
                                #             plausible_new_paragraph = True

                                # # # Short lines may also signify plausible new paragraphs
                                # if not plausible_new_paragraph:
                                #     if (
                                #         ps
                                #         and (
                                #             line_id != ps.get("line_id")
                                #             or block_id != ps.get("block_id")
                                #         )
                                #         and abs(s_bbox[1] - ps["bbox"][3])
                                #         > ps.get("size", 5) * 0.85
                                #         and abs(s_bbox[0] - s_bbox[2]) * 0.5
                                #         > abs(ps["bbox"][0] - ps["bbox"][2])
                                #     ):
                                #         plausible_new_paragraph = True

                                # if page_id == 31 and 0 < block_id < 10:
                                #     # print("toc", toc_numbers)
                                #     print(
                                #         s_text,
                                #         # round(abs(s_bbox[0] - s_bbox[2])),
                                #         # round(abs(ps["bbox"][0] - ps["bbox"][2])),
                                #         # ps.get("block_id"),
                                #         # block_id,
                                #         # ps.get("line_id"),
                                #         # line_id,
                                #         # "-->",
                                #         # len(s["text"] + " "),
                                #         # ps.get("text"),
                                #         # plausible_new_paragraph == False,
                                #         # s_size,
                                #         # no_space_between_spans,
                                #         # block_or_line_change,
                                #         end_of_header,
                                #         "-->",
                                #         s_size == ps.get("size", 0)
                                #         or no_space_between_spans,
                                #         bool((1 - plausible_new_paragraph)),
                                #         prev_page_id + 1 == page_id,
                                #         s_color == ps.get("color"),
                                #     )

                                # if font size and color is the same as previous span then we assume that they are connected in a paragraph
                                if (
                                    (
                                        s_size == ps.get("size", 0)
                                        or no_space_between_spans
                                        or not block_or_line_change
                                    )
                                    and (1 - plausible_new_paragraph)
                                    and len(block_dict.get("text", "")) > 0
                                    and prev_page_id + 1 == page_id
                                    and is_new_footnote == False
                                    and is_page_number == False
                                    and end_of_header == False
                                    # and s_color == ps.get("color")
                                ):
                                    # if (
                                    #     s_size == ps.get("size", 0)
                                    #     and len(block_dict.get("text", "")) > 0
                                    #     and prev_page_id + 1 == page_id
                                    #     and (
                                    #         1
                                    #         - font_type_changed
                                    #         * plausible_new_paragraph
                                    #         * granularity
                                    #     )
                                    #     and plausible_new_paragraph == False
                                    #     and is_new_footnote == False
                                    #     and s_color == ps.get("color")
                                    # ):

                                    block_dict["text"] = self._remove_rowbreak_dashes(
                                        ps,
                                        s_text,
                                        block_dict["text"],
                                        line_id,
                                        no_space_between_spans,
                                    )
                                    block_dict["bbox"] = self._max_bbox(
                                        s_bbox, block_dict["bbox"]
                                    )

                                    # if (
                                    #     page_id == 3
                                    #     and 0 < block_id < 10
                                    #     and "1" == s_text  # "Introdu" in s_text
                                    # ):
                                    #     print("--->>", s_text)
                                    #     print(block_dict["text"])

                                elif (
                                    block_dict.get("type") == "footnote_text"
                                    and is_new_footnote == False
                                    and is_page_number == False
                                ):
                                    block_dict["text"] = self._remove_rowbreak_dashes(
                                        ps,
                                        s_text,
                                        block_dict["text"],
                                        line_id,
                                        no_space_between_spans,
                                    )
                                    block_dict["merged_tags"] += "_" + s_tag

                                elif (
                                    s_text in ["th"]
                                    and ps.get("size", 0) > s_size
                                    and len(block_dict.get("text", "")) > 0
                                    and prev_page_id + 1 == page_id
                                ):
                                    block_dict["text"] += s_text
                                    s["size"] = ps[
                                        "size"
                                    ]  # set size to previous tag to avoid new paragraph
                                    block_dict["merged_tags"] += "_" + s_tag
                                else:
                                    if block_dict:
                                        # rlbi = block_dict["linebreak_indexes"][::-1]
                                        # block_dict["linebreak_indexes"] = [
                                        #     v
                                        #     for i, v in enumerate(rlbi)
                                        #     if not rlbi[max(i - 1, 0)]
                                        #     in no_space_between_spans_set
                                        # ][::-1]
                                        parsed_content.append(block_dict)
                                    block_dict = {}
                                    block_dict["text"] = s_text
                                    block_dict["tag"] = s_tag
                                    block_dict["size"] = s_size
                                    block_dict["color"] = s_color
                                    block_dict["page_id"] = page_id
                                    block_dict["merged_tags"] = s_tag
                                    block_dict["linebreak_indexes"] = []
                                    block_dict["block_id"] = block_id
                                    block_dict["line_id"] = line_id
                                    block_dict["bbox"] = s_bbox
                                    no_space_between_spans_set = set()

                                    if page_number and page_number["bbox"] == s_bbox:
                                        block_dict["type"] = "page_number"
                                    else:
                                        block_dict["type"] = "text"

                                    if (
                                        is_new_footnote
                                        and not s_footnote["is_page_bottom"]
                                    ):
                                        block_dict[
                                            "type"
                                        ] = "footnote_id"  # The footnote placement
                                        is_new_footnote = False
                                        last_footnote_id_pos = len(
                                            parsed_content[-1]["text"]
                                        )
                                        block_dict[
                                            "footnote_id_pos"
                                        ] = last_footnote_id_pos
                                    elif (
                                        is_new_footnote
                                        and s_footnote["is_page_bottom"]
                                        and s_footnote["text"] == s_text
                                    ):
                                        block_dict["type"] = "footnote_text_id"
                                    elif is_new_footnote:
                                        block_dict["type"] = "footnote_text"
                                        is_new_footnote = False
                                ps = s

                            prev_s = s
                            # if page_id == 4 and 0 < block_id < 10:
                            #     print(block_dict["text"])

                            # if text spans were found on line and added then append them to the block_dict
                            block_text_length = len(block_dict.get("text", ""))
                            last_linebreak_index = (
                                block_dict["linebreak_indexes"][-1]
                                if block_dict.get("linebreak_indexes", None)
                                else 0
                            )
                            if (
                                block_text_length > 0
                                and last_linebreak_index != block_text_length
                            ):
                                # remove dashes binding together to lines
                                block_dict["linebreak_indexes"].append(
                                    block_text_length
                                    if block_dict["text"][-1] != "-"
                                    else block_text_length - 1
                                )
                                if no_space_between_spans:
                                    no_space_between_spans_set.add(
                                        block_dict["linebreak_indexes"][-1]
                                    )
                                if (
                                    len(block_dict["linebreak_indexes"]) > 1
                                    and block_dict["linebreak_indexes"][-1]
                                    in no_space_between_spans_set
                                ):
                                    del block_dict["linebreak_indexes"][-2]

                        prev_line_id = line_id
                        prev_line_length = line_length
                # if page_id == 4 and block_id == 9:  # 0 < block_id < 10:
                #     print(block_id)
                #     print("no_space_between_spans", block_dict["text"])
                #     print("no_space_between_spans", block_dict["linebreak_indexes"])
                #     print("no_space_between_spans", no_space_between_spans_set)
                prev_block_id = block_id
            # Next page: check if text block has been generated an i.e. differs from previous stored block. If so append it and commence new block.
            if block_dict and block_dict != parsed_content[-1]:
                parsed_content.append(block_dict)
                block_dict = {}
            prev_page_id = page_id

        # Merge all paragrahs broken up by footnotes
        prev_bl, next_bl_add = None, dict()
        footnote_breaks_to_remove = []
        for idx, bl in reversed(list(enumerate(parsed_content))):
            if bl["type"] == "footnote_id" and prev_bl:
                next_bl_add = prev_bl
            elif (
                next_bl_add
                and bl["tag"] == next_bl_add["tag"]
                and bl["page_id"] == next_bl_add["page_id"]
            ):
                parsed_content[idx + 1]["footnote_id_pos"] = len(
                    parsed_content[idx]["text"]
                )
                footnote_breaks_to_remove.append(idx + 2)
                parsed_content[idx]["text"] += (
                    next_bl_add["text"]
                    if next_bl_add["text"][0] in ",.!?:;-"
                    else " " + next_bl_add["text"]
                )
                next_bl_add = None
            else:
                next_bl_add = None

            prev_bl = bl
            # Remove line breaks etc. from text
            bl["text"] = re.sub(_SPECIAL_CHAR_PATTERNS, " ", bl["text"])

        for idx in sorted(footnote_breaks_to_remove, reverse=True):
            del parsed_content[idx]

        self.parsed_content = parsed_content

        return parsed_content

    def parse_toc(self, block: dict):
        text = block["text"]
        prev_lidx, prev_no_match_text, prev_line_text = 0, "", None
        section_type = "Main"
        parent_section = None
        prev_table_row = dict()
        prev_page_number = 0
        last_ii_added = 0
        prev_page_number_type = None
        roman_numeral_headings = False
        if len(self.toc) > 0 and self.toc[-1].get("section_type") == "Annex":
            section_type = "Annex"

        linebreak_indexes = block["linebreak_indexes"]

        for ii, lidx in enumerate(linebreak_indexes):
            line_text = text[prev_lidx:lidx].strip()

            # A new section reference is assumed to be found if either line contains 3 or more dots in a sequence or
            # if line ends with a digit larger than the previous recorded page number
            # dot_matches = re.search(r"[\.]{3,}", line_text)
            dot_matches = re.search(r"[\.]{2,}[\s]*[0-9]+", line_text)
            if not dot_matches:
                dot_matches = re.search(
                    r"[\.]{2,}[\s]*" + _ROMAN_NUMERAL_PATTERN[1:], line_text.upper()
                )

            arabic_page_number_search = re.search(r"([0-9]+)$", line_text)
            roman_page_number_search = re.search(
                _ROMAN_NUMERAL_PATTERN[1:] + "$", line_text.upper()
            )
            if arabic_page_number_search:
                page_number = (
                    arabic_page_number_search.group().strip()
                    if arabic_page_number_search
                    else ""
                )
                pstart, pend = arabic_page_number_search.span()

                # if not (int(page_number) == prev_page_number and dot_matches):
                #     print(
                #         "dot_matches",
                #         page_number == str(prev_page_number),
                #         prev_no_match_text,
                #     )

                is_page_number = (
                    int(page_number) >= prev_page_number
                    if page_number
                    and (
                        prev_page_number_type == "arabic"
                        or prev_page_number_type is None
                    )
                    and (pstart == 0 or line_text[pstart - 1] == " ")
                    and pend == len(line_text)
                    # and (int(page_number) == prev_page_number and dot_matches) == False
                    # and not (
                    #     prev_was_page_number == True
                    #     and len(prev_no_match_text) == 0
                    #     and ii > 0
                    # )
                    and not (ii == last_ii_added + 1 and len(line_text) < 5)
                    else False
                )
                # if ii == last_ii_added + 1 and len(line_text) < 5:
                #     is_page_number = False
            elif roman_page_number_search:
                page_number = (
                    str(self.romanToInt(roman_page_number_search.group().strip()))
                    if roman_page_number_search
                    else ""
                )
                pstart, pend = roman_page_number_search.span()
                is_page_number = (
                    int(page_number) >= prev_page_number
                    if page_number
                    and (
                        prev_page_number_type == "roman"
                        or prev_page_number_type is None
                    )
                    and (pstart == 0 or line_text[pstart - 1] == " ")
                    and pend == len(line_text)
                    and not (ii == last_ii_added + 1 and len(line_text) < 5)
                    else False
                )
            else:
                page_number = ""
                is_page_number = False

            # print(
            #     line_text.upper(),
            #     "::",
            #     page_number,
            #     "; is_page_number",
            #     is_page_number,
            #     "; !dot_matches",
            #     dot_matches == None,
            #     prev_page_number_type,
            #     prev_page_number,
            #     arabic_page_number_search,
            #     ii,
            #     last_ii_added,
            # )

            if (
                dot_matches or is_page_number
            ):  # if match contains dotted line or ends with a page number then it is a row in the toc
                if dot_matches:
                    mstart, _ = dot_matches.span()
                    # page_number = dot_matches.group().strip(".").strip() if arabic_page_number_search else page
                else:
                    mstart, _ = (
                        arabic_page_number_search.span()
                        if arabic_page_number_search
                        else roman_page_number_search.span()
                    )
                page_number = str(page_number)

                if prev_no_match_text:
                    header = "{} {}".format(
                        prev_no_match_text.strip(), line_text[:mstart].strip()
                    )
                else:
                    header = line_text[:mstart].strip()

                if not page_number.isdigit():
                    page_number = str(self.romanToInt(page_number.upper()))

                if (
                    "Annex" in header
                    or "ANNEX" in header
                    or "Appendix" in header
                    or "APPENDIX" in header
                ):
                    section_type = "Annex"

                roman_numeral_header = re.search(_ROMAN_NUMERAL_PATTERN, header)
                arabic_numeral_header = re.search(_SECTION_DIGIT_PATTERN, header)

                # if roman_numeral_header or digit:
                if roman_numeral_header:
                    section = roman_numeral_header.group()
                    section_level = 1  # section_level keeps track of subsections (1: main section, 2: subsection, 3: subsubsection, etc...)
                    roman_numeral_headings = True

                elif arabic_numeral_header:
                    section = arabic_numeral_header.group()
                    section_dots = section.count(".")
                    section_level = section_dots + int(
                        roman_numeral_headings
                    )  # if parent heading was roman numeral section level is moved one step
                else:
                    section = None
                    if section_type == "Main":
                        section_level = 2
                    else:
                        section_level = None

                if not section_level is None:
                    prev_section_level = prev_table_row.get("section_level")
                    if not prev_section_level is None:
                        if (
                            section_level > prev_section_level
                        ):  # if section level has increased then previous row will be a parent section
                            parent_section = prev_table_row.get("section", None)
                        elif (
                            section_level > 1
                        ):  # elif section is a sub section then we traverse back until we find same level as current
                            for tc in reversed(self.toc):
                                if tc["section_level"] == section_level:
                                    parent_section = tc["parent_section"]
                                    break
                        elif section_level != prev_section_level:
                            parent_section = None
                else:
                    parent_section = None

                new_table_row = {
                    "text": " ".join(header.split()),
                    "page_number": page_number,
                    "section": section,
                    "section_level": section_level,
                    "section_type": section_type,
                    "parent_section": parent_section,
                }
                if header:
                    self.toc.append(new_table_row)

                prev_table_row = new_table_row

                prev_no_match_text = ""

                prev_page_number = int(page_number)
                prev_page_number_type = (
                    "arabic" if arabic_page_number_search else "roman"
                )
                last_ii_added = ii
            else:
                prev_no_match_text += " " + line_text

            prev_was_page_number = is_page_number
            prev_lidx = lidx
            prev_line_text = line_text

    def extract_table_of_contents(self) -> List[Dict]:
        """Extract a table of contents. 
        Method identifies all lines in the document that belong to the table of contents. 
        Actual parsing is done by the parse_toc() method.
        """
        parsed_content = self.parsed_content
        # Identify table of contents (toc)
        toc_last_page_id = 0
        toc_page_limit = 20
        toc_page_ids = []
        toc_font_sizes = set()
        toc_bl_ids = []

        for idx, bl in enumerate(parsed_content):
            # We assume toc is located within the first toc_page_limit pages.
            if bl["page_id"] > toc_page_limit:
                break

            # We assume toc contains dot sequences or that the page_id has already been identified as a table of content
            if bl["text"].count("...") > 2 or bl["page_id"] in toc_page_ids:
                if toc_last_page_id == 0 or (bl["page_id"] - toc_last_page_id) < 2:
                    if bl["page_id"] not in toc_page_ids:
                        toc_page_ids.append(bl["page_id"])
                        toc_last_page_id = bl["page_id"]

                    if bl["type"] == "text" and (
                        bl["text"].count("...") > 2
                        or re.search(_SECTION_DIGIT_PATTERN, bl["text"])
                        or toc_last_page_id == bl["page_id"]
                    ):
                        toc_font_sizes.add(bl["size"])
                        toc_bl_ids.append(idx)
        # print(parsed_content[toc_bl_ids[0]])
        # print(toc_page_ids, toc_bl_ids)
        # print(self.max_page_num_bbox)

        # We create a toc dict where we store all text and linebreak_indexes identified as a toc
        toc = {"text": "", "merged_tags": "", "size": None, "linebreak_indexes": []}
        for idx, bl in enumerate(parsed_content):
            # Once again we assume toc contains dot sequences and is located within the first toc_page_limit pages.
            if bl["page_id"] > toc_page_limit:
                break

            # if the page_id was previously identified as a table of content page
            if (
                bl["page_id"] in toc_page_ids
                and bl["type"] != "page_number"
                and (
                    self.max_page_num_bbox
                    is None  #  True if document has no printed page numbers
                    or bl["bbox"][3]
                    < self.max_page_num_bbox[3]
                    - bl[
                        "size"
                    ]  # bbox y1 value should differ by at least a font size from the max page number bounding box
                )
            ):
                # print(bl["bbox"])
                # print(bl["size"] in toc_font_sizes)
                # print(bl)

                # if block_id in toc ids or if it belongs to the common group of toc font sizes
                # and y0 of bbox is on upper half of page (avoids potential page number or footer mixups)
                if idx in toc_bl_ids or bl["size"] in toc_font_sizes:
                    # print("---")
                    # print(bl["text"])
                    # print(bl["linebreak_indexes"])
                    _correct_split_word = False
                    if toc["text"] != "":
                        # Join words split by pdf convert tool e.g. "Purpose" (see 2011:22)
                        if re.search(r"[\s][a-zA-Z]$", toc["text"]) and not re.search(
                            "[\.a-zA-Z][\.\s]" + _ROMAN_NUMERAL_PATTERN[1:] + "$",
                            toc["text"].upper(),
                        ):
                            toc["text"] += bl["text"]
                            toc["linebreak_indexes"] = toc["linebreak_indexes"][:-1]
                            # toc["linebreak_indexes"][-1] =
                            # toc["linebreak_indexes"][-1] = (
                            #     toc["linebreak_indexes"][-1] + 1
                            # )
                            _correct_split_word = True
                            # print(bl["text"])
                            # print(bl["linebreak_indexes"])
                        else:
                            toc["text"] += " " + bl["text"]
                    else:
                        toc["text"] = bl["text"]
                        # _replace_toc_text = ["Table of Contents", "Tabel of Contents"]
                        # for rtt in _replace_toc_text:
                        #     if rtt.lower() in toc["text"].lower() and len(
                        #         toc["text"].strip()
                        #     ) > len(rtt):
                        #         toc["text"] = toc["text"]

                    last_line_break_idx = (
                        (
                            toc["linebreak_indexes"][-1]
                            if toc["linebreak_indexes"]
                            else 0
                        )
                        + 1
                        # + int(_correct_split_word)
                    )
                    for lb in bl["linebreak_indexes"]:
                        toc["linebreak_indexes"].append(lb + last_line_break_idx)

                    if _correct_split_word:
                        toc["linebreak_indexes"][-1] = len(toc["text"])

                bl["type"] = "toc_orig_text"
        # print("----")
        # print(toc)
        # We remove specific control characters such as newline, return, tab and spaces (\xa0)
        toc["text"] = re.sub(_SPECIAL_CHAR_PATTERNS, " ", toc["text"])
        # print(toc)

        # Parse toc which gets stored in self.toc
        self.parse_toc(toc)

        if len(toc_page_ids) == 0:
            print("Warning no Table of Contents identified.")
        else:
            print("ToC length:", len(self.toc))

        return self.toc

    def extract_table_of_contents_v2(self) -> List[Dict]:
        """Extract a table of contents (version 2). 
        Method for parsing toc which don't contain dots
        """
        parsed_content = self.parsed_content
        # Identify table of contents (toc)
        toc_last_page_id = 0
        toc_page_limit = 20
        toc_page_ids = []
        toc_font_sizes = set()
        toc_bl_ids = []

        def itemgetter(idxs):
            idxs = [0] + idxs

            def g(text):
                return tuple(
                    text[idx : idxs[i + 1]] if i < len(idxs) - 1 else text[idx:None]
                    for i, idx in enumerate(idxs)
                    if text[idx:None]
                )

            return g

        toc_page_id = None
        toc_match = None
        toc = []
        prev_mtype, mtype, prev_m = None, None, None

        section_type = "Main"
        section_level = 0
        parent_section = None
        toc_row = {"text": "", "page_number": None, "section": None}
        for idx, bl in enumerate(parsed_content):
            # We assume toc is located within the first toc_page_limit pages.
            if bl["page_id"] > toc_page_limit:
                break

            if not toc_match:
                toc_match = re.match(
                    r"(table)[\s]+(of)[\s]+(contents)", bl["text"], re.IGNORECASE
                )
                if toc_match:
                    toc_page_id = bl["page_id"]

            if (
                toc_page_id == bl["page_id"]
                and bl["type"] != "page_number"
                and toc_match.group(0) != bl["text"]
            ):
                linebreak_indexes = bl["linebreak_indexes"]
                bl["type"] = "toc_orig_text"
                matches = itemgetter(linebreak_indexes)(bl["text"])

                # print(matches)
                for m in matches:
                    text = m.strip()
                    arabic_numeral_header = re.search(_SECTION_DIGIT_PATTERN, text)
                    roman_numeral_header = re.search(
                        _ROMAN_NUMERAL_PATTERN, text.upper()
                    )

                    arabic_page_number_search = (
                        re.search(r"^([0-9]+)$", text) if len(text) < 4 else None
                    )
                    roman_page_number_search = re.search(
                        _ROMAN_NUMERAL_PATTERN[1:] + "$", text.upper()
                    )
                    # print(text)
                    # print("head: ", arabic_numeral_header, roman_numeral_header)
                    # print("page: ", arabic_page_number_search, roman_page_number_search)

                    if (prev_mtype == "page_number" or prev_mtype == None) and (
                        arabic_numeral_header or roman_numeral_header
                    ):
                        mtype = "section"
                        section = (
                            roman_numeral_header.group(0)
                            if roman_numeral_header
                            else arabic_numeral_header.group(0)
                        )
                        toc_row["section"] = section.strip()
                    elif arabic_page_number_search or roman_page_number_search:
                        mtype = "page_number"
                        page_number = (
                            str(
                                self.romanToInt(
                                    roman_page_number_search.group(0).strip()
                                )
                            )
                            if roman_page_number_search
                            else arabic_page_number_search.group(0)
                        )

                        if roman_numeral_header and "-" in text:
                            page_number = str(
                                self.romanToInt(roman_numeral_header.group(0).strip())
                            )
                        toc_row["page_number"] = page_number.strip()
                        if prev_mtype == "section":

                            toc_row["text"] = prev_text

                    else:
                        mtype = "text"
                        toc_row["text"] = text

                    if mtype == "page_number":

                        if (
                            "Annex" in toc_row["text"]
                            or "ANNEX" in toc_row["text"]
                            or "Appendix" in toc_row["text"]
                            or "APPENDIX" in toc_row["text"]
                        ):
                            section_type = "Annex"
                        toc_row["section_type"] = section_type
                        toc_row["parent_section"] = None
                        if len(toc) > 0 and toc[-1]["section"] and section:
                            if len(toc[-1]["section"]) < len(section):
                                section_level += 1
                                toc_row["parent_section"] = parent_section
                            elif len(toc[-1]["section"]) > len(section):
                                section_level = 0
                                parent_section = toc_row["section"]
                            else:
                                toc_row["parent_section"] = parent_section

                        toc_row["section_level"] = section_level

                        toc.append(toc_row)
                        toc_row = {"text": "", "page_number": None, "section": None}
                    prev_mtype = mtype
                    prev_text = text

        if len(toc) == 0:
            print("Warning no Table of Contents identified.")
        else:
            print("ToC length:", len(toc))

        # print("ToC")
        # for t in toc:
        #     print(t)
        self.toc = toc

    def match_table_of_contents(self) -> List[Dict]:
        """ Match a header to the corresponding table of contents row. """
        toc = self.toc
        page_numbers = self.page_numbers
        parsed_content = self.parsed_content
        toc_length = len(toc)

        # Find best matching header without considering page_number info
        for toc_idx, toc_row in enumerate(toc):
            for content_idx, content in enumerate(parsed_content):
                if content["type"] == "text":  # "<h" in content["tag"]:
                    token_sort_ratio = fuzz.token_sort_ratio(
                        content["text"], toc_row["text"]
                    )
                    if "toc_match" in toc_row.keys():
                        if token_sort_ratio > toc_row["toc_match"]["token_sort_ratio"]:
                            toc_row["toc_match"] = {
                                "content_idx": content_idx,
                                "token_sort_ratio": token_sort_ratio,
                            }
                    else:
                        toc_row["toc_match"] = {
                            "content_idx": content_idx,
                            "token_sort_ratio": token_sort_ratio,
                        }

        # If previous match was poor find best matching header on corresponding page_number
        for toc_idx, toc_row in enumerate(toc):
            if toc_row["toc_match"]["token_sort_ratio"] < 80:
                for pp in page_numbers:
                    if pp["text"] == toc_row["page_number"]:
                        page_id = pp["page_id"]
                        prev_page_token_sort_ratio = 0
                        for content_idx, content in enumerate(parsed_content):
                            if (
                                page_id == content["page_id"]
                            ):  # and "<h" in content["tag"]:
                                page_token_sort_ratio = fuzz.token_sort_ratio(
                                    content["text"], toc_row["text"]
                                )
                                if page_token_sort_ratio > prev_page_token_sort_ratio:
                                    toc_row["toc_match"] = {
                                        "content_idx": content_idx,
                                        "token_sort_ratio": page_token_sort_ratio,
                                    }
                                    prev_page_token_sort_ratio = page_token_sort_ratio
                            elif content["page_id"] > page_id:
                                break
                        break
        self.toc = toc
        return toc

    def write_files(self, output_path):
        """ Write parsed content to a json file and a markdown file. """
        parsed_content = self.parsed_content
        filename = self.filename.split(".")[0]
        if output_path and not os.path.exists(output_path):
            os.mkdir(output_path)
        file_path = os.path.join(output_path, filename)
        with open("{}.md".format(file_path), "w") as f:
            for bl in parsed_content:
                if bl["type"] == "text":
                    text = bl["text"]
                elif bl["type"] == "page_number":
                    text = "<b>p. {}</b>".format(bl["text"])
                elif bl["type"] == "footnote_id":
                    text = "<i>{}</i>".format(bl["text"])
                elif bl["type"] == "footnote_text":
                    text = "<i>{}</i>".format(bl["text"])
                elif bl["type"] == "footnote_text_id":
                    text = "<i>{}</i>".format(bl["text"])
                else:
                    text = bl["text"]

                if bl["tag"][0:2] != "<s":
                    f.write(bl["tag"] + text + "</" + bl["tag"][1:])
                else:
                    f.write(
                        "<p style='font-size:{}px'>{}</p>".format(
                            round(bl["size"]), text
                        )
                    )
        with open("{}_content.json".format(file_path), "w") as f:
            for bl in parsed_content:
                f.write(json.dumps(bl, ensure_ascii=False))
                f.write("\n")

        with open("{}_meta.json".format(file_path), "w") as f:
            for row in self.toc:
                row["type"] = "toc"
                f.write(json.dumps(row, ensure_ascii=False))
                f.write("\n")

            # f.write(json.dumps({"table_of_contents": self.toc}))


def parse_pdf_directory(replace_files: str):
    """ Parse all pdf files in a directory """

    input_path, output_path = _FETCHED_FILES_PATH, _PARSED_FILES_PATH
    if not os.path.exists(input_path):
        os.mkdir(output_path)
        print("Created input_path: {}".format(input_path))
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        print("Created input_path: {}".format(output_path))
    if not os.path.exists(os.path.join(output_path, "summary")):
        os.mkdir(os.path.join(output_path, "summary"))
        print(
            "Created output_path summary folder: {}".format(
                os.path.join(output_path, "summary")
            )
        )

    files_already_parsed = [
        file.replace("_content.json", "")
        for file in os.listdir(output_path)
        if file.endswith("_content.json")
    ]
    summary_stats = {"accuracy_scores": []}
    print("Number of files: ", len(os.listdir(input_path)))
    results = {}
    table_of_contents_cnt = 0
    for idx, file in enumerate(sorted(os.listdir(input_path)), start=0):
        # if idx not in [57]:
        #     # if idx < 227:
        #     continue

        # process_files = [
        #     # "2013:38_15359",
        #     # "2014:22_15415",
        #     # "2014:52_15491",
        #     # "2014:53_15493",
        #     # "2014:67_15509",
        #     "2014:55_15494",
        # ]
        # if file.split(".pdf")[0] not in process_files:
        #     continue

        if replace_files == "n" and file.replace(".pdf", "") in files_already_parsed:
            print(f"Already parsed: {file}")
            continue

        if file.endswith(".pdf"):
            print(idx, file)
            granularity = True
            font_size_remainder = 1
            pdoc = ParseDoc(
                os.path.join(input_path, file),
                font_size_remainder=font_size_remainder,
                granularity=granularity,
            )
            font_counts, styles, page_numbers = pdoc.fonts_and_page_numbers()
            size_tags = pdoc.font_tags()
            footnotes = pdoc.get_footnotes()
            parsed_content = pdoc.parse_content()
            pdoc.extract_table_of_contents()
            if len(pdoc.toc) == 0:
                print("Try v2 extraction...")
                pdoc.extract_table_of_contents_v2()
            toc = pdoc.match_table_of_contents()
            token_sort_ratio_sum = 0

            for t in toc:
                show_keys = ["text", "page_number", "parent_section"]
                token_sort_ratio = t["toc_match"]["token_sort_ratio"]
                print(
                    token_sort_ratio,
                    " / ",
                    t["toc_match"]["content_idx"],
                    ": ",
                    {key: t[key] for key in show_keys},
                )
                token_sort_ratio_sum += token_sort_ratio

            accuracy_score = None
            if toc:
                accuracy_score = token_sort_ratio_sum / (100 * len(toc))
                summary_stats["accuracy_scores"].append(accuracy_score)

            results[file] = {
                "font_counts": len(font_counts),
                "styles": len(styles),
                "page_numbers": len(page_numbers),
                "size_tag": len(size_tags),
                "footnotes": len(footnotes),
                "parsed_content": len(parsed_content),
                "table_of_contents_length": len(toc) if toc else None,
                "accuracy_score": accuracy_score,
            }
            table_of_contents_cnt += min(len(toc), 1)

            print("font_counts:", int(len(font_counts)))
            print("styles:", int(len(styles)))
            print("page_numbers:", int(len(page_numbers)))
            print("size_tag:", int(len(size_tags)))
            print("footnotes:", int(len(footnotes)))
            print("parsed_content:", int(len(parsed_content)))

            print("")
            pdoc.write_files(output_path=output_path)
        # if idx > 2:
        #     break

    print(summary_stats)
    print(
        "Number of 100% accuracy ratio:",
        summary_stats["accuracy_scores"].count(1.0),
        "/",
        len(summary_stats["accuracy_scores"]),
    )
    print("table_of_contents_cnt:", table_of_contents_cnt)
    # Write results data
    with open(os.path.join(output_path, "summary/parsing_results.json"), "w") as f:
        f.write(json.dumps(results))


@click.command()
@click.option(
    "--replace_parsed_files",
    default="y",
    prompt="Replace already parsed files in path?",
    type=click.Choice(["y", "n"]),
)
def main(replace_parsed_files):
    """ Command line method for parsing all pdf files in a directory """
    # Run from project level
    # python -m parse_evaluations.parse_evaluation

    parse_pdf_directory(replace_parsed_files)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
