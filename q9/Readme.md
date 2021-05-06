# Extract donors and estimating joint financial support 

## Methods
This section focus on financial support enquires and extracting text passages with bearing on financial support and entities that are involved in funding of the evaluated projects and programmes - question 9 from LME-dataset.

The developed method for this question is spelled out in the steps below:
* The initial analytical process entails the parsing and tokenization of the raw documents or evaluations (as described under Readme files for nlp_procssing, and parse_evaluations).
* Multi-pronged mapping process of text passages with bearing on "funding" and "donor". 
    1. pre-processing of all words in the complete corpus (i.e. all evaluations) in order to single out words with semantic similarity to "funding" and "donor". This allows for compilation of a context specific list of matching words that reflects the used language and variations within in the evaluations. This pre-process utilises spaCy's pretrained similarity function that uses word embeddings or word vectors that has been generated with the algorithm word2vec (https://spacy.io/usage/vectors-similarity). This process rendered a range of words that has been manually scrutinized and the following list holds the lemmatized versions of the words that have been deemed to be of relevance for identifying sentences with bearing on funding of the evaluated projects/programmes. 
        * assistance
        * contribution
        * donation
        * donor
        * effort
        * finance
        * financier
        * financial
        * financial support
        * fund
        * funding
        * grant
    2. Utilization of spaCy's Matcher function (https://spacy.io/api/matcher ). This allows for parsing of relevant text passages. In short, if a sentence have a version of the above listed words the sentence will be singles out for additional assessment.  The matcher is designed to utilise and match based on the on the used words lemmatized words. Lemmatization of a word mostly relates use of a vocabulary and morphological analysis of words, mostly removing endings of word and give the essence of base of the word per se. A frequent used algorithm for this is Porter's algorithm (Manning et al 2008). 

    3. Utilization of spaCy's English NER model to single out countries (GPE) and donor organisations (ORG) that are mentioned as financers/donors, which includes Sweden/Sida, in the sentences, that has been singled out in step 2 – sentences with words of interest. 
* Evaluation of parsed entities from the steps above. In short, three response categories have been developed (in accordance with the LME-dataset). Appraisal process and evaluating estimation of whether or not Sida is sole financier. This step includes counting the occurrence of the identified donors and evaluating against the following logic:
    1. "Ja" - Yes, Sida/Sweden is sole donor. This applies when Sida and/or Sweden is the only identified donor. 
    2. "Nej" - No, Sida/Sweden is **not** the only donor. This category is selected when there are more known (based from list of donor organisations and/or OECD/DAC donor countries) that are mentioned in sentences singled out from the steps above. 
    3. "Oklart, framgår ej" - Unclear. This applies with the approach does not produce any results that comply with the steps above. 

## Results
The machine approach for Q9 have performed relatively well against the data from LME-dataset. The machine-based approach predicted the right outcome in 38 out of 58 available test cases. This translate to a accuracy level of 65%. However, 8 of the available test cases are labelled as 'Avser strategi/motsvarande', which, in contrast to LME-dataset, have been processed in this assessment. When these cases are excluded the accuracy level reaches 76%. In short, these results surpassed the initial expectations for this exercises slightly, which should be viewed in the lihgt of the set difficult level (High) and level of confidence to solve the questions (Fairly confident).

Using the model to extrapolate on the entire data set of collected evaluations (currently > 300 evaluations) gives some interesting insights. First, the LME-dataset sample showed that the relative distribution was as follows: Sida/Sweden sole donor 13%, More donors 69%, and unclear/strategies 19%. This pattern translate well to the developed methods result for the entire data set - Sida/Sweden sole donor 15%, More donors 83%, and unclear/strategies 2%.


## CAVEATS

* The used list of donor organisations is not guaranteed to be exhaustive by any means. It is likely that more data/donor organisations would improve the performance of the developed methods. 

* The machine-based approach is not tune for past financial support of a evaluated project /programme. For example in the excerpt below: "The MCC support was focused heavily on achieving targets for results, and far less on sustainable capacities within Mozambican public institutions to undertake land administration efforts in the long-term. Due partly to the lack of attention to capacity development, all interviewees described how the institutions that were developed through MCC collapsed when the programme was discontinued. This was partly due to the two-year (2013-14) gap in support to the land sector before GESTERRA could start when Sweden and the Netherlands stepped in and renewed support to Mozambique’s land sector. Whereas MCC’s more structured and co-ordinated approach relied". This is an example of where different periods are compared. Where US/MCC seem to have funded the programme before the current phase, which is supported by Sweden and Netherlands. Note - the information that the programme have received support earlier might, however, give a better understanding of the programme that just for the current period. 

* Another challenge in this case is evaluations that uses references to other projects/programmes that has been funded.

* The approach is not designed to handle evaluations that LME-dataset label as "Avser strategi/motsvarande". These are analysed in the same way as the other types and, hence generate estimations in line with the steps above.


---

## Usage

Command line: directory: `[project_root]`
```
$ python -m q9.main
```

