Start Terminal

Change the folder to project directory

Run: ./packages.sh

Then run the bash script on your system
Type: ./job.sh path_of_project_directory
Replace path_of_project_directory with path of the project directory on your system.


If ~/CoA_Project/ is your project directory, then directory structure should be the following:
- job.sh
- merge-fjc-judges <folder with scripts>
- make_dirs.py
- merge_ideology.py
- output_dir <starts empty>
- raw-caselaw <this has the raw caselaw data>
        - f-appx_text_20200604
        - f3d_text_20200604

- data-raw <raw data for merging etc>
        - ap08on.txt
        - ap71to07.txt
        - cited_from.csv.gz
        - cited_to.csv.gz
        - federal_judges_organized_by_judge.csv
        - judge_ideology.JCS.sav
        - pagerank_scores_renamed.csv

 
Please ensure that the raw data is stored in correct directory (as per the above structure). Also do not duplicate directories, for instance, the location of cited_from.csv.gz should be:

~/data-raw/cited_from.csv.gz and NOT ~/data-raw/data-raw/cited_from.csv.gz

Such mismatches will create errors.

The raw data was accessed from the sources below. It is also on file with Nina Varsava.

Caselaw Access Project (CAP) cases by reporter (retrieved April 21, 2022)
f-appx_text_20200604
f3d_text_20200604
Note that you need authorization from the Caselaw Access Project (CAP) to download the opinion data.
https://case.law/download/bulk_exports/20200604/by_reporter/case_text_restricted/

FJC’s Integrated Database (IDB) (retrieved Jan 27, 2022)
ap08on.txt
ap71to07.txt
https://www.fjc.gov/research/idb
- Appeals Data, Appellate Cases Cumulative File
- Cases terminated in FY 2008 through December 31, 2022 and cases pending as of December 31, 2022
- Cases terminated in SY 1971 through FY 2007

Citations graph (retrieved Oct 7, 2021)
cited_from.csv.gz
cited_to.csv.gz
https://case.law/download/citation_graph/2021-04-20/citations.csv.gz
https://case.law/download/citation_graph/2021-04-20/pagerank_scores.csv.gz

Pagerank data (retrieved Dec 7, 2021)
pagerank_scores_renamed.csv
https://case.law/download/citation_graph/2021-04-20/pagerank_scores.csv.gz

FJC judge data (retrieved Sep 29, 2021)
federal_judges_organized_by_judge.csv
https://www.fjc.gov/history/judges/biographical-directory-article-iii-federal-judges-export


Judicial Common Space scores (retrieved Oct 15, 2021)
judge_ideology_JCS.sav
http://epstein.wustl.edu/research/JCS.html
