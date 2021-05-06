# Package for parsing SIDA evaluations PDF's

Uses Python package 'PyMuPDF' to extract text from pdf file. The extracted text contains info on e.g. font size, text color and position on page for all content identified as text string. Based on this info the ParseDoc class contains methods for parsing the content for auxillary meta data. This includes identifying whether an extracted text string belongs to a footnote, page number, table of content, header or main text (paragraphs). The class also contains methods for structuring the table of contents and linking each reference to its header so that it can be verified to which header each paragraph in the text belongs. 

PDF's can be downloaded from https://www.sida.se/English/publications/publicationsearch/ using scraping process found in `[project_root] / fetch_evaluations`.

See docstrings in ParseDoc class of parse_evaluation.py for details.

## Caveats:

Parsing of content is based mainly on fixed rules for how specific meta is formatted. For example, page numbers are assumed to be a series
of at least 5 numerals (arabic or roman) increasing by 1 for each new page. Hence, if for some reason the extracted text deviates from these
rules the content is con properly parsed. Two examples where this occurs is: 
* 2013:47 - Python package 'PyMuPDF', unable to determine appropriate font characteristics which causes a very poor parsing.
* 2012:62 - Does not have a Table of contents.
* 2014:52 - Poorly formatted Table of contents.

Potential errors of this kind can be identified post parsing based on summary statisitics that are extracted and placed at the end of the structured 
output json file.

## Output

The parsing results for each pdf document are stored in 3 files found in `[project_root] / parse_evaluations / results`:
* Visual content: a markdown file which shows a visible structure of the parsed results in a human readable format. Here, headers, footnotes and page numbers have been formatted accordingly.
* Parsed content: a json lines file with the ending `_content.json`  which contains the parsed content and meta data for each of the parsed content.
* Table of Contents: a json lines file with the ending `_meta.json` which contains the parsed Table of Contents for the pdf file.  

### Parsed content

The parsed content has a number of meta attributes:

* text: this is the text string of the content
* type: this indicates whether a the string is of some particular type such as page number. Possible types are:
  * text: some text
  * toc: table of content
  * toc_orig_text: table of content as originally parsed
  * footnote_text: footnote text
  * footnote_id: footnote id
* tag: a tag is given to all parsed text. The tags can be interpreted as follows:
  * <h: Large font/sizes found in the document.
  * <p: The most common font/size found in the document.
  * <s: Small font/size found in the document.
* size: font size of content
* color: font color of content
* page_id: the page id of where the content was found. Page id's start at 0 (fist page) and are incremented by 1 for each page in the pdf. (note: page_id and page numbers usually differ)

### Table of Contents

The Table of Contents for the doc has the following meta attributes:

* text: this is the text string of the content
* page_number: the page_number where the contents are to be found.
* section: the number given to the section heading
* section_level: the level a section is on (0: highest level).
* section_type: type can be Main or Annex.
* parent_section: the parent of the section (only for Main types)
* toc_match: dictionary containing matching info:
  * content_idx: the row number in the `Parsed content file` which was matched to the table of content text (content_idx starts at 0).
  * token_sort_ratio: the matching score given by fuzzy wuzzy
* category: whether the content belongs to a specific category e.g. executive_summary, terms_of_reference or a dac_criteria

### Summary json files

The summary folder contains summary stats for the content files, meta and table of contents.

## Usage

* Parsing all pdf files in a directory.
Command line: directory: `[project_root]`
python -m parse_evaluations.parse_evaluation

* Alternative: parsing individual pdf file.
In the python terminal:
>> from parse_evaluation import ParseDoc
>> pdoc = ParseDoc(path_to_pdf_file)

