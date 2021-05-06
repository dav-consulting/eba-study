## OECD/DAC evaluation criteria

This section presents results for the developed QSS for assessing what evaluations have concluded regarding the OECD/DAC evaluation criteria sustainability as well as the potential it may have in terms of scaling up to an assessment of what the evaluations have concluded about other [OECD/DAC evaluation criteria](#other). <!-- A central question in the LME dataset related to what past evaluations have concluded regarding the OECD/DAC criteria sustainability in evaluations covering the years between 2012-2014.--> The specific questions that are addressed in this section are the following:

    Q17. Is the contribution(and/or its results) deemed to be sustainable?
    Q23. Does the evaluation mention the contribution's sustainability in the evaluation's summary?
    Q24. Does the evaluation mention the contribution's sustainability in the evaluation's recommendations?
    Q25. Does the evaluation give recommendations for how the contribution can improve its sustainability?

### Findings
#### Accuracy of designed strategies

The results from the first developed QSS, which made use of a pre-trained sentiment classifier, to address question 17 performed quite poorly when evaluated against the LME-dataset. The predictions of our sentiment classifier aligned with the manual assessments in the LME-dataset in only 41 out of a total of 126 evaluations that were assessed. This corresponds to approximately an accuracy score of 33%. 

As detailed in the applied methods section below, the poor results triggered an attempt to set up a second strategy for question 17. This strategy was designed to test whether the predictions could be improved if we instead trained a model of our own for the specific task at hand. This approach is what the NLP community would generally resort to when the accuracy of models are of central importance. High accuracy rates are however typically produced when large volumes of labelled training data are available, and the 126 evaluations that were available in this case are to be regarded as a very small dataset, which at the outset thus dimmed our hopes to successfully train an accurate model. Interestingly, the trained model did however perform significantly better than our previous strategy. Based on a five fold cross-validation (see applied methods below), our model aligned with the labels derived from the LME dataset, on average, in 11 out 27 evaluations. This corresponds to approximately 40 percent of the predictions correctly aligning with the LME dataset.[^dc0] Although this result is not likely to be sufficiently high to be of any practical use, it still provides ground that this strategy has potential if more time and resources are spent on optimizing the model parameters, as well as extending the size of the training dataset. For instance, by annotating additional labels that could be used to improve the model's accuracy. 

It is also noteworthy that the correlation between the LME dataset and the validation dataset is just slightly higher (47%) in this case, which underlines the difficulty involved in finding a successful approach for this question. Further, when evaluating the models trained on the 14 evaluations assessed by the independent third-party expert, the score looks better and reach an accuracy score of 49%, which thus looks even better in contrast to the comparison between the LME dataset and the third party assessments. Importantly, it should however be noted that the size of the evaluation dataset is very small implying that one should be careful in drawing far reaching conclusions from these results.


An important benchmark when evaluating these results is also what outcome one should expect if the accuracy was nothing more than a random guess. In this light the results of the first approach is slightly better than reported above, and the second significantly better. A purely random guess would on average align with the LME labels about 25% (1/4) of the time indicating that both methods still manage to produce some information of value. As previously mentioned, a comparison to a random guess may however not be the most adequate baseline for comparison. Instead a frequency adjusted random guess, which takes into account the empirical distribution of the labels may be a better comparison (see applied methods section below). For the full sample of 126 evaluations, the LME dataset reports 24 as sustainable, 46 as partially sustainable, 46 as unsustainable and 14 as non applicable. Based on these numbers the random guess, could thus be adjusted and instead of having an equal probability for each outcome base these probabilities on each label’s frequency of occurrence in the underlying dataset. Such frequency adjusted probabilities would result in an algorithm that guesses unsustainable or partially sustainable ~36.5% of the time (i.e. they both occur in 46 out of the 126 evaluations) and sustainable ~16% (occurring in 20 out of 126) of the time and non applicable ~11% (occurring in 14 out of 126) of the time. On average such an algorithm would align with the LME dataset in approximately 30% of the times (38 out of 126 trials if repeated enough times). This is a relevant comparison for the second question specific strategy where a unique model was trained. The reason for this is is simply that if our training data contained no information of value for predicting the correct label, the training algorithm may simply adjust its parameters so that predictions are made entirely based on each labels’s frequency of occurrence in the training dataset instead of making predictions based on the prediction data. 

For questions 23-25, regarding whether the OECD/DAC criteria was mentioned in the text, the results were much better which is partly due to a lower level of difficulty. For question 23 we replicated the results from the LME dataset in 83% of the cases, while for question 24-25 the results matched in approximately 76% of the cases. The table below summaries these results (see [section 2.3](#evaluating-performance) for detailed explanations of columns). 

| Question  | QSS Accuracy | Label counts | Random Adj. Accuracy  | Third party Accuracy | LME vs. Third party |  Anticipated difficulty | Assessed difficulty |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Q17 | 40% | 4 | 30% | 49% | 47% |  High | Very high | 
| Q23 | 84% | 2 | 69% | 76% | 60% | Moderate |  Low  | 
| Q24-25 | 67% | 2 | 71% | 66% | 60% | High |  Moderate | 

Questions 23-25 further used an approach that allowed us to also evaluate the results from these questions against other OECD/DAC evaluation criteria (i.e. apart from sustainability). For these criteria areas, the accuracy was assessed using the assessment from our third party validation dataset. The results turned out to be more or less equally favorable as that of sustainability. The accuracy scores are summarized in the table below.

| Question  | Relevance | Efficiency | Effectiveness  | Impacts |
|:---:|:---:|:---:|:---:|:---:|
| Q23 | 86% | 76% | 83% | 45% |
| Q24-25 | 79% | 69% | 86% | 59% |

Finally, and given the higher level of accuracy for the developed strategies for question 23-25, it may also be of interest to display some statistics when deploying the model on all of the collected evaluations (>300 evaluations). The result from this is depicted below and show the occurance of all OECD/DAC evaluation criterias in the processed evaluations' chapters/sections covering the summary section as well as the recommendation section. 
<!--
**[kanske ska fylla på mer här med att det ändå ger viss insikt i att se vilka kriterier de arbetar med. Och ev stämma av med uppdragsbeskrivning.]**
-->
This data gives indications on what the conducted evaluations focus in terms of their analytical scope and could be cross-referenced with the ToR for assessment of the amount of compliance and/or changes the evaluations undergo compared to the original plan from the Terms of Reference.
<!--
An interesting aspect is that all the OECD/DAC criteria are mentiond much more frequently in the recommendation sections than in the executive summarys of the processed evaluations. 
-->
**Figure 8. Estimation of occurrence (%) of OECD/DAC evaluation criteria between 2012-2020**

@import "../images/dac_all.png"

### Applied methods 

Among these questions, number 17 proved to be the most challenging and several different statistical-based strategies were developed and tested. First, in order to address the question in a way that could be scaled to other OECD/DAC evaluation criteria, our first strategy relied on building a so called classifier that would classify each evaluation criteria into one of the four labels applied in the LME-dataset for this question. The idea was that this classifier would build upon a previously trained language classifiers from the open source community that could be modified for this purpose. In particular, we hypothesized that a so called [sentiment classifier](#methods) (positive, negative or neutral labelling) could be applied to the sentences or phrases from the evaluation that mentioned sustainability or other OECD/DAC evaluation criteria, and then weigh them together to produce an overall document sentiment score. 

The support for our hypothesis came from other attempts in classifying tweets from twitter in a similar way which has achieved accuracies as high as 60% (Elbagir and Yang, 2019). To accomplish this we made use of a pre-trained sentiment classifier provided by [Huggingface’s transformers](#open-source-packages). The approach was thus simply to extract sentences containing the variations of the word sustainability and then after some preprocessing (removing e.g common words and casing) apply the sentiment classifier to these sentences.

The classifier gave us a label (positive or negative) and a score between one and zero indicating the strength of the sentiment. An overall score was then obtained by averaging the individual sentence scores. Finally, we experimented with various threshold levels for when a score should indicate that a document belonged to the "partially" or "not applicable" category as labeled in the LME dataset. As reported in the result section below the performance of this approach was unsatisfactory. 

For this reason we also looked into a second strategy for addressing the question. This method relied on state-of-the-art methods for text classification using another modeling pipeline also provided by Huggingface’s transformers. This strategy made explicit use of the manually labelled data from the LME dataset. More specifically, we made use of the provided labels to train a machine-learning model with the specific objective of predicting the label given to a specific evaluation.

The training process involved designing and setting up a neural network model featuring pre-trained parameters from a large scale state-of-the-art language model, and then fine tune that model to the task of classifying our evaluations into one of the four categories in the LME-dataset[^dc1]. The pre-trained parameters we used for this task were based on the well-known language representation model [BERT](#open-source-packages) (Devlin, et.al., 2018). This model was adopted both due to its high performance level but also the fact that it has become a benchmark model that much of the models that have come out since then are evaluated against.[^dc1b] The implementation of this approach was done using the [spaCy](#open-source-packages) package. In order to accurately evaluate the model, we split the full dataset into a training dataset consisting of approximately 80 percent randomly chosen evaluations that were represented in the LME-dataset (100 evaluations), and a test dataset consisting of the remaining 20 percent (27 evaluations).[^dc2] The test dataset was then used to evaluate the predictions of the model that we trained using the training dataset. This procedure was repeated five times with different test datasets in a procedure known as cross validation. The accuracy score reported below is an average of these five models' performance on their corresponding test datasets.


For questions 23-25 it was deemed that strategy were best to be based on rules-based methods to search for predetermined patterns and that this would give satisfactory estimations. All these strategies furthermore relied heavily on the successful parsing mechanism and the above described capability to parse certain sections in the evaluations (i.e. the executive summary for question 23 and the recommendation section for question 24-25). All positive observations were recorded and counted. The third party validation data also provides some additional insight of the performance and accuracy of the developed strategies. When it comes to question 23 - if sustainability is mentioned in the summary - the developed strategy correlates well with both the LME dataset (84%) as well as the third party validation dataset (76%). Question 24 and 25 - if the evaluation recommendation handles sustainability - secured decent scores with a rough 2/3 of the predictions matching for both datasets. 

<!--  EBA2017 Cross eval scores: 11 / 27  | 11 / 25 | 10 / 25 | 7 / 25  | 11 / 24  -->
<!--  ThirdParty Cross eval scores: 8 / 14   | 6 / 14 | 8 / 14 | 5 / 14  | 7 / 14  -->

### Caveats

The challenges in this section, and in particular for question 17, were mainly due to the complexity of the used language in many of the processed evaluations. Based on our own manual assessment of excerpts of text passages on sustainability we have observed that a relatively large share tends to refrain from the use of clear statements such as *"the project is not sustainable"*, and instead rely on more vague formulations in their language usage. The text passages below are anecdotal examples from our manual assessment[^dc3] where there have been discrepancies between the guesses produced by our developed strategies and the LME labels.

*"NBE has a strong economic situation, which means that the cost of continuing activities introduced in the NBE/SEA cooperation will not be a major threat to sustainability."*. 

*"It is impossible to provide any general conclusion about sustainability of knowledge gained from the programme. [...] which all point in a positive direction regarding sustainability of capacity development. Its sustainability will partly depend on what parts of the Turkish judicial reform programme go forward and to what extent such knowledge is applied. [...]. The general conclusion is hardly surprising: that the likelihood for sustainability depends on varying conditions within and outside the programme."*

*"Sida funding covered activities between 2012 and 2013, and clearly, it would be too early to judge sustainability at this stage. [...] It is difficult to discuss the potential for sustainability given the absence of follow-up and monitoring on ERRC’s activities. [...] Sustainability is also likely to be enhanced by a coherent human rights-based approach that prioritizes processes as much as results, including more focus on building capacity of partners."*

*"We also assess the capacity built through the municipal-level working groups to be sustainable; this is also the case for some of the working groups, which we expect to operate beyond the project intervention. [...] Nevertheless, the sustainability of results of the project depends largely on the ongoing commitment to JJ by government counterparts, which will, to some extent, be a result of continuing advocacy work by the international community"*.

These excerpts demonstrate the complexity when it comes to passing a judgment of whether or not they advocate for sustainability or not. This partly explains  why both of our strategies - the sentiment approach to classification and model training approach - underperforms for question 17. This complexity furthermore transcends, in our view, the limit between human and computer. In many cases because there is no simple answers to these questions, and it is this background that foreshadowed the discrepancies between the output from the developed strategies for question 17 and the LME data.

The overall conclusion from the above analysis is thus that the second strategy for question 17, involving training a model seems to be the most effective approach. However, and despite gradual improvements, the model accuracy was deemed too low for inclusion in the scale-up exercise to cover the full dataset. This accuracy level could however potentially be improved by further fine tuning the BERT model to the specific vocabulary used within the field of international development cooperation. Another limitation in this case is that the strategy could only scale to assessing more evaluations with respect to the OECD/DAC evaluation criteria sustainability. If another OECD/DAC were to be included a completely new model would have to be trained for this task alone. The amount of training data would likely need to be more than the 126 observations we had available in order to produce good results. 


[^dc0]: The corresponding standard deviation for the cross validation was approximately 6%.

[^dc1]: the LME-dataset included four labels for the assessment of question 17: "yes", "no", "partially" or "not applicable"

[^dc1b]: Since the publication of BERT, several models have been published that in benchmark datasets have a slightly higher performance than the BERT model. Examples, include models such as RoBERTa, XL-NET and T5. However, since these models are not as common benchmarks as the BERT model we did not use them in this study.

[^dc2]:  The random choice was done in a way that ensured approximately equal balance of labels in both the training data and test data.

[^dc3]: Our manual assessment showed that our assessment in many cases are in consensus with the labels in LME-dataset. However, disagreement is not uncommon in cases where the LME-dataset has deemed the there is no support for sustainability or in cases where information was concluded to be non existent. A likely explanation for the later, is that discussions on sustainability was not always available in a specific sustainability section but rather incorporated in a conclusions- or summary chapter - something that is easy overlooked in not the whole document is scrutinised for each evaluation. 

<!-- Examples, with decent accuracy have however been given also with small datasets which inclined us to also test how this would perform. 
 This contrasts to the much more explicit language present in datasets like imdb and twitter which are often used when evaluating NLP models (see e.g. Sun et.al. 2019).
-->


