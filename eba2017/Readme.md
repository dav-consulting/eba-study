# Matching and parsing results from: Livslängd och livskraft: Vad säger utvärderingar om svenska biståndsinsatsers hållbarhet? (EBA 2017:12)

Contains methods for processing the results from EBA2017:12.

## Matching the reports analyzed in EBA 2017:12 to the SIDA evaluation database

All titles of reports analysed in the report EBA2017:12 are matched to the titles extracted from pdf's downloaded from: 

https://www.sida.se/English/publications/publicationsearch/

### Usage
Command line: directory: `[project_root]`
```
$ python -m eba2017.eba_match
```

## Parsing EBA 2017:12 analytical framework results
Analytical framework from EBA2017:12 used to derive:

`[project_root]` / original_data / eba2017_12.xslsx

needs to be parsed and placed in: 

`[project_root]` / processed_output.db ( table: eba2017 )

in order to make effiecient comparisons to a machine based algorithm of the same analysis.

### Usage
Command line: directory: `[project_root]`

```
$ python -m eba2017.eba_parse
```

## Caveats

The matching mechanism misses 2 evaluations present in EBA2017:12.

* Nr: 25 / Evaluation of the Raoul Wallenberg Institute’s regional programme “Building Human Rights Knowledge and Resources in the Middle East and North Africa”
* Nr: 99 / Evaluation of Save the Children’s Child Rights Governance and Protection Projects in Tanzania – Zanzibar project

These evaluations were however not to be found in the SIDA database search at https://www.sida.se/English/publications/publicationsearch/

