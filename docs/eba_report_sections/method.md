# Methodology

This chapter elaborates on the overall work approach and the analytical steps taken in this study. The ambition is to enable a high degree of transparency that can allow for a good intuition for the analytical steps taken. A [project repository](#other) containing all the model code and documentation is also made available which allows for full reproducibility of the study results. This chapter also introduces the computational techniques that have been applied, as well as the conventions for how to evaluate the performance of the analytical results. 

## Natural Language Processing  

Natural Language Processing or NLP is a collective phrase or catchall term for general approaches to “process” natural or human language. In practice, NLP involves the use of a wide variety of computational algorithms and techniques, which allow us to e.g. identify linguistic rules, uncover the structure of a text, and extract meaning. Common tasks to which such algorithms are applied include areas such as text classification, text similarity, text summarisation and keyword extraction.

<!-- T In this section we provide a brief overview of NLP as well as some of the most important methods that we have applied to various questions in the analytical framework. 

The list is by no means intended to provide an exhaustive summary of NLP methods or the methods applied in this study but rather give an overview of some of the most central NLP techniques that have allowed us to uncover the results found in this study. 

Before moving forward to the detailed processess executed in this study a brief discussion on the studies general strategies should be spelled out.
Three broad *types of strategies* have been used depending on the understanding of possibilities and challenges involved with responding to a given question. Selection of what strategy to apply basically comes down to the complexity of the question, availability of data, and available resources. 
All three types of strategies are listed below with brief expiatory text in terms of background and requirements. 


### Introduction to NLP
-->

As humans we process language pretty well, but we are not perfect. Misunderstandings are relatively common among humans and we often interpret the same texts or language differently. In other words, language processing is not deterministic, and something that might be interpreted in one way by one person, may have a different meaning to another. A common example where this occurs frequently is when irony is used in texts or speech. 

This inherent non-deterministic nature of language processing makes it an interesting and difficult problem to develop machine-based algorithms for. In this sense, understanding language is like creating a new form of intelligence in an artificial manner that can understand how humans process language, which is also why NLP is a subfield of artificial intelligence. Importantly, if humans do not agree 100% on NLP tasks, such as text classification or language translation, it is not in general possible to model an algorithm to perform these tasks without some degree of error. In machine learning this peer-to-peer human understanding on a given subject or question is commonly referred to as inter-annotator agreement. A typical example, in NLP where the level of inter-annotator agreement tends to be large is the problem of text classification i.e. recognising which category a specific text belongs to (e.g. should a novel be categorised as thriller or drama). In general, the level inter-annotator agreement tends to form an upper boundary or benchmark for what to expect in terms of performance from machine-based approach on a specific task (see for example Artstein 2017 or Bobicev and Sokolova 2017). 


<!-- https://sigmoidal.io/what-is-natural-language-processing-nlp/#:~:text=Parsing%3A,uses%20Linguistic%20rules%20and%20patterns.&text=Statistical%20NLP%20induces%20linguistic%20rules,of%20a%20new%20data%20source. -->

The methods applied in the field of NLP are often separated into two different sets of approaches. One relying on hand-crafted set of rules, and the other on statistical or machine-learning techniques. In practice, however, NLP is typically comprised of a combination of these two approaches where parts of both approaches are used with the intention to find a potent mix that can optimise the level of accuracy. It is this mixed-method approach we have taken on for most part in this study, where statistical models have been used for some parts, and rules-based techniques have been applied to others. Below we provide a brief overview of these approaches and some of their most central methods and features.


### Rules-based methods
 
Rule-based systems are the earliest approach to NLP and consist of hand-crafted linguistic rules for text analysis. Each rule is formed by an antecedent and a prediction. So, when the system finds a matching pattern, it applies the predicted criteria. Since the rules are determined by humans, this type of system is easy to understand and can sometimes provide accurate results with little effort. However, manually crafting and enhancing rules can be a difficult and cumbersome task, and often requires a linguist or a knowledgeable engineer that has deep knowledge of the intrinsic details of the domain that is being analysed. Also, adding too many rules can lead to complex systems with contradictory rules. The rules-based approach has been a given choice in this study for cases/questions where the task have been relatively straightforward, such as to identify unique text passages, assess word frequency or extract keywords from documents. An example, of such an application in this study is an algorithm known as Tf-Idf (term frequency - inverse document frequency), which is typically used to extract keywords from a text. In a nutshell the algorithm counts the frequency of occurrence of each word in a document, and then weighs these frequencies based on how common these words are in other documents in the same corpus.[^m1] 

Although the analysis, which can be done with these types of methods are limited, a major advantage is that they do not require any labelled training data and cumbersome model estimation, which typically is the case when statistical or machine learning methods are applied. As a result, rules-based methods are a good option if you do not have much data and are just starting out on an analysis and need to conduct exploratory analysis of the used language.

### Statistical/machine learning based methods
By statistical approaches and machine learning methods we mean algorithms which have been crafted to learn and make predictions based on previous observations. This process is typically referred to as the training of a model or establishing a hypotesis. In other words, the process where the model learns to make associations between a particular input and its corresponding output. 

In the figure below we have depicted a generic model that has been applied in this study. In most cases the applied models or hypothesis have been derived from pre-trained models, but we have also trained models of our own for a few of the questions in this study. In short, and as depicted by the figure below. The vertical process constitutes the training process where labelled training data is fed to a learning algorithm. In a labeled dataset, the labels are typically defined manually, and simply constitutes a question/answer sheet from which the algorithm can learn the correct answers to a predefined set of questions. The algorithm then calibrates a model by seeking out a set of parameters such that the model produces the best guesses of the correct answers to the questions in the labeled dataset. Translated to this study, the LME-dataset has been used to train various algorithms. Once the model has been trained the horizontal process or prediction of new or unprocessed data can be executed. In the case of this study new evaluations or identified text paragraphs of relevance have been fed to the trained algorithms which has made predictions based on this training. 


**Figure 2.a Generic representation of statistical/machine learning model**
@import "images/eba_approach.png"

The displayed learning process is the biggest advantage of these methods since their ability to learn on their own, implies that there is no need to define manual rules. What you however need is accurate training data, which constitutes the foundation and the relationships upon which we want the model to learn. Machine learning models typically perform better than rule-based systems over time, and the more training data you feed them, the more accurate they often become. However, the algorithms are typically data hungry in the sense that they need enough training data relevant to the specific problem you want to solve in order to produce an accurate model.

Training data can often be difficult to acquire and usually involves many hours of manual work labelling the data where people with expert domain knowledge usually are needed to ensure quality. This is for example the case when training models to predict aspects such as a words part-of-speech tag or the linguistic relationships among words within a sentence. Another example, where this is crucial is within the task commonly referred to as Named Entity Recognition ([NER](#Methods)). This includes the process of finding specific types of entities within a text, where an entity can be a word or a series of words that have bearing on, for example, a personal name, an organisation, a location, a product as well as date related expressions, money and more.[^m2]  NER was introduced in the middle of the 1990’s in an attempt to find solutions for extracting data on entities within the field of information extraction (Nadeau and Sekin 2007).

<!-- 
 NER can be designed by using linguistic grammar-based techniques as well as statistical approaches, and there are advantages as well as disadvantages with both approaches (Gupta 2018). 

 The spaCy model used in this study are based on a statistical- or machine learning approach that utilises large volumes of annotated examples over real-world entities to train the models and the accuracy for predicting entities are close to 86% (Honnibal and Montai 2017).  -->



**Text embeddings**

A central concept in NLP research where machine learning approaches have yielded much success involves the concept of text embeddings. Text embeddings​ is a process where words or phrases from a vocabulary are mapped to vectors of real numbers. These numerical vectors thus become valued representations of text strings, where the numbers in the vectors are chosen so that vectors lying close to each other in a vector space represent text strings that appear in similar contexts in documents. 

Text embeddings are considered a good starting point for many complex NLP tasks. They allow deep learning to be effective on smaller datasets, and are one of the most popular ways for doing transfer learning in NLP where knowledge from training on one problem is transfered on to another. A clear advantage with these algorithms is that they do not require manually labelled training data, but instead relies upon large volumes of text from common data sources, such as Wikipedia in their training process. The labelling (of the training data) in this case is extracted from pre-existing relationships in the way sentences and words have been spelled out in relation to each other.

One of the most popular text embedding algorithms in recent years has been [Word2vec](#Methods), which was created and published in 2013 by a team of researchers led by a group of scientists at Google (Mikolov et.al., 2013). An interesting revelation when this research came out was that the word vectors that were produced by the algorithm could actually be used to mathematically solve word riddles. One of the most noteworthy was the riddle: *"King - man + women = ?"*. Replacing these words with their mathematical representations (i.e text embeddings) produced by the Word2vec algorithm, resulted in an output vector which was most close in the vector space to the numerical vector for the word *queen*, which by many was viewed as the most logical answer to the above riddle.

In this study pre-trained embedding models have been frequently applied, and for a few questions models have also been trained on available data from the [LME-dataset](#other) . This includes training with the Word2vec algorithm on our corpus consisting of 311 evaluations. However, for most cases these text embedding techniques have recently been surpassed by a new class of model algorithms often referred to as [Transformers](#Methods) which also has been utilised and applied in this study.


**Contextual text embeddings**

A main challenge with Word2Vec is that it provides a single representation for a word that is the same regardless of its context. This means that words like "bank" in several different senses, for example river bank and investment bank, will end up with a representation that is an average of the senses and thus not representing either of the two particularly well.

For this reason, following research focused on the idea of training separate language models to produce better contextual word representations. This has led to the development of the mentioned Transformers networks. The transformer is essentially a deep learning model proposed in a paper by researchers at Google and the University of Toronto in 2017, used primarily in the field of NLP (see Vaswani et.al. 2017). Since their introduction, transformers have become the model of choice for tackling many problems in NLP, in particular due to their capacity to differentiate between words based on their context.

This enhancement has been somewhat of a revolution and led to the development of a wide variety of pre-trained systems all building off the abilities made possible via transformer networks. Examples of such are the BERT (Bidirectional Encoder Representations from Transformers) and GPT (Generative Pre-trained Transformer) models, which both have been trained on very large language datasets, and can be further fine-tuned to specific language tasks. These models are typically available to the general public as open source code which can be readily downloaded through various channels.

In this study, we have relied on these transformer networks to solve specific challenges. The models have been accessed via an open source package called [Huggingface's transformers](#open-source-packages). This package provides thousands of pre-trained models to perform tasks on texts, such as classification, information extraction, question answering, summarisation, translation, text generation, etc in 100+ languages, with the aim to contribute to the public good and make cutting-edge NLP easier to use for everyone with an internet connection. 


<!--

As already mentioned we rely heavily on existing state-of-the-art NLP techniques in this report. 

Two of the more advanced topics which require more in-depth explanations include the use of text embedding methods and named entity recognition which we describe below.


Pre-processing of all words in the complete corpus (i.e. all evaluations) in order to single out words with contextual similarity to all three areas - "donor dependency", "dependency", "donor". This allows for compilation of a context specific list of matching words that reflects the used language and variations within in the evaluations. This pre-process utilises spaCy's pre-trained similarity function that uses word embeddings or word vectors that has been generated with the algorithm word2vec (https://spacy.io/usage/vectors-similarity). This process rendered a range of words that has been manually scrutinised and the following lists hold the lemmatised versions of the words that have been deemed to be of relevance for identifying sentences with bearing on funding of the evaluated projects/programmes.


BERT looks at all the words in the sentence as a whole.

-->










## Detailed walkthrough of study processes

For each selected question phrased in the [LME-dataset](#other) (see appendix 1.1 for the questions) different approaches have been designed, developed and practically tested in what we will refer to as the *question-specific strategies* (henceforth the [QSS](#other)) of this study. Each designed strategy is based on what was deemed the most suitable path to take in order to secure a solid approach that would yield good results. In addition and depending on the estimated accuracy of the designed strategies two possible applications have been executed in this study. First, strategies estimated to have high performance, and thus correlate well with the results from LME-dataset, have been used in a scaled-up exercise where the designed strategy has been applied on the full set of available evaluations between 2012-2020. Second, strategies that perform poorly and thus with low correlation with the LME-dataset has not been deemed to be suited for generating predictions on unprocessed evaluations. Instead, challenges and flaws with the poor strategies are discussed together with possibilities to improve the strategies (on a theoretical level). 

The figure below outlines the generic steps taken in the development of all the QSS in this study. 

**Figure 2.b Generic process for development of question-specific strategies**
@import "images/eba_strategy_process.png"

Specific details on the steps taken in the development of all the QSS in this study follows below:

First, a manual assessment of a random sample of evaluations processed in the LME-dataset was done in order to get an idea of what methods may be useful to apply. In general, each question required a unique focus in order to grasp how to design and later deploy each of the developed QSS. An important part of this step was to review and use the LME-dataset as a point of departure for how to design each strategy.  

Second, for each question a choice was made on the most appropriate design to use to address it. This included the following sub-steps, searching for methods that had been successfully applied to similar questions in the past as well as look for available [Open Source Packages](#other) that could be utilised.  

Third, the design and coding of each strategy was implemented in order to allow for automated processing of multiple evaluations.   

The fourth step then involved, testing the developed code by applying it on a sample of evaluations from the LME-dataset. This step also included performance testing where the results of the developed strategy/algorithm were compared with the labels provided in LME-dataset - the applied tests at this stage are carefully described in the subsection *Evaluating performance* below. A manual assessment of these results was then done in order to follow-up on  any significant discrepancies between the output produced by the algorithm and the labels provided in the LME-dataset.  

Fifth, based on details and insights from the manual assessment the strategy was adjusted in order to improve the strategies performance. The majority of designed strategies furthermore required a number of iterations of steps 4 and 5 in order to arrive at a final strategy where we did not see any immediate options for quick improvements.  

The sixth step involved a decision between two possible paths forward based on the strategies overall performance. Strategies with good performance, in the sense that the developed strategy produced results which aligned well with the LME-dataset labels, where used to extrapolate the analysis and include all evaluations from 2012 and onwards (>300). 

For well performing strategies the following steps where then executed:  
a. Scale up of process and deployment of the QSS on the full sample of evaluations.  
b. Descriptive statistic analysis and visualisation of results. The recorded estimations were compiled in a dashboard for easy access for the whole assessed period.   
c. Comparative analysis between the LME-dataset, the results/output from the designed strategies as well as estimations from a third party/independent validation assessment based on a random sample of 30 evaluations (see further details below)).

Strategies with lower accuracy and thus not deemed to have enough potential to generate reasonable estimations followed the following steps:  
a. Thorough elaboration of the challenges and problems with securing a high enough accuracy.  
b. Additional research and theoretical discussion on possibilities to improve the strategy.   
c. Comparative analysis between the LME-dataset, the results/output from the designed strategies as well as estimations from a third party/independent validation assessment based on a random sample of 30 evaluations (see further details below)).  

Finally, the last step involved documentation of the full process for each QSS. All strategies have been thoroughly documented with the applied method/s, results and caveats and are readily available in the [Project repository](#other). 

<!--

1. Manual assessment of a random sample of evaluations processed in the LED data set. Each question required a unique focus in order to grasp how to designed and later deploy each of the developed QSS. An important part of this step was to review and use the LED data as a point of departure for how to design each strategy. 
2. Theoretical design of each QSS. This step included the following sub-steps:  
    a. Team discussion on possible solutions and decision on path to take.  
    b. Research of available [Open Source Packages](#other) to use.
3. Practical design of each QSS - development and setup of code structure.  
4. Testing of QSS where the developed code was applied on a sample of the LED evaluations. This step also included the following sub-steps:  
    a. Performance test where the strategy’s result or output was compared with the results from LED.
    b. Manual assessment of deviating results. This include follow-up on discrepancies between the output from the designed strategies and the labels from LED.
5. Optimisation of the strategy. Based on details and insights from the manual assessment (step 4b) the strategy was adjusted in order to improve the strategies performance. The majority of designed strategies furthermore required a number of iterations of Steps 4 and 5 
6. Usage if designed QSS. At this stage one out of two possible paths were selected for each strategy, and the selection was made based on the strategies overall performance as mentioned above. Strategies with good performance, and thus deemed to have potential to give solid estimations, where used to extrapolate the analysis and include all evaluations from 2012 and onwards (>300).   
    For strategies with high accuracy the following steps where executed: 
    
    a. Scale up of process and deployment of QSS on the full sample of evaluations.
    b. Descriptive statistic analysis and visualisation of results. The recorded estimations were compiled in a dashboard for easy access for the whole assessed period. 
    c. Comparative analysis between the LED, the results/output from the designed strategies as well as estimations from a third party/independent validation assessment based on a random sample of 30 evaluations (see further details below)).
    
    Strategies with lower accuracy and thus not deemed to have enough potential to generate reasonable estimations followed the following steps:
    
    a. Thorough elaboration of the challenges and problems with securing a high enough accuracy.
    b. Additional research and theoretical discussion on possibilities to improve the strategy. 
    c. Comparative analysis between the LED, the results/output from the designed strategies as well as estimations from a third party/independent validation assessment based on a random sample of 30 evaluations (see further details below)).
7. Documentation of the full process for each QSS. All strategies have been thoroughly documented with the applied method/s, results and caveats and are ready available in the [Project repository](#other). 


-->


## Evaluating performance

As described above each QSS involved a test of various methods and techniques. In order to evaluate their performance a benchmark or baseline for comparison needed to be established. As mentioned, one such baseline for comparison has been the labeled data from the LME-dataset. The designed strategies predictions have thus been compared to the manually labelled data in mentioned dataset for each question.  The idea is that when designing algorithms one can use these manually crafted labels as a *source of truth* when evaluating the performance of the algorithm. However, other potential benchmarks are also possible. Bellow we describe our performance benchmarks in further detail.

<!--

**Industry benchmarks**

https://gluebenchmark.com/leaderboard 
https://towardsdatascience.com/evaluation-of-an-nlp-model-latest-benchmarks-90fd8ce6fae5 
-->


**Performance metric**

Several metrics for evaluating the performance of machine learning models exists. In this report we will adopt one of the most common metrics called *"accuracy"*. The accuracy of a model or algorithm has to do with the relative share of labels in the dataset that were correctly predicted. For example, imagine we have a dataset consisting of 100 sports referees from tennis and hockey, of which 30 have been labelled as hockey and the remaining as tennis. If our model, which is designed to predict the correct labels, manages to label 20 of the 30 hockey referees as hockey, and 40 out of the 70 tennis referees as tennis, then the accuracy of its predictions would be calculated as 60 percent - ((20+40)/100)).[^m2b] 

**Evaluating accuracy scores** 

When comparing accuracy score of different classification problems, one must also account for the difficulty of the classification problem. Clearly, achieving high accuracy scores are easier when predicting the correct outcome in a classification problem involving only two labels, compared to a classification problem where ten possible labels exist. For this reason, we may also want to evaluate our model based on the difficulty of the classification problem.  This can be done in various ways. The most straightforward approach may be to calculate the expected outcome of a random choice where equal probabilities are given to each label. For example, if only two labels exist there is a 50-50 chance that we would guess the correct outcome. For a case with three labels, the corresponding probability is 33 percent, and so on. With this information we can at least judge whether an algorithm or model is performing worse than if labels were just chosen randomly.

**Frequency adjusted random accuracy scores** 

The above mentioned type of comparison can work well in many cases, but there are some cases where it may be misleading. For example, if we were training a machine learning model to perform a classification exercise, were all the input data has been replaced by nonsensical data, the training exercise may instead of producing a model which tries to make sense of the input data instead start to make guesses based on the frequency of label occurrence. In other words, the model learns the empirical frequency of a labels in the training dataset and makes guesses based on what it expects the probability of occurrence may be. To account for this, one could instead evaluate a models performance based on a probability adjusted random guess, which takes into account the empirical distribution of the labels. For example, in the sports referee example above, if we were to choose a referee at random, the probability of picking a hockey referee would be 30%. Hence, if we picked out a random sample of 10 referees and counted the number of tennis referees vs hockey referees, we would on average find three hockey referees and seven tennis referees if we repeated this experiment enough times. The machine learning model might thus learn that the distribution of labels in the training data is skewed in this way, and make use of this information to also inform its predictions. If this is the case, this may imply that we wrongfully conclude that the model has learned to predict labels well based on the underlying training data when it in fact only has learned how many of each labels exists in the training dataset. Hence, if machine learning models only were evaluated based on how much better they perform than a purely random guess this would then imply that we would be favouring models that were trained on datasets with highly skewed labels. For this reason, a probability adjusted random choice based on empirical frequencies of the labels in the training dataset is often a more appropriate benchmark comparison when evaluating machine learning models.

**Third party validation**

Another benchmark utilised in this study aims to compare our results to that of an independent assessment from a third party evaluator.[^m3] The purpose with this step was threefold. First, it allowed us to evaluate the performance of an extended set of questions with regards to other [OECD/DAC evaluation criteria](#other) apart from sustainability.[^m4] Second, it allowed us to also assess the designed strategies results to a second *source of truth*. Third, as mentioned above, human based assessments are typically not perfect and hence the third party assessment could thus give us an idea of what the upper-bounds for the accuracy scores might be in accordance to an inter-annotator agreement of sorts as mentioned previously. That is, if for example, the third party agreed with the LME-dataset labels around 90% of the time for a specific question, we should not expect any better performance from our machine-based approach.

**Presentation of findings**

In this study we have calculated all of the mentioned accuracy scores for all selected questions in order to shed light on the designed strategies estimated performance. The scores are reported in tables in the upcoming result sections, together with our initial assessment of the difficulty and confidence in developing a good strategy. The table columns are defined as follows:

- *QSS Accuracy*: Comparison of designed question specific strategies (QSS) predictions against the manually  assessed LME-dataset labels.
- *Label counts*: The number of plausible labels for answering a specific question i.e. the number of potential answers to a question.[^m5]
- *Random Adj Accuracy*: Theoretical accuracy scores of a random guess with probabilities for each outcome adjusted to match the empirical frequencies of the LME-dataset labels.
- *Third party Accuracy*: Accuracy scores for predictions from designed QSS's against the third party validation assessment.
- *LME vs. Third party*: Comparison of third party validation assessments to that of LME dataset. This comparison is based on 15 evaluations and computed in the same way as a standard accuracy score.
- *Anticipated difficulty*: Our initial pre-study assessment of the difficulty in finding a good strategy.[^m6]
- *Assessed difficulty*: Our ex post assessment of how difficult it was to find a good strategy.


[^m1]: This method was for instance applied in the first of our approaches to question 17 of the analytical framework.
[^m2]: This method was for instance applied in questions 3-5 in the analytical framework.
[^m2b]: For sake of transparency and in order to make our results easliy digestable to an audience novel to machine learning methodology, we have relied on accuracy as our sole metric of performance in this study. It is however, important to know that accuracy is not the only evaluation metric possible. Other notable examples include precision, recall and f-score (see e.g. Grus (2019) for further details on these metrics). 
[^m3]: The third party evaluator, Cecilia Ljungman, was chosen in dialogue with EBA, and has 25 years of experience working in the field of international development cooperation in general and with evaluations in particular.
[^m4]: A key question in the LME-dataset focused on the OECD/DAC criteria sustainability. The concept of this criteria and the attempts to design a machine-based approach that can automate parts, or the whole process, of assessing the evaluators judgments and conclusions relating to this criteria is therefore of central importance in this study.
[^m5]: For example, a question that can only be answered as a *yes* or a *no* has 2 labels, while a *yes*, *no* and *maybe* implies 3 labels.
[^m6]: The scale for difficult level ranges from: Very low; Low; Moderate; High, Very high. Our anticipated confidence level of being succesfull was also assessed ex ante with ranges from: Highly confident; Confident; Fairly confident; Unconfident. These judgments are provided in the appendix.  
