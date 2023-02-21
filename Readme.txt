Start Terminal Change the folder to project directoryRun: ./packages.sh Then run the the bash script on your systemType: ./job.sh  path_of_project_directoryReplace path_of_project_directory with path of the project directory on your system.If ~/CoA_Project/ is your project directory, then directory structure should be the following: - job.sh- merge-fjc-judges <folder with scripts>- make_dirs.py- merge_ideology.py - output_dir - it is an empty while setting it up- raw-caselaw <this has the raw caselaw data> 	- f-appx_text_20200604	- f3d_text_20200604- data-raw <raw data for merging etc> 	- ap08on.txt	- ap71to07.txt	- cited_from.csv.gz	- cited_to.csv.gz	- federal_judges_organized_by_judge.csv	- judge_ideology.JCS.sav	- pagerank_scores_renamed.csv Th raw data is available on file with Nina Varsava. Below is the list of sources and other details for the raw data

1) f3d_text_20200604:- Retrieved on March 30, 2022, from
https://case.law/download/bulk_exports/20200604/by_reporter/case_text_restricted/f3d/

2) f3d_text_20200604:- Retrieved on March 30, 2022, from 
https://case.law/download/bulk_exports/20200604/by_reporter/case_text_restricted/f-appx/

3) ap08on.txt, ap71to07.txt:- Federal Judicial Center’s Integrated
Database from https://www.fjc.gov/research/idb

4) For a description of the PageRank scores, see Data Specifications, CASELAW ACCESS PROJECT,
https://case.law/docs/specs_and_reference/data_formats

5) federal_judges_organized_by_judge.csv:- Biographical Directory of Article III Federal Judges, 1789–present,from https://www.fjc.gov/history/judges



Please ensure that the raw data is stored in correct directory (as per the above structure). Also do not duplicate directories, for instance, the location of cited_from.csv.gz should be: ~/data-raw/cited_from.csv.gz and NOT ~/data-raw/data-raw/cited_from.csv.gz Such mismatches will create errors. 