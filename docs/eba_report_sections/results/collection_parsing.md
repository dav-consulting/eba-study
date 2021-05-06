## Data collection and parsing of documents

This section outlines all processes involved in the collection, pre-processing and organization of the data in this study. All these steps are vital parts in all NLP studies. Finally, some descriptive statistics are showcased to illustrate how unstructured data can be synthesized and used to provide insights with regards to the current context. 

### Applied methods

A key component and necessary condition for this study to become successful was the design of the method that could extract relevant evaluations from the internet, and more importantly to parse content of key importance within these evaluations. The lion share of the data underlying the analysis in this study was embedded in pdf documents available via Sidas's publication database [^cp1]. Given that the scope of our study stretched between 2012-2020, during which several hundred evaluations had been produced and published, we decided to use an open source package for web scraping named [Scrapy](#open-source-packages). After having customized this package to the task at hand we were able to systematically extract all available evaluations during the mentioned period in a couple of minutes. This is a process which can easily be repeated and/or scheduled once new evaluations are published, should these processes need to be repeated and or the results updated. 

After the collection of the evaluations and storage of the documents the text within needed to be extracted and converted into a format that enabled deployment of the designed strategies (as described in the methods chapter above). For this task the open source package [PyMuPDF](#open-source-packages) was utilized, and all the collected evaluations were converted from pdf documents into [JSON](#dataformats) formatted documents. In this process each row of the evaluations was labelled with meta data holding auxiliary information about the text such as font size, text color and position on page etc. 

This auxiliary information was of particular importance since it allowed for rules-based algorithms to identify specific sections within each of the evaluations, which was a crucial component in answering some of the selected questions in this study. For instance, the font size of a specific paragraph was of importance for parsing out specific sections within the evaluations. These algorithms made use of handcrafted rules that were based on document attributes such as the fact that document headers in the evaluations usually had larger font-size than the body text. Similarly, the most common font-size in the evaluations allowed us to identify the body text of evaluations. Another aspect that was used in this approach was the position of text in the evaluations. In particular, page numbers and footnotes are typically located at the bottom of documents and numbered sequentially. Using knowledge of these types of characteristics of the texts allowed us to derive additional rules for how to identify text passages of relevance. In short, the success of this parsing algorithm allowed us to parse and extract specific sections from the evaluations, which was a prerequisite for responding to several of the selected questions in the LME-dataset.

### Findings
#### Accuracy of designed strategies

In total 318 of Sida's decentralized evaluations that covered the period 2012-2020 were downloaded in this study. After removal of some deviating[^cp2] cases, 311 documents remained and were included in the scaled-up analysis (mentioned in the methods chapter above). Out of these evaluations we could identify a table of contents in 309 of the evaluations (99%). Given that this was such a common feature we crafted a specific method for parsing the table of contents, which gave us an overview of the most frequent paragraphs in the downloaded evaluations, and then used the page numbers as index for how they could be systematically found.

Many of these paragraphs were particularly important in order be able to answer certain questions in the analytical framework that targeted specific evaluation paragraphs. This includes questions with bearing on the executive summary, recommendations, terms of reference as well as sections addressing specific OECD/DAC criteria. The table below presents summary statistics with regards to the frequencies with which these sections were found among the 309 documents that were parsed.


| Section | Count  | Percent  |
|:----------:|:-------------:|:-------------:|
| Table of contents | 309 | 99% |
| Executive summary | 302 | 97% |
| Recommendations | 283 | 91% |
| OECD/DAC - Sustainability | 283 | 91% |
| Terms of reference | 262 | 84% |
| OECD/DAC - Relevance | 209 | 67% |
| OECD/DAC - Effectiveness | 197 | 63% |
| OECD/DAC - Efficiency | 163 | 52% |
| OECD/DAC - Impacts | 123 | 40% |


The parsing process also allowed us to identify document specific characteristics such as title, authors, commissioning agency, publication date, series number, article number and publisher. This data was extracted with what we believe to be a hundred percent accuracy (no errors were found). However, these processes revealed some discrepancies between the data available on Sidas´s website and the data in the actual published evaluations. A plausible explanation to these discrepancies is believed to be tied to human error occurring at the time when the evaluations are being uploaded to Sida´s publication database and evaluation details are transcribed. 

#### Descriptive statistics from scaled-up analysis

Already at this stage, the parsed data allowed us to derive some descriptive statistics for the full set of evaluations between 2012-2020. The inserted chart below displays the number of conducted evaluations for each individual year during the relevant time period. There seems to have been a general declined in commissioned decentralized evaluations during recent years, when compared to a few relative busy years between 2013-2015. 

**Figure 1. Number of evaluations in Sida's database between 2012-2020**
@import "../images/eval_time.png"

An assessment of the commissioning agency for the evaluations show that two thirds (66%) were commissioned by Sida HQ, and close to 32% are commissioned by Swedish embassies, as displayed by the inserted graph below.

**Figure 2. Estimation of commissioning agency between 2012-2020**
@import "../images/com_ent_all.png"


Another example on statistics that can be directly produced at this stage, and which is particular important to consider since it is the language in the evaluations that are analyzed, is the number of involved evaluators or authors. This can give an estimate on the diversity of used language in the processed evaluations. Using the collected data to assess this angle revealed roughly 550 unique names among the list of authors in the 309 processed evaluations. This suggest that there is a large number of individuals involved in drafting the evaluations. A closer look showed that five percent of the authors are relatively reoccurring i.e. have been part of 6 evaluations or more. The most frequent evaluator who had taken part in no less than 53 evaluations which constitutes 17% of the complete set of evaluations in our study.



<!--
[Ideas for additional synthesis of extracted unstructured text from the evaluations.

Given a rough estimate on 700 000 SEK for the standard cost of a typical decentralised evaluation, the total annual costs for Sida's decentralised evaluations have varied between 13,5 MSEK and 43 MSEK over the course of the evaluated period. This can be valuable for planning purposes and give a rough idea for how to plan and keep a sound  budget for commissioning the decentralised evaluations.
]

, and thus are likely to bring individual language traits into the evaluations, which adds complexity and challenges for a machine-based language studies
-->



[^cp1]: https://www.sida.se/English/publications/publicationsearch/
[^cp2]: A few deviations have been observed among the downloaded evaluations. A few turned out to belong earlier years (2009 and 2010). We also found documents of the type "Sida Review" which had been wrongly labelled as a "Sida decentralized evaluation". There has also been examples where the evaluation per se has contained the wrong content - the front page and table of contents seemed to be accurate, but the actual document was a consultancy tender. 




