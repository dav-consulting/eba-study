## Funding and donors
This section focuses on questions that one way or another are tied to the funding of the evaluated projects and programmes. More specifically it focuses on content with bearing on funding and donor related issues that are discussed in the processed evaluations. The aim has been to design QSSs that can yield reliable estimations for the inserted questions below: 

    Q9 - Is Sida the sole financier?
    Q21 - Does the evaluation assess the importance of Sida's funding relating to the contributions sustainability/lack of sustainability?
    Q22 - Does the evaluation analyse whether the contribution is dependent on funds from international donors?

### Findings
#### Accuracy of desinged strategies

The expectations to design solid models for these questions were low at the outset of this study. However, the designed QSS´s have performed relatively well for all questions in this section. Compared to the LME dataset the accuracy levels ranges from 68 percent for the assessment of Sida's importance (question 21) and 78 percent for dependency of international donors (question 22). When the results are compared to the third-party validation data the accuracy is suggested to be lower for all the listed questions. And it is a bit surprising that the accuracy levels between the LME and the third-party validation datasets are even lower [^fd1]. 


| Question  | QSS Accuracy | Label counts | Random Adj. Accuracy  | Third party accuracy | LME vs. Third party |  Anticipated difficulty | Assessed difficulty |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Q9 | 72% | 2 | 64% | 55% | 40% |  High | High | 
| Q21 | 68% | 4 | 55% | 55% | 50% | Very high | Very high  | 
| Q22 | 78% | 2 | 59% | 59% | 80% | High |  High | 


#### Descriptive statistics from scaled-up analysis
All of the developed strategies were deemed to be reliable enough [^fd2] to be used and deployed on the full sample of collected evaluations (>300 evaluations). A large majority of the evaluated projects/programmes/organizations were found to have references to several donors' organizations and/or OECD donor countries. In more than 8 in 10 (80%) of the processed evaluations, the developed QSS for assessing if Sida was the sole donor (question nine), found one or more donors (besides Sida/Sweden) that were referenced in relation to the funding of the project/programme. In the remaining twenty percent of the cases, Sida and Sweden was the only entity mentioned in the same context. The absolute majority of the evaluated projects and programmes are thus believed to receive funding from multiple donors. 

The same strategy also collected data on the specific donor organization and donor country that was mentioned in the evaluations. Sweden was referenced to funding in relevant text paragraphs in 98 percent of the processed evaluations, which is not surprising given that Sida is undertaking the evaluations and thus likely to be a donor. The large percentage for this observation - Sida mentioned in the relevant context - gives support to the strategies ability to find and extract relevant text passages and is a validation of the overall performance level. Other commonly mentioned OECD donor countries[^fd3] are the USA (18 percent), Norway (8%), the UK (6%), France (5,5%), Belgium (5,5%), Netherlands (5%), Denmark (3,5%), Canada (3%) and Germany (3%). 

The second developed QSS in this section aimed to estimate whether or not Sida's funding was discussed in relation to its importance for the evaluated entities sustainability (question 21). This strategy found relevant content in close to one in four (25 %) of the processed evaluations as displayed in figure 6 below. This would suggest that a rough quarter of the evaluations in one way or another are discussing the importance of Sida's funds in the proximity to discussions relating to the sustainability of the entities that are being evaluated. The inserted chart depicts this result for the entire assessed period. 

**Figure 6. Estimation of Sida's importance for sustainability 2011-2020**
@import "../images/sida_imp_all.png"


The final strategy was designed with the purpose to give an estimate on the extent of how the concept of donor dependency is covered in the evaluations. As shown in figure 7, roughly 30 percent of the processed evaluations had one or several text passages with content that semantically matched with what the current QSS was designed to record - donor dependency. The chart below shows the relative shares for all processed evaluations.

**Figure 7. Estimation of discussion of donor dependency between 2011-2020**
@import "../images/donor_dep_all.png"


### Applied method/s 
Each QSS has required a unique mixed-methods approach. Initially, a model with pre-trained [word embeddings](#methods) using [word2vec](#methods) was utilised in the strategies for all three questions. The purpose with this inital step was to identify semantic similar words to the key words in the spelled out questions (i.e. what semantic similar words for *donor, funding, sustainability, importance* et.c. were used in the processed evaluations). This pre-processing was executed, for each question, on the entire corpus (i.e. all words in the >300 evaluations were scanned). The resulting output was a set of words that share contextual and semantic similarity to key words in each of the presented questions. 

The next step included a design of a flexible analytical structure for applying the various sets of semantically similar words that could be fitted to the requirements for each single question. This flexibility allowed each of the QSS´s to undertake targeted searches for text paragraphs with content of particular relevance for each question. The final step, which was the same for all the strategies, included a design of a rules-based approach that located text paragraphs with bearing on *funding*. All positive observations were extracted for additional analysis. 

At this stage of the analysis, the three strategies diverged, and applied unique rules dependent on the specific requirements for each question. However, all strategies followed the same logic with identical analytical steps - processed sentence by sentence and recorded all sentences were words in the selected text paragraphs held matching words with the semantic word sets tied to each question. For example, if a text paragraph with a reference to funding was found, the paragraph was then selected for additional analysis. If one or several sentences in the selected text paragraph held words with semantic similarity to Sida/Sweden as well as important and sustainability, it would register as a positive observation for question 21. 
### Caveats
Despite the fairly good results several limitations with the developed strategies exist. First, the strategies in this section were designed - in line with the selected questions from the LME dataset - to pick up on content and assess if a topic of interest is discussed or not. The current design of the strategies does not account for how or in what way it is discussed. This has implications for the sort of conclusions that can be drawn from this assessment (i.e. the conclusion can for instance be that the concept of *donor dependency* was discussed but not whether the project or programme per se was dependent on funds from external parties).

The developed validation lists, that the rules-based approaches have drawn upon relating to donors and semantic words of relevance for the questions at hand, are by no means believed to be exhaustive. It is, hence, likely that the performance of all the strategies in this section can be improved by adding more data on relevant entities as well as semantic words of relevance. The strategies are furthermore ill equipped to handle text paragraphs where past and present implementation periods and/or funding of other projects are mixed. Examples have been found where references in the processed evaluations were made to past implementation periods, where there for instance were more donors involved, which then could be mistaken for the evaluated period and thus yield fraudulent conclusions. 

A clear advantage that extends to all the designed strategies in this section are their wider scope and the possibility to process the full texts of the evaluations. Manual follow-up and scrutiny of diverting results showed that some results or observations in the LME dataset seem in some cases to have been extracted from a limited part of the processed evaluations, for instance the sustainability chapter. Hence, and due to the wider scope applied in the QSS, which stretched beyond obvious parts of the evaluations in search for specific content, accurate observations with relevant content were able to be identified and recorded.


[^fd1]: The accuracy levels between the validation dataset and the LME-dataset are in a few cases based on few observations (<5 evaluations). This is an effect of the LME-dataset’s variating coverage – not all questions have 128 observations – and since the validation dataset is based on a random sample of the full sample (128 evaluations) the number of comparative observations varies between questions. 
[^fd2]: The estimation of the reliability in the QSS prediction capability were determined by the displayed accuracy levels. In general and in most cases 70% was used as lower limit for when to include the designed QSS in the scaled-up analysis of >300 evaluations. 
[^fd3]: The displayed estimates also include observations of national donor organizations for each country. 