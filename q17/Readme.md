# Is the contribution (and/or its results) deemed to be sustainable?

## Methods

Two approaches for answering this question was tested.

The first approach relies on extracting the overall sentiment of sentences mentioning the word sustainability. This was accomplished in two steps:

1) Preprocess (`prepare_training_data.py`):  All sentences mentioning sustainability, sustainable or similar are extracted and stored in the results / data / sustaianbility folder after filtering out non ascii characters.
2) Process (`main.py`): The sentences in step 1) are evaluated based on their sentiment. This is done using a pretrained pipeline from the 
Hugginface´s transformers package (https://github.com/huggingface/transformers). The package provides sentiments as a score in the range 0-1 with labels POSITIVE or NEGATIVE. For example, the sentence "The project was not sustainble." recieves a score of 0.9997933 and the label NEGATIVE.

The idea is thus to divide the evaluations into one of the four categories of EBA2017:12 (Sustainable, Unsustainable, Partially sustainable, Not avaliable). The threshold was set at 0.9 for a positive or negative result and below 0.75 was assumed to indicate "not available". If succesful this approach could then easily be applied to any DAC criteria.

The second approach relied on the use of a more advanced method for developing a an assessment model. This approach assumes the availability of training data to build a model based on a previous manual assessment of what the evaluation has concluded regarding sustainability. For this we relied on the EBA2017:12 sustainability assessments. In total there were 126 assessments of what the evaluation has concluded regarding sustainability. From these we relied on 99 evaluations to for training a model. The remaining 27 evaluations were then used to assess the performance of the trained model. To accomplish this we have relied on methods for text classification found in the spaCy transformers package (https://spacy.io/universe/project/spacy-transformers). In this package we made use of a pretrained state-of-the-art transformer architecture, known as BERT. The BERT model is a bidirectional transformer pretrained using a combination of masked language modeling objective and next sentence prediction on a large corpus comprising the Toronto Book Corpus and Wikipedia (see Devlin et.al 2018).

The training process is prepared in the file `prepare_training_data.py`.
The training process is executed in the file `train_category.py`.
The evaluation process is done in the file `evaluate_training.py`.


## Results

The results from the first approach resulted in a quite poor outcome, with a prediction corresponding to EBA2017:12 in 41 out of the 126 evaluations. This is just slightly better than a random guess which would produce on average 32 correct guesses. Based on our own manual assessment of an excerpt of the extracted passages on sustainability we have concluded that this is likely due to the rather involved and subtle language present in most evaluation. By this we mean that evaluators tend to refrain from the use of strong statemnts such as "the project was not sustaianble" and instead typically use language such as "... challenges towards the sustainabilty of the project". This explains why a sentiment approach to classification performs badly.

To evaluate whether the state-of-the-art language models for text classification could perform better, our second approach was an attempt to train such a model using the results found in EBA2017:12. In total, EBA2017:12 provided us with 126 assessments of sustainability. Typically this is regarded as an extremely small dataset in the NLP community and our hopes for training an accurate model was miniscule. To our surprise this model performed significantly better.

In our evaluation dataset, consisting of 27 out of the 126 evaluation our model was on average able to correctly predict 11 out 27. This is slightly above 50% correct predictions and although not likely to be sufficiently high to be useful still provides hope that this approach has potential if more time is spent on tweaking the model parameters and also extending the size of the training dataset.


## Caveats

The main caveats associated with this question concerns the reliability of the training data. A manual assessment of the EBA2017:12 assessment of sustainability revealed that it is quite difficult to make this judgement and that in a few cases we even felt that we even disagreed with the authors conclusions. 

Examples:

* Nr: 21 / Evaluation of Promoting the Integrity of Civil Data in Georgia

of EBA2017:12. The assessment is: Insatsen bedöms vara hållbar 

However, the evaluation only mentions the DAC criteria sustainability in one passage:

"The sustainability of results will be discussed under questions Nos. 5 and 6."

Later on page 31 the evaluators conclude:

"The MTR Team finds the probability high that the benefits of the project will continue after project completion. "

These type of separations are particularly difficult for our sentiment algorithm to cature.


* 2012:34

p.31: "In the light of this, the sustainability of the outputs already achieved by the budget
reform component cannot be taken for granted after the project ends."

p.5. . "For these outputs to become operational, orders from the senior management of the Ministry of Finance are
needed; the lack of written authorisation to use the products raises questions as to the
sustainability of these outputs."

## References

Devlin, J., Chang, M.W., Lee, K. and Toutanova, K., 2018. Bert: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805.