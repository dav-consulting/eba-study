#Estimating donor dependency

## Methods
This method is designed to estimate which evaluations that assesses donor dependency - question 22 from LME-dataset. Note that there are several versions of this question in the LME-dataset: A) "Nämner utvärderingen explicit/uttryckligt att insatsen är beroende av finansiering från utländska givare? (2014)", and B) "Diskuterar utvärderingen insatsen utifrån begreppet biståndsberoende?". The given responses in the LME-dataset are "Ja" and "Nej". The LME-dataset also include "Nej, men man skriver explicit att insatsen är beroende av bistånd", which has been translated to "Ja" when assessing the accuracy of the designed method - see details below. This method has furthermore taken bearing on question B. In short, estimate if the evaluators assesses donor dependency in their evaluations.

* The developed method for this question is spelled out in the steps below:
    
    * The initial analytical process entails the parsing and tokenisation of the raw documents or evaluations (as described under Readme files for nlp_procssing, and parse_evaluations).

    * Pre-processing of all words in the complete corpus (i.e. all evaluations) in order to single out words with contextual similarity to all three areas - "donor dependency", "dependency", "donor". This allows for compilation of a context specific list of matching words that reflects the used language and variations within in the evaluations. This pre-process utilises spaCy's pre-trained similarity function that uses word embeddings or word vectors that has been generated with the algorithm word2vec (https://spacy.io/usage/vectors-similarity). This process rendered a range of words that has been manually scrutinised and the following lists hold the lemmatised versions of the words that have been deemed to be of relevance for identifying sentences with bearing on funding of the evaluated projects/programmes.

    * Multi-pronged mapping process of text passages and sentences with bearing on word vectors similar to "donor dependency", "dependency", "donor". 
    
    This step relies on the utilisation and application of the spaCy's Matcher function (https://spacy.io/api/matcher ) from the step above. This allows for parsing of relevant text passages and sequential analysis for contextual content. First the "donor dependency" matcher is applied in an independent step over all but the terms of reference paragraphs. Second the "dependency" matcher and subsequently the "donor" matcher is also applied in an individual analytical step assessing all but the paragraphs under “terms of reference”. In short, if a sentence hold a word associated with the three listed areas, the sentence will be singled out for additional assessment. The matchers are designed to utilise and match based on lemmatized words. Lemmatization of a word mostly relates to use of a vocabulary and morphological analysis of words, mostly removing endings of word and give the essence or base of a specific word. A frequent used algorithm for this is Porter's algorithm (Manning et al 2008).

    * Utilisation of spaCy's English model for Named Entity Recognition (NER) (https://spacy.io/universe/project/video-spacys-ner-model) for parsing geographic  and organisational entities. NER has been developed to extract information from text or to be more specific entities of various types such as locations, organisations, persons or date/time. NER as a concept has been around since the mid 90's and is still a popular research areas (Goyal, Gupta and Kurman 2018). The pre-trained model from spaCy, which is used in this study, is trained with a neural network on a large English corpus and has been evaluated with an accuracy on 86,4% (Honnibal 2017). This step also hold a mapping process where parsed organisational and geopolitical entities are checked against OECD/DAC donor countries and a list of key donor organisations. 
    
    * Appraisal process of parsed data from the steps above and estimation of whether or not the evaluation discuss the contribution from an aid dependency perspective. The estimations rest on a simple logic in line with the two main response categories from LME-dataset:
        1. "Ja" - Yes, if there is text that has bearing on the three steps spelled out above - donor dependency and/or dependency and donor.
        2. "Nej" - No, no text passages with the described characteristics have been found. 


## Results
Based on the LME-dataset the machine-based approach reach an accuracy of 78%. This result met the initial expectations for this exercises, which should be viewed in the light of the set difficult level (High) and level of confidence to solve the questions (Fairly confident). Note that the category "Nej, men man skriver explicit att insatsen är beroende av bistånd" from LME-dataset have been converted to "Ja" of logic reason - that they are discussing donor dependency. 

Using the model to extrapolate on the entire data set of collected evaluations (currently > 300 evaluations) gives some interesting insights. First, the LME-dataset sample showed that the relative distribution was as follows: 29% that discussed donor dependency, and 71% that did not. This pattern correlate well with the machine-based approach for the full data set - "Ja" (94 or 29,5%) and "Nej" (244 or 70,5%).


## Caveats

   * A difficulty for the machine or rules-based approach is handling with negation in a sentence that is "positive". For instance in 2014:59 where the following sentence can be found: "Therefore, they are dependent on receiving cash or individual wires which, mainstream donors have difficulty providing". In short, there is a reference for dependency for funds and donors in the same sentence, but the reference to donors is in fact misleading in this case. This evaluation was labelled correctly as "Nej" in LME-dataset, and falsely with "Ja" by the machine-based approach.  
   * Another example where the machine approach has an advantage is the scrutiny of the bulk with full robust consistency. The evaluation 2014:39 is labelled as "Nej" by LME-dataset, and seem for example to have overlooked the following sentence "It is not healthy that the research agenda is almost entirely dependent on donor funding at one university", which suggest that the correct estimate is "Ja" that was concluded by the machine-based approach given that the question is to assess if donor dependency have been discussed.  
   * Another challenge is indirect language. For instance the evaluation 2014:15 that has been labelled as "Ja" by LME-dataset and "Nej" by the machine-based approach. A manual assessment of the evaluation reveals there is no mention of "donor dependency" per se. However there are references to "dependent on funding" and "dependent on core support". This can be deemed correct in a wider sense, but it is difficult to determine the right answer in this case since it depends on what the underlying question is (i.e. donor dependency in this case). Note that the machine approach could easily be amended to include "funding" and would thus conclude "Ja" as well in this case.  
   * The used matcher lists and list of donor organisations are not guaranteed to be exhaustive by any means. It is more than likely that more data and more carful selection of key words would improve the performance of the machine approach.



## Usage

Command line: directory: `[project_root]`
```
$ python -m q22.main
```

