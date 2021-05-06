## Geography and time
This section presents the results for selected questions with bearing on geographical- and time related issues. More specifically, we cover countries and geographical areas, time periods that are being evaluated and at what phase of the contribution the evaluation took place. The specific questions that are addressed in this section reads as follows:

    Q3. Country (include all countries that has been studied in the evaluation)?
    Q4. Geographical region?
    Q5. Geographical focus area (Country/local; Region; Global)?
    Q6. Time period that is being evaluated?
    Q14. At what phase of the contribution is the evaluation being conducted?

### Findings
#### Accuracy of designed strategies
At the outset of the study, estimates for the difficulty- and confidence-level for finding successful strategies for each question were estimated. Compared against these estimations, all of the QSS in this section have performed relatively well. The most noteworthy strategy, in this light, are the ones dealing with geographical focus areas (question five), estimations of the time period (question six) and the type of evaluation (question fourteen). All these questions were believed to be difficult to find proper solutions for and the initial expectations have been surpassed with the results from the developed QSSs. The table below depicts performance estimates for all questions in line with the benchmarks described in [section 2.3](#evaluating-performance). As spelled out in the table below the accuracy level ranges from 63 percent to 86 percent.

When the results from the developed strategies are compared with the third party validation data the correlation is lower. This is also the case when comparing the LME labels against the third party validation, which makes it difficult to set an upper boundary for each QSS[^gt1]. In fact, the QSS tend to correlate higher with the LME, than the third party validation data does which implies that the manual assessments are thus less consistent than that of the machine-based approach and the LME-dataset. 

A likely explanation for the somewhat scattered correlations between the different comparisons can to some extent be explained by the rigour for how we determine the accuracy. The results from the QSS needs to match exactly with that of the benchmark dataset in order to register as equivalent. This can lead to reduced accuracy measures when the results in fact is comprised of multiple observations, which for example was the case with question three where the answer consisted of a list of countries. For comparison, if we were to settle with comparing the most frequently extracted country name in each evaluation, the accuracy level between the developed QSS for question 3 and the LME-dataset would increase to 97 percent. This suggests that there is higher correlation if parts of the predicted data are used for comparison rather than using all observations or countries. And in this case, it might be more valuable to use the most observed countries since most evaluations usually focus on one or a few countries. However, we have settled to apply a strict metric where only exact matches will register as a success in this study. 

| Question | QSS Accuracy | Label counts | Random Adj. Accuracy  | Third party Accuracy | LME vs. Third party | Anticipated difficulty | Assessed difficulty |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Q3 | 73% | - | - | 54% | 86% |  Moderate | Moderate  | 
| Q4 | 79% | 6 | 25% | 55% | 67% |Moderate | Low | 
| Q5 | 86% | 3 | 51% | 79% | 80% |High | Low | 
| Q6 | 63% | - | - | 57% | 100% |High | High | 
| Q14 | 76% | 4 | 52%| 72% | 60% |High | Moderate | 
 

#### Descriptive statistics from scaled-up analysis
All of the QSS in this section have been deemed accurate enough to be used in a scale-up exercise where each designed strategy was used on the full data set of >300 evaluations. The applied strategies are believed to give a fair overview for the assessed period (2012 - 2020) and have given some insights into the questions at hand. However, it is important to note that the numbers and figures below should be viewed in the light of the displayed accuracy levels for each specific strategy. 

A total of 115 countries were recorded in the full data set. The top 10 ODA recipient countries - mentioned most frequently - are as follows: Kenya (68 evaluations or 21,3%), Tanzania (60 or 18,8%), Uganda (54 or 16,9%), South Africa (37 or 11,6%), Turkey (34 or 10,7%), Serbia (31 or 9,7%), Bosnia and Herzegovina (31 or 9,7%), Rwanda (30 or 9,4%), Ethiopia (29 or 9,1%), Zambia (28 or 8,8%), and Georgia (28 or 8,8%). It is noteworthy that East African countries stand out and are highly overrepresented in the full dataset.

The results for geographical region (based on UN regions) gave the estimates that the top 10 regions that have been evaluated during the last 10 years are as follows: Eastern Africa (137 or 43,3%), Western Asia (60 or 18,9%), Southern Europe (50, 15,8% ), Southern Asia (34 or 10,7%), South-Eastern Asia (32 or 10,1%), Western Africa (29 or 9,1%), Southern Africa (26 or 8,2%), Eastern Europe (21 or 6,6%), Northern Africa (20 or 6,3) and South America (18, 5,7%). For the final geographical question and the geographical focus area the results for the full sample estimated that most evaluations focused on the country/local level (192 or 60,1%). The regional level (76 or 24%) was the second most common level, and the global (37, 11,7%) level was trailing. The chart below displays the number of evaluations each year grouped on the estimated regional focus area (question five). The relative shares between the three various regional categories are relatively stable over the course of the assessed period. 

**Figure 3. Estimation of evaluations by geographical focus area between 2011-2020**
@import "../images/geo_time.png"

The time related questions also gave some interesting estimations. The average time period for the evaluated projects/programmes is 4,1 years with a distribution ranging from less than a year and up to 24 years. The most common evaluation type, for the entire period, is the end-of-phase evaluations with 72,3% (230) and the remaining share of 27,6% (88) is comprised of mid-term evaluations. The chart below shows the distribution between estimations between the type of evaluations over the whole assessed period. Years that deviate with considerable fewer mid-term reviews are 2016 (12%) and 2020 (7%). 

**Figure 4. Estimation of evaluations group by type between 2011-2020**
@import "../images/eval_type_time.png"



### Applied method/s 
A mixed-methods approach was used to develop the QSS in this section. At an initial stage all the QSS relied on the text parsing mechanism described above. Identified text passages with content that had bearing on geographical- and time related aspects were extracted and singled out for additional analysis. 

All of the strategies for handling the geographical queries share a basic analytical structure, where relevant parsed text excerpts from the evaluations were processed in a three-pronged approach. First, the pre-trained [spaCy](#open-source-packages) model for Named-Entity Recognition [NER](#methods) was utilized to extract geographical entities throughout each processed evaluation.

Second, the identified entities were normalized and cross-checked against manually established validation lists. A central example is the normalization process for country names - variation in country names and misspellings were common in the underlying dataset and needed to be sorted before any further analysis could be conducted. The ISO standard 3166 for country names were used for this, and a nomenclature for country names were established with the open source package [pycountries](#open-source-packages). During this process identified countries were also matched against a second validation list of countries that receives [ODA](#other) support from OECD countries. All positive matches to these queries were counted and recorded as positive observations for question three.  

Third, for the two questions relating to geographical region (question four) and geographical focus area (question five), yet another matching exercise was conducted where recorded countries were matched against UN regions using the open source package [country-converter](#open-source-packages). The geographical focus area (question five) required an additional step that accounted for the number of recorded countries and their geographical spread to estimate the geographical focus area. The estimation of accuracy for all three of these strategies were determined by mapping exercises where the strategies output (for each processed evaluation) was compared against the corresponding data in the LME-dataset.
 
Regarding the questions with bearing on time related issues, two separate rules-based QSS were developed. Both strategies were designed based on a thorough review of samples of evaluations and how the time period and the type of evaluation (i.e. if it was mid-term or an end-of phase evaluation) commonly are expressed. Both these QSS were limited to process text excerpts of the evaluation's terms of reference, executive summary, and introduction. 

The QSS for the evaluation time period (question six) used a pre-determined text matcher that recorded all observations that followed patterns where two years (or more) were observed in close proximity to each other. The most common combination found in the document was deemed to be the most likely estimation and was recorded assumed to be the correct answer. The last strategy, with the purpose of assessing the type of evaluation (question fourteen), also utilized text matching as a method. This strategy added the document title to sub-sections that was analyzed. Both strategies furthermore included validation steps that compared the estimations against available benchmarks, such as a comparison with the publishing date of the evaluations (i.e. the publishing date is likely to fall within the estimated project phase in cases of mid-term evaluations). 

### Caveats
The most obvious limitation with the QSS´s in this section is the inflexibility that comes with the rules-based approach. The underlying rules are deterministic and mostly designed based on expectations on how the underlying documents are structured. There will most likely always be deviating observations and it is close to impossible to derive a rules-based approach that yields perfect results when dealing with these relatively complex documents, which hold a high degree of variation in both content, structure and individual writing styles.

False predictions or inaccurate results are thus to a certain degree unavoidable. Example of this shortcoming is limitations in grasping the importance of a key country when many different countries are frequently mentioned. Another example, with bearing on time period, is referenced to older programme periods for the same object. These are examples of context complexity and settings that are difficult for the QSS to handle. Yet another challenge are cases where there is no data recorded to be assessed in the QSS (e.g. no county names where found). There are also limitations when it comes to capturing more abstract notions such as the theoretic scope rather than a practical one. For instance, if operations in an evaluated project or programme are centered in a few countries, but the project objective/s suggests a wider geographical scope, beyond the core/mentioned countries, the designed strategies have been observed to make the wrong predictions on occasion. 
<!--
It should however be emphasised that these shortcomings, in many cases, hold true also when manually processing of the sata. This has also has been observed in this study and will elaborated in later chapters. 
-->
However, the developed strategies also hold advantages. Besides the typical factors, relating to the advantages in speed and consistency, the geographical strategies have harnessed the advantages to collect larger amount of data by default. The designed strategies records additional meta data besides the necessary country names including information on example for geographical region and focus area. During the text parsing exercise additional entities were singled out, such as OECD/DAC donor countries and donor organizations, which can give additional insights into how the evaluated projects/programmes are funded. This data could also be used to give deductive estimations with regards to whom Sida and Sweden collaborates with. This could in turn fuel an analysis of key objectives in the Paris Declaration on Aid Effectiveness relating to for instance donor alignment and harmonization from a Swedish perspective. 




[^gt1]: The accuracy levels between the validation dataset and the LME-dataset are in a few cases based on few observations (<5 evaluations). This is an effect of the LME-dataset’s variating coverage – not all questions have 128 observations – and since the validation dataset is based on a random sample of the full sample (128 evaluations) the number of comparative observations varies between questions. 


<!--
[^gt1]: Note that the accuracy levels between the validation data set and the LED in some cases are calculated on very few observations (<5 evaluations).
-->

