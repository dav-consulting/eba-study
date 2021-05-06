# Extract evaluation topic (Sakområde)

## Method

We tested three different approaches for classifying the evaluations. These approaches all involve the use of [word embeddings](#methods). The first approach relies on the word embeddings called "en_core_web_lg" which is part of [spaCy](#open-source-packages)´s NLP package. These vectors are based on Levy and Goldberg (2014) which involves a specific  implementation of the [word2vec](#methods) model. The approach also makes use of [Tf-Idf](#methods) vectors, i.e. a method for extracting keywords from a document.

First, we tried two unsupervised approaches for extracting topics have been tested. Both of these approaches involve the use of word embeddings (i.e. vector representation of words based on their surrounding words). 

The first approach relies on the word embeddings called "en_core_web_lg" which can be downloaded as part of spaCy´s NLP package. These vectors are based on Levy and Goldberg (2014) which departs from a skip-gram implementation of word2vec. The approach also makes use of Tf-Idf vectors (term frequency–inverse document frequency) which is a method for extracting keywords from a document.

The prodecure is as follows:

- For each evaluation we extract the keywords using the Tf-Idf algorithm.
- For each topic we manually create a list of 10 synonyms to the topic.
- We compute a similarity score between each topic synonym and each keyword for a each evaluation.
- We match each evaluation to the topic which had the highest average similarity score.
- If two topics had very similar average scores. We computed assumed the evaluation cover more than one topic.

The second approach relies on the use of pretrained sentence-transformers from a spaCy extension package. This package wraps sentence-transformers (also known as sentence-BERT) directly in spaCy (see Reimers and Gurevych, 2019). The intention of this algorithm is that when the similarity of the pair of sentence embeddings is computed, it should represent accurately the semantic similarity of the two sentences. This differs from standard measures of sentence similarity where similarities are computed by simply averaging the similarity among the different words in a sentence. Using the spaCy - sentence-transformers we calculated the sentence similarity between the evaluation titles and brief topic description.

The prodecure is as follows:

- First calculate the sentence embeddings for evaluation titles using spaCy - sentence-transformers.
- Second compute the similarity between these embeddings and the topic despriptions.
- We match each evaluation to the topic which had the highest average similarity score.
- If two topics had very similar average scores. We computed assumed the evaluation cover more than one topic.

The third approach designed to estimate predictions to this question relied on an implementation of [zero-shot learning](#methods) using [Huggingface's transformers](#open-source-packages). This is an unsupervised machine learning approach which can be used to solve text classification problems when there is no training data available to train a model.

## Results 

The first approach performed the poorest. Compared to the LME-dataset the model predicted the correct topic in only 29 cases out of 126. 

The second approach performs the best and compared to the LME-dataset our model is able to correctly predict the topic in 42 out of 126 cases.

Given that in total there are 16 topics to choose from a random algorithm should be expected to make a correct around 13 correct predictions. 

Hence, our first algorithm performs more than twice as good as random guess and the second algorithm more than three times as good. The results are in our opinion however not sufficiently good to replace a manual process.

The third approach, relying on zero-shot learning, had the highest accuracy scores and performed best. By using the pre-trained zero-shot learning algorithm we managed to make predictions corresponding to the LME-dataset in 55 out of a total of 126 (~44%).

The third approach can be executed in the file `zero_shot.py`.
## Caveats

With more time and experimentation the results would likely improve. However, a major caveat to this problem is the fact that there are so many topics and that they tend to be semantically very similar. For example topics such as democracy and human rights often appear in similar contexts and hence tend to lie close in vector space. This creates a challenge for these type of algorithms that tend to work better when distinguishing topics that are semantically more distinct e.g. sports and politics.

Another issue was that when reviewing some of the findings in the EBA2017 dataset we did not agree with the results.