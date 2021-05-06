# Code repository for EBA study: Exploring the Potential of Data Science Methods for within the Field of International Development Cooperation

This repository contains methods and classes for processing the analytical framework in appendix 1 of eba_application_200413.pdf.

The following packages are contained within the project:

* docs:
    * contains background and info docs related to the code including background docs eba_application_200413.pdf (eba_application_200413) underlying this repository and eba_livslängd_och_livskraft_2017-12.pdf (EBA2017:12).
* eba2017:
    * eba_match.py: for matching SIDA evaluations analyzed in EBA 2017:12 to evaluations downloaded from SIDA's publication platform. Results are stored in columns: eba_match_title and eba_match_nr in processed_output.db.
    * eba_parse.py: class and methods for parsing the results recorded results of applying the analytical framework in EBA 2017:12 so that they can be compared to the present analysis.
    * orginal_data: contains the original data files underlying EBA 2017:12. 
* fetch_evaluations:
    * uses the python open source package Scrapy to download and process evaluations from `https://www.sida.se/English/publications/publicationsearch/`
* nlp_processing:
    * process_docs.py: contains method for creating Spacy docbin objects which are stored as bytes files under the subdirectory results
* parse_evaluations: uses the Python package 'PyMuPDF' to extract text from pdf file and then parses its contents. Results are stored in the subdirectory results as json files.
* q1_q2:
    * extract_titles_and_series_numbers.py: extracts titles and series numbers from pdf's downloaded at: `https://www.sida.se/English/publications/publicationsearch/`
* q3_q5:
    * main.py: extracts countries and estimates regions as well as geographical focus from the evlauations.
* q6:
    * main.py: extracts estimated for the period of time for the evaluations.
* q9:
    * main.py: extracts text passages with bearing on financial support and parse entities in order to estimate if Sida/Sweden is sole financier or not.
* q11:
    * main.py: classify evaluations according to predefined topics. 
    * zero_shot.py: classify evaluations according to zero shot algorithm,. 
* q14:
    * main.py: extract estimation for implementation phase of the contribution when the evaluation is being conducted.
* q17:
    * prepare_training_data.py: prepares training data.
    * training_category.py: train a model.
    * main.py: extracts text passages with bearing on sustainability and assess the overall sentiment. 
    * evaluate_training.py: evaluate trained model .
* q21:
    * main.py: extracts text passages with bearing on financial support, sustainability and importance and parse entities and estimate the importance of Sida/Sweden's support for the project/programmes' sustainability.
* q22:
    * main.py: extracts text passages that have bearing on donor dependency and estimates if the concept (donor dependency) is discussed in the evaluation.
* q23:
    * main.py: extracts text passages with bearing on sustainability in the executive summary.
* q24_25:
    * main.py: extracts the contribution's sustainability in the evaluation's recommendations.
* util.py: contains methods and constants that are used throughout the project.
* webapp.py: script for launching a streamlit webapp dislaying the results `streamlit run webapp.py`.

**Further, additional info for each of the bullets above can be found in the 'Readme' files located in the folder for each individual query/process.**

## Installation 

Required python packages are found in `requirements.txt`-

Also a Spacy model must be installed e.g. 
Spacy models must be installed e.g.:
```
python -m spacy download en_core_web_lg
```

## Usage

All processes should can be run from `[project_root]` at the command line with exception for fetch_evaluations with should run from within its folder. For example, to run parse_evaluation.py:
```
$ python -m parse_evaluations.parse_evaluation
```

Questions from the analytical framework outlined in appendix 1 of eba_application_200413 are organized in folders labeled qX or qX_qY e.g. q1_q2. NOTE, However, before running these processes the following code must have been completed successfully in the following order:

```
fetch_evaluations $ scrapy crawl fetch_eval
$ python -m parse_evaluations.parse_evaluation
$ python -m parse_evaluations.parse_toc
$ python -m nlp_processing.process_docs
$ python -m eba2017.eba_match
$ python -m eba2017.eba_parse
$ python -m q1_q2.main
$ python -m q3_q5.main
$ python -m q6.main
$ python -m q9.main
$ python -m q11.main
$ python -m q11.zero_shot
$ python -m q14.main
$ python -m q17.prepare_training_data
$ python -m q17.train_category
$ python -m q17.main
$ python -m q17.evaluate_training
$ python -m q21.main
$ python -m q22.main
$ python -m q23.main
$ python -m q24_25.main


```

The output of the analysis is contained in the file: 'processed_output.db'.

Some tests are done with the pytest module:
```
python -m pytest
```

.'