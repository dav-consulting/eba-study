## Thematic area

This section presents results for the applications of methods in an attempt to develop a QSS capable of generating reliable estimations on the thematic area of an evaluation. The LME-dataset contains 16 thematic areas for labelling the evaluations where each evaluation was given a single label. Translated from Swedish to English the labels were the following: "Democracy", "Human Rights", "Gender equality", "National, regional or local government", "Market entrepreneurship trade innovation",  "Agriculture forestry fishing land", "Education", "Research higher education", "Humanitarian aid", "Climate", "Environment and water", "Sexual and reproductive health and rights", "Conflict peace security", "Sustainable community building infrastructure" and finally "several categories in one". Thematic labelling was executed on all 128 evaluations included in the LME dataset. 

### Findings
#### Accuracy of designed strategies

The first strategy relying on word2vec word embeddings (detailed in the applied methods section below) performed the poorest. When comparing to the LME dataset the strategy predicted the same category in only 29 cases out of 126 (~23%).  The second strategy relying on pre-trained sentence-transformers performed significantly better. Compared to the LME dataset, this model predicted the same category in 44 out of 126 cases (~35%). The third strategy, relying on zero-shot learning, had the highest accuracy scores and performed best. By using the pre-trained zero-shot learning algorithm we managed to make predictions corresponding to the LME-dataset in 55 out of a total of 126 (~44%).

Given that in total there are 15 distinct labels to choose from a random guess would be expected to make on average 8 correct predictions that match the LED after 126 trials. In this light, our first strategy performs more than three times as good as the random guess; the second strategy more than five times as good; while the third strategy is more than 6 times as good. Similarly, a random guess with probabilities adjusted to account for the frequency of occurrence in the dataset would on average guess inline with LED in 15 out of a total of 126 (~11%). Although, these strategies perform quite well in comparison to random guesses the results are in our opinion are still not sufficiently good to replace a manual labour and hence lack the performance to be included in the scaled-up analysis for all collected evaluations.


### Applied methods 

The task of labeling text and placing them into different bins is typically referred to as topic or text classification. There exist several methods for approaching this problem ranging from the purely rules-based methods to the training of models adapted to the specific task at hand. The success of these methods also varies depending on context, and more specifically the extent to which the classes/labels are regarded as exclusive in the sense of being very distinct in terms of the texts in which they are nested. 

We tested three different approaches for classifying the evaluations. These approaches all involve the use of [word embeddings](#methods). The first approach relies on the word embeddings called "en_core_web_lg" which is part of [spaCy](#open-source-packages)´s NLP package. These vectors are based on Levy and Goldberg (2014) which involves a specific  implementation of the [word2vec](#methods) model. The approach also makes use of [Tf-Idf](#methods) vectors, i.e. a method for extracting keywords from a document.

The analytical procedure for this strategy was as follows:  
- For each evaluation we extracted the evaluation keywords using the [Tf-Idf](#methods) algorithm.  
- For each category we manually create a list of 10 synonyms to the topic.  
- We computed a similarity score between each category synonym and each keyword for a each evaluation.  
- We matched each evaluation to the category which had the highest average similarity score.  
- If two or more topics had very similar average scores. We assumed the evaluation covered more than one topic.

The second strategy relied on the use of pre-trained sentence-transformers from a [spaCy](#open-source-packages) extension package. This package wraps sentence-transformers (also known as sentence-BERT) directly into spaCy (see Reimers and Gurevych, 2019). The intention of this algorithm is that when the similarity of the pair of sentence embeddings is computed, it should represent accurately the semantic similarity of the two sentences. This differs from standard measures of sentence similarity where similarities are computed by simply averaging the similarity among the different words in a sentence. Using the [spaCy](#open-source-packages) - sentence-transformers we calculated the sentence similarity between the title of the evaluations and the translated categories above.

The procedure for the second strategy was as follows:  
- First calculate the sentence embeddings for evaluation titles using spaCy - sentence-transformers.  
- Second compute the similarity between these embeddings and the topic descriptions.  
- Match each evaluation to the topic which had the highest average similarity score.  
- If two topics had very similar average scores. We assumed the evaluation covered more than one topic.  

The third strategy designed to estimate predictions to this question relied on an implementation of [zero-shot learning](#methods) using [Huggingface's transformers](#open-source-packages). This is an unsupervised machine learning approach which can be used to solve text classification problems when there is no training data available to train a model. Instead, this approach relies on the use of large scale pre-trained transformer models, similar to what we applied in our previous approach for developing a strategy for estimating the sustainability of the evaluated projects/programmes (question seventeen). Further, as in our second approach we assumed that the titles of the evaluation provide enough information as to which category the evaluation belongs to.

Thanks to Huggingface's transformers the procedure for implementing this method is rather straightforward. The procedure involves feeding the algorithm with a list of evaluation titles as well as a list of potential categories to which each title may belong. The algorithm returns a score for each potential category were numbers close to one indicate a high degree of similarity between category and title. The category receiving the highest score is then chosen as the best guess unless the score is below a certain threshold which indicates that it may belong to more than one topic.

### Caveats
<!--
With more time and experimentation we expect the results would likely improve. However,
-->
A major caveat for classifying the thematic focus was the fact that there were so many topics and the fact that they tend to be semantically very similar. For example, topics such as democracy and human rights often appear in similar contexts and hence tend to lie close to each other in vector space. This creates a challenge for these types of algorithms that tend to work better when categories are semantically more distinct e.g. sports and politics. A simple way to improve the performance of our third strategy would thus simply be to reduce the number of categories and make sure that their intrinsic meanings are distinct. 

Another issue for this section aligns with comments or caveats from earlier sections in this study. Namely disagreement, in some cases, relating to the applied labels in the LME dataset. One obvious reason for this discrepancy in the case of assigning a thematic area is likely due to the relatively large variety of labels which may be applied to each of the processed evaluations. 

Two examples, where we disagreed with the LME dataset and agreed with the labels assigned by the [zero-shot learning](#methods) algorithm were the evaluations with series numbers 2012:2 and 2014:54. In 2012:2 the title of the evaluation was "Review of the Sida-funded Project Education for Sustainable Development in Action (ESDA)". In this case, the zero-shot learning labeled this as the thematic area "Education" while in the LME dataset it was labeled as "Climate change". From the title and reading of the executive summary we find no evidence in support of labelling the thematic area as "Climate change", but instead find quite compelling evidence for the label "Education". For 2014:54, the title was "MidTerm Review of The LVEMP II Civil Society Watch project of the East African Sustainability Watch Network". Here the LME-dataset is Agriculture forestry fishing land while [zero-shot learning](#methods) gave it the label "Environment and water". Manually reviewing this evaluation we would also have labeled it as the latter. 

On the other hand, our manual assessment is clearly dependent on context and/or the original intentions of the creators of the typology, our subjective judgements may therefore be incorrect. These examples were thus not lifted out to point out that the LME-dataset is flawed, rather the point we are trying to make is that assigning labels is a tricky context dependent task which is easy to get wrong and thus perhaps not suitable for a fully machine-based assessment.




