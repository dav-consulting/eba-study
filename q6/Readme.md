# Extract evaluation time period

## Methods

The approach taken is a simple rules-based method. For each evaluation we search for sentences containing years between 1980 and 2020. For each sentence we search for pair of years lying close to each other. An example would be a sentence such as "The four-year programme (2011-2015) seeks to complement ...". By calculating the frequencies of occurencies for such pairs of years we draw conclusions as to which intervall is most likely to be correct.

## Results

The approach matches the time intervall in LME-dataset in 36 out of the 58 observations found. This equals 63% and is considered to be relatively fair accuracy score for this question. When comparing these results to the initial set expectations for the difficult level (High) and confidence level (Fairly confident) the developed method has performed relatively well.


## Caveats

There are examples of results in the EBA2017 dataset where we disagree with the reported time intervall. 

* 2014:45_15482 we found that the correct intervall should be 2013-2019 but in LME-dataset  the intervall 2010-2019 is reported.
* 2014:26 the evaluation executive summary states that: "This is an evaluation of the ICT in Teachers’Colleges project implemented from 2005 to 2008..." but in LME-dataset the period 2005-2014 is reported.
