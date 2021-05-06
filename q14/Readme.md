# At what phase of the contribution is the evaluation being conducted?

## Methods

The approach taken for question 14 from the LME-dataset is a simple rules-based approach, which relies on extracting specific text passages from the processed evaluations. The focus lies on identifying the time period that is being evaluated and to extract the publication date of the report for validation check. The latter of the two are done in the downloaded evaluations (i.e. PDF documents) further described under the readme file for q0. The text patterns we search for are variations of "mid-term" and "end-of-phase". The search is limited to the evaluation title, executive summary and terms of reference.

The method starts out with the text search as described 

The initial analytical process entail the parsing and tokenization of the raw documents or evaluations (as described under Readme files for nlp_procssing, and parse_evaluations). If a specific string such as "Mid-Term" is found the developed method record and assume that the evaluation is conducted mid term. The method also conducts a validation exersice and checks if the evaluation report, given that it is a mid-term evaluation, is published within the time period in which the project or programme is being evaluated. If this logic is not met we assume that the evaluation was conducted during the end of the project and thus recorded as an end of phase evaluation.

## Results

The results match that of LME-dataset in 44 out of 58 cases. This equals 76% and is deemed to be a solid accuracy score for this question. When comparing these results to the initial set expectations for the difficult level (High) and confidence level (Fairly confident) the developed method has performed relatively well. 

## Caveats

The LME-dataset holds a couple of categories which we find difficult to distinguish ("Precis i slutet på el direkt efter finansierad period" and "Ett tag efter finansierad period"), which have effected and lowered the accuracy level for the developed method. The developed method could furthermore be improved with additional analytical steps taken. 