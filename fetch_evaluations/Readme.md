
# Fetch evaluations from www.sida.se

Scrapy spider that collects meta data and the evaluations per se from Sida's online documentation archive `https://www.sida.se/English/publications/publicationsearch/`.
The spider is designed to scrape data based on a filter that is pre-made on the Sida's domain.
This filter and the amount of hits to fetch is dictated through the initial web address in the varible "start_urls".

# SUMMARY
Scrapy spider that collects meta data and the evaluations per se from Sida's online documentation archive (@ www.sida.se).
The spider is designed to scrape data based on a filter that is pre-made on the Sida's domain.
This filter and the amount of hits to fetch is dictated through the initial web address in the varible "start_urls".
   
The actual data collection utilises the XML-structure on Sidas web domain to design an approach 
that has collected data on: title, publication data, serier, series_number, language, issued,
authors, description, documentation url, and the pdf documents per se. 

The collected data has been parsed and stored in a SQL database for further analytical usage. 
    
Note that the returned data from the spider conatins various data types, such as strings, tuples, lists
and pdf-documents.

# CAVEATS
* The structure of Sidas web domain seem to have been altered (and made more robust in 2012) which poses 
    challenges for some aspects of the meta data collection - available data varies for the relevant evaluations
     which will affect the possibility to conduct systematic assessments for some areas. 
* Duplicates of domains for the same evaluations have been observed. Even though this does not affect the
     data collection if bear mark of flaws in the architecture of web domain.
* Sida's web domain do now allow data collection from third parties other than bots from larger web companies
     (based on their "https://www.sida.se/robots.txt"). This limits the possibility to utilise data sciences approaches.
     This collection have been bade in a supervised manner and has thus complied with the restrictions.
     However, the restriction will continue to have implications for applying data science approaches

# HUMAN- vs. COMPUTER APPROACH 
The structure of the web domain needed to be analysed throughly in order to understand to to build the web spider.
This task is easy for a human - gets intuition by seeing the web page structure and can make inferences of its functions
by the mere sight and review of it. The machine apporach need a deeper understanding of the underlying structure of HTML,
CSS, XML and JS in order to retrieve the accurate data.
In this light the human approach is faster and easier for understanding and using the system one-off. However,
the machine approach, once set up, is extremely fast and will fetch the data within seconds. MORE ONE THE BENEFITS. 
---

OBS  SKRIV OM ATT DET OBSERVERATS OPÅLITILG DATA  - STAVFEL ETC. SOM GÖR DET SVÅRT ATT VET ATT VI HAR RÄTT DOKUMENT. 
Se exempel i fuzz_output_examples on_challenges.xlsx. Dvs där det är svårt för datorn att avgöra med säkerhet. 
---
## Usage

Command line: directory: [project_root] / fetch_evaluations
$ scrapy crawl fetch_eval