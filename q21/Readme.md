# Estimating importance of Sida support

## Methods
This section focus on paragraphs with bearing on the importance of Sida's financial support in relation to the evaluated projects/programmes sustainability - question 21 from LME-dataset: Does the evaluation assess the importance of Sida's funding relating to the contributions sustainability/lack of sustainability?

* The developed method for this question is spelled out in the steps below:
    
    * The initial analytical process entails the parsing and tokenisation of the raw documents or evaluations (as described under Readme files for nlp_procssing, and parse_evaluations).

    * Pre-processing of all words in the complete corpus (i.e. all evaluations) in order to single out words with contextual similarity to all three areas - "funding", "sustainability", "importance". This allows for compilation of a context specific list of matching words that reflects the used language and variations within in the evaluations. This pre-process utilises spaCy's pretrained similarity function that uses word embeddings or word vectors that has been generated with the algorithm word2vec (https://spacy.io/usage/vectors-similarity). This process rendered a range of words that has been manually scrutinised and the following lists hold the lemmatized versions of the words that have been deemed to be of relevance for identifying sentences with bearing on funding of the evaluated projects/programmes.

        # Funding
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

        # Sustainability
        * financial sustainability
        * sustainability
        * sustainable
        * sustain
        * self-sustain
        * self-sustainability
        * donor-dependency
        * self-financing

        # Importance
        * critical
        * crucial
        * essential
        * important
        * importance
        * particular
        * significant
        * vital
        * need for

    * Multi-pronged mapping process of text passages with bearing on word vectors similar to "funding", "sustainability", "importance" as well as Sida support. This step relies on the utilisation and application of the spaCy's Matcher function (https://spacy.io/api/matcher ) from the step above. This allows for parsing of relevant text passages and sequential analysis for contextual content. First the "funding" matcher is applied; second the "sustainability" matcher, thirdly the "importance" matcher. Each of these steps are cumulative and uses the results from the earlier step in a three-pronged process. In short, if a sentence have a version of the above listed words the sentence will be singled out for additional assessment. Finally, a query was conducted to assess if Sida and or Sweden was referenced in order to tied the result to Sida's funding. The matcher is designed to utilise and match based on the on the used words lemmatized words. Lemmatization of a word mostly relates use of a vocabulary and morphological analysis of words, mostly removing endings of word and give the essence of base of the word per se. A frequent used algorithm for this is Porter's algorithm (Manning et al 2008).

    * Appraisal process of parsed data from the steps above and estimation of whether or not the Sida's support is discussed and related to the project/programme's sustainability. The estimations rest on a simple logic in line with the two main response categories from LME-dataset. Note that the category "Analyseras ej då hållbar alt att hållbarhet ej har analyserats" from LME-dataset have been converted to "Nej" of logic reason - discussed below under results. 
        1. "Ja" - Yes, if there is text that has bearing on the four steps spelled out above - funding, sustainability, importance, Sida/Sweden. 
        2. "Nej" - No, no text passages with the described characteristics have been found. 


## Results
Based on the LME-dataset test sample the machine approach reach an accuracy of 76%. It should be noted that 17 cases in the LME-dataset are registered as "Analyseras ej då hållbar alt att hållbarhet ej har analyserats". By sheer logic that would entail that there are no mention of relevant text passages with bearing on Sida's importance for sustainability in the evaluations. Given that LME-dataset is correct the most logic label for these cases would therefore be "Nej" - that the evaluation do not mention any of this. When processing these 17 cases with the machine approach does not find any relevant text passages in 94% of the cases. This suggest that the machine approach accuracy is relative robust.  

These results surpassed the initial expectations for this exercises, which should be viewed in the light of the set difficult level (Very high) and level of confidence to solve the questions (Unconfident).

Using the model to extrapolate on the entire data set of collected evaluations (currently > 300 evaluations) gives some interesting insights. First, the LME-dataset sample showed that the relative distribution was as follows: "JA", importance of Sida support assessed 25%%, "Nej" 75%. This pattern correlate well with the machine approach for the full data set - "Ja" (77 or 24%) and "Nej" (241 or 76%).

Looking at geographical areas there are some variations. At the country level the evaluations assesses the importance of Sida's support in 26% of the cases; the Global level it higher with a share of 32%; and at the Regional level of 12% of the cases brings up Sida's importance in this case. 


## CAVEATS

* The machine-based approach is designed to pick up on content and assess if the topic of interest is discussed. The current design does not account for how or in what way it is discussed. 

* The iteration order in the spelled out approach do effect the results, and further elaborations with this is likely to bring positive effects on the results. 

* The used lists of matcher words ("funding", "sustainability" and "importance") is not exhaustive by any means. It is likely that more data/relevant words would improve the performance of the approach. 

* Assessment of diverting results between LME-dataset and the machine approach: 

    * Strict focus on sustainability chapter. A human eye and approach is likely to assess the sustainability chapter for this task. LME-dataset ladled 2014:9 as "Nej" and there is no text that seem to support Sida's importance for the sustainability of the programme in the sustainability chapter. However, looking more closely the following sentence can be found under the effectiveness and efficiency chapter: "The overall picture is that the market for the concerned commodities has changed towards greater sustainability, to a certain extent, during the period of Sida core support and that WWF, through the MTI, has made important contributions to these achievements.". This gives indication that the Sida role do in fact affect the sustainability in this case.  

    * Machine approach challenges with indirect references. When the financial contribution is discussed in relation to sustainability without making references to Sida and/or Sweden poses a challenge for the machine approach. For instance in 2014:17 - "Most Partner Organisations were aware that international funding was not going to last forever but few had contingencies in place. Anxiety about funding and international agencies pulling out was expressed. For one Partner Organisation, Kvinna till Kvinna provided 90% of their funds and for others it varies between 14% and 40%. Three Partner Organisations felt it would be devastating if funding from Kvinna till Kvinna stopped and four said it would reduce their ability to function but they would be able to carry on. With regard to national funding streams 4 said there is no funding available at national level and 2 Partner Organisations believe only if your organisation is politically affiliated will you get funded. [...] Conversely there was a sense that if funding were to stop, apart from the most vulnerable, it would stimulate skills in seeking funds elsewhere.", In this case Kvinna till Kvinna might be viewed as proxy for Sida and that would make the label "Ja" as understandable (form LME-dataset). However, there is no direct reference of Sida in this context, which can be used to argue that the right label is "Nej", which the machine label produced. 

    * Inconsistent perspective over time. Some cases are difficult to value for the human eye and it is easy to miss details when assessing lots of data. The evaluation 2014:19 has been labelled as "Nej" in LME-dataset. However, the machine approach was able to capture the following: "As Sweden took the decision to terminate its bilateral cooperation in Burkina, there will not be any opportunity for NDI’s programme to be financially supported by Swedish funds in the near future. The fact that this evaluation shall be seen as a final evaluation (from Sweden’s point of view) reinforces the importance of the sustainability criterion. From a TBE perspective, the focus will be on explicitly identifying which results are likely to remain, and which are not likely to remain, after Swedish funding and support ceases. It will also be important to assess the extent to which the Plan for Phasing Out Sweden’s Development Cooperation with Burkina Faso 2013-2016 has contributed to strengthening the results. This analysis also will be helpful to NDI’s understanding on which results the Institute can continue to build upon, and which ones might need additional support to become sustainable.". The label for this should be "Nej". 

---
## Usage

Command line: directory: `[project_root]`
```
$ python -m q21.main
```
