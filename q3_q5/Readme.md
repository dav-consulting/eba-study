# Extract geographical entities
## Methods
This section focus on geographical enquires and extracting geographic entities and categories from Sida's decentralised evaluation - question 3,4 and 5 from the LME-dataset.

### Method Q3 - Identification of countries
The developed method for this question is spelled out in the steps below:
*	The initial analytical process entail the parsing and tokenization of the raw documents or evaluations (as described under Readme files for nlp_procssing, and parse_evaluations).
*	Utilization of spaCy's English model for Named Entity Recognition (NER) (https://spacy.io/universe/project/video-spacys-ner-model) for parsing geographic entities. NER has been developed to extract information from text or to be more specific entities of various types such as locations, organisations, persons or date/time. NER as a concept has been around since the mid 90's and is still a popular research areas (Goyal, Gupta and Kurman 2018). The pre-trained model from spaCy, which is used in this study, is trained with a neural network on a large English corpus and has been evaluated with an accuracy on 86,4% (Honnibal 2017).
*	Normalisation process and streamlining of the geographic entities that were singled out it in the process above. It became clear that the data needed to be normalised - variation in country names and misspelling was relatively common. The ISO standard 3166 for country names where utilised to establish a nomenclature for country names. To this affect the third party python modules pycountry (https://pypi.org/project/pycountry/) and contry-converter (https://pypi.org/project/country-converter/) were utilized.
*	Mapping process and analysis of geopolitical entities (GPE) from the spaCy model are evaluated in three individual steps:
    1.	Exact matches - GPE entities are matched against pycountry/ISO standard 3166 country names. Exact matches are counted and stored.
    2.	Alternative country names and abbreviations - GPE entities are matched against functions in the module country-converter and regex lookups. Converted matches are counted stored.
    3.	Alternatives and misspellings - GPE entities are matched against pycountry function for fuzzy matches. Alternative spelling and typos of countries are picked up and the most similar country is singles out and stored. Fuzzy string matches uses the model Levenshtein distance [See Appa Rao et al 2018] to compare the difference between two sequences. This technique is a common practice in cases like this where two words or sentences are compared.

*	Sorting process and sorting of the matches from the mapping process above in various context-based categories:
    1.	Recipient countries - Countries that is not an OECD/DAC member (i.e. not a donor country) - the main target of this exercise.
    2.	Donor countries - Countries that is a OECD/DAC member (i.e. a donor country) as of 2020 (http://www.oecd.org/dac/financing-sustainable-development/development-finance-standards/DAC-List-of-ODA-Recipients-for-reporting-2020-flows.pdf).
    3.	Evaluation results - meta data for each match according to the 1-3 mapping steps above.
    4.	Non-matches - All entities that are not matched in any of the a-c evaluation steps above.

*	Appraisal process and evaluating identified countries. This step includes counting the occurrence of the identified countries and establishing threshold values to estimate the relevance of the country. A range of test have been conducted during the study period. The final threshold was set to more than 5 occurances. In short, if a country is mentioned 5 times of more it is considered as a relevant object for the assessment. The output of this method is a set of countries and the number of times each country was referenced in the evaluation. The result form this method is discussed below under results Q3.

### Method Q4 - Identification of region
The method for this section relies on the output from the assessment of Q3 - identification of countries. Given that the identified countries are accurate, their geographical location should defacto be able to generate a response for Q4 - evaluated project/programme's geographic region. Based on this logic a function has been drafted to map the identified countries against their respective UN region (see below for list for UN regions). The UN regions is a more detailed (i.e. number of regions) list of regions than the categories used in LME-dataset. See below for list for LME-dataset. As a consequence, and to be able to evaluate the developed methods performance, all UNregions have been mapped against the regions used in LME-dataset.

The actual assessment of region uses the output from Q3 and store the UNregion, in accordance with the list below, for all countries that is identified 10 times or more in Q3. The result from this is then processed in a mapping exercise in order to correspond to the regions used in LME-dataset. The result form this method is discussed below under results Q4.

* UN regions (part of the country converter module):
    •	Antarctica
    •	Australia and New Zealand
    •	Caribbean
    •	Central America
    •	Central Asia
    •	Eastern Africa
    •	Eastern Asia
    •	Eastern Europe
    •	Melanesia
    •	Micronesia
    •	Middle Africa
    •	Northern Africa
    •	Northern America
    •	Northern Europe
    •	Polynesia
    •	South America
    •	South-Eastern Asia
    •	Southern Africa
    •	Southern Asia
    •	Southern Europe
    •	Western Africa
    •	Western Asia
    •	Western Europe

* LME-dataset regions (used in EBA2017:12):
    •	AfrikaSoS
    •	Mena
    •	Syd- och latinamerika
    •	Öst- och centraleuropa
    •	Öst/syd och centralasien

### Method Q5 - Identification of geographical focus
The method for this question is based on a two-pronged approach. First, the evaluation titles are scrutinized for country names that matches with countries from the pycountry list. All countries, but Sweden, are part of the exercise. If the method identifies one specific country it yields the result "country/local" category of geographical focus. Secondly, if the initial step identifies more than one country or no country at all, the assessment takes an additional analytical step.

The output from Q3 (identification of countries throughout the full document) and from Q4 (estimation of region) are used to estimate the geographical focus. If only one country is mentioned more than 5 times throughout the document the geographical focus is labelled "Country/local". If more than one country is mentioned more than 5 times and that at least two countries that are mentioned more than 11 times have different regions (output from Q4) the geographical focus is labelled "Region". Finally, if more than 2 regions (output Q4) are identified the geographical focus is labelled "Global".


### Results

The strategy for Q3 have performed well against the data from LME-dataset. In 73% of the cases the machine approach was able to extract the exact right country/ies that are listed in the dataset from LME-dataset.. When comparing the most mentioned country from the machine approach there was positive matches in 97% of the evaluations. In total, these results surpassed the initial expectations of this exercise, even though the difficult level was set to Moderate and the confidence of success was estimated to confident.

In 79% of the cases the strategy for Q4 was able to extract the exact right country/ies from the dataset from LME-dataset. Based on the relative distribution of the data in the five categories in the LME-dataset. study a random selection whould be expected to make a correct prediction roughly 25% of the times. Hence, our strategy performs much better than a random guess. The results are in our opinion sufficiently good to replace a manual process. The confidence (Confident) and difficult level (Moderate) is deemed to be more or less in line with the initial expectations for this exercise.

In 86% of the cases the strategy for Q5 was able to extract the accurate geographical focus from the dataset from LME-dataset. Compared to the the relative distribution in the data and a random selection would be estimated to reach an accuracy for 53%. In this light the strategy is deemed succesful.  


## CAVEATS

The data from LME-dataset has been used to check the accuracy of the machine-based approach for the three questions in this section. A central caveat in this regard is variation and quality in the data. As a consequence the machine-based approach needed to include step for cleaning the data in terms of misspelling as well as translating Swedish to English. LME-dataset also hold a few arbitrary categories for country (e.g. "Många globala länder" and "18 globala länder") and the regions used in the LME-dataset seem to be very specific for Swedish development cooperation. All these factors resulted in the fact that a nomenclature and lookup functions needed to be developed.

Another important factor to consider is that the machine-based approach for Q4 and Q5 dependenp on the accuracy for Q3. Even though the accuracy is high (73%/97%) there are likely cases that do now follow the spelled out logic. Below follows some examples from the manual assessments of evaluations that has been classified differently than from LME-dataset results:

* ##### Challenge to grasp scope
    This challenge highlights that there are both strengths and weaknesses with the machine-based approach for responding to Q3. In some cases the approach is missing what is obvious for a human eye (i.e. that a country is in central and thus in focus). In other cases the machine-based approach can pick-up on things that are easily overlooked by a human eye (i.e. that titles does not necessarily entail the full scope). For example, the title "Outcome Assessment and Lessons Learnt from Swedish Development Cooperation with Macedonia (1999–2012)"/2012:3_15205 is quite clear that the focus of the evaluation lies on Macedonia. However, when assessing named entities or countries mentioned in the evaluation there is a range of countries that are well referenced (>10) throughout the document. As a consequence the machine approach labels this as a regional evaluation (as opposite to the national/local category from the LME-dataset). Another example is the evaluation of Sida’s support to Kvinna till Kvinna (KtK) and its programme: “Palestinian women seek greater power and influence to organise for democratic state building” 2011-2013/2013:40_15361 which has been labelled as a country/local evaluation. However, when assessing the identified countries it is obvious that Israel plays a key role in the evaluation, which would make a regional focus understandable. Note that this issue has been sorted with the additional analytical step to assesses the evaluation title and review if there is a single country mentioned, which then is used as a higher level indicator for focus on country/local level.

* ##### No or few geographical entities
    In the Evaluation (2014:25_15433) of the Sida Supported Programme of the International Association of Universities there is no country that is mentioned more then 5 times, which is the threshold set for a relevant country in the developed method. The consequence for this is that no country is selected for this evaluation. A solution for this would be to lower the threshold which would make the machine approach to pick up a many countries. A lower threshold would however generate none wanted effects for the other questions. This illuminate a limit with the machine approach that need to settle for a optimization solution rather than a solution that will work for all cases. On the other hand these limitations are made visible with this approach, which is not the case for a more manual approach that relies on face value - i.e. there is seldom a possibility for systematic follow-up.

* ##### Strategy scale and scope wider than operations
    Another challenging cases are development programmes that has a larger strategic reach than their operations. For instance that they aim to affect at a global level, but the operations are on a single or a few country level/s. This is the case in the Evaluation of “Leaders Engaged in New Democracies Network (LEND)/2014:38_1545. This evaluation has been labelled as global in scope for Q4 and Q5 while having a country focus in Q3 in the LME-dataset. While it is unclear which categories that are correct in this case it is another example on a challenging task for the machine-based approach.


---

## Usage

Command line: directory: `[project_root]`
```
$ python -m q3_q5.main
```