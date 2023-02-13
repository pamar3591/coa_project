#!/bin/sh

 #remove all ._ files (if any) created by MAC
 #dot_clean -m $1

# # create the directory structure; $1 indicates project folder location from commandline
#python3 make_dirs.py $1

# # merge ideology data with FJC
#python3 merge_ideology.py $1

# # splits the data in raw-caselaw into year-wise JSON files
# # separate json file for each year in directory /output_dir/Data/yearData
#python3 merge-fjc-judges/splitJsonFiles.py $1

# # merge caselaw data with judge data for all judges on panel
#python3 merge-fjc-judges/dataPrep.py $1

# creates a separate row for each opinion given by judge
#python3 merge-fjc-judges/split_csv.py $1

# matches opinion author to correct index on judge panel
#python3 merge-fjc-judges/match_opinion_judges.py $1

# merge IDB, citations, pagerank data
#python3 merge-fjc-judges/merge_data.py $1

# creating main variables from the data
#python3 merge-fjc-judges/add_variables.py $1

# filter required variables from the data
python3 merge-fjc-judges/filter.py $1
