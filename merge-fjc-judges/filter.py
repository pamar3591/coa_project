# filters required rows from final dataset

import pandas as pd
import os
import sys
import math
from collections import Counter

# keep only rows where an opinion is present
def check_per_curiam(a):
    a = a.lower()
    if 'per curiam' in a or "pe r curiam" in a or "per curlam" in a or "by the court" in a or "pur curiam" in a or "percuriam" in a.replace(" ","") or "by the panel" in a or "memorandum and order" in a or "pee curiam" in a or "er curiam" in a or "per ctjriam" in a:
        return(True)
    if len(a)<15 and ("per cur" in a or "per curiam" in a): # for cases like 'per curiafd' or 'per curium' other variants:
        return(True)
    return(False)

def calculate_male_judges(val):
    val = val.replace('[','').replace(']','').replace('\'','').replace(' ','').split(',')
    d = Counter(val)
    return(d['0'])

def calculate_white_judges(val):
    val = val.replace('[','').replace(']','').replace('\'','').replace(' ','').split(',')
    d = Counter(val)
    return(d['0'])

def isNaN(string):
    return string != string


# modify this for without author as well.
def check_pj_special_case_with_author(row):
    visiting_var = [row.get_visiting_judge, row.get_visiting_judge1, row.get_visiting_judge2]
    senior_var = [row.get_senior, row.get_senior1, row.get_senior2]
    req_index = float("NaN")
    # 2 visiting and 1 senior: senior judge is presiding
    if sum(visiting_var)==2 and sum(senior_var)==1:
        req_index = senior_var.index(1)

    # 2 senior + 1 visiting: senior with the longest tenure
    possible_longest_tenure_original = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    possible_longest_tenure = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    if sum(senior_var) == 2 and sum(visiting_var) == 1:
        index_of_visiting = visiting_var.index(1)
        possible_longest_tenure.pop(index_of_visiting)
        req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
    return(req_index)


def check_pj_special_case_without_author(row):
    visiting_var = [row.j1_visiting_judge, row.j2_visiting_judge, row.j3_visiting_judge]
    senior_var = [row.j1_senior, row.j2_senior, row.j3_senior]
    req_index = float("NaN")
    # 2 visiting and 1 senior: senior judge is presiding
    if sum(visiting_var)==2 and sum(senior_var)==1:
        req_index = senior_var.index(1)

    # 2 senior + 1 visiting: senior with the longest tenure
    possible_longest_tenure_original = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    possible_longest_tenure = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    if sum(senior_var) == 2 and sum(visiting_var) == 1:
        index_of_visiting = visiting_var.index(1)
        possible_longest_tenure.pop(index_of_visiting)
        req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
    return(req_index)


def all_three_senior_or_visiting_noauthor(row):
    possible_longest_tenure_original = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    possible_longest_tenure = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
    return(req_index)

def all_three_visiting_or_senior_with_author(row):
    possible_longest_tenure_original = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    possible_longest_tenure = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
    return(req_index)

def all_three_mixed_with_author_final(row):
    # if all three are visiting or senior:
    # first exclude visiting status judges
    possible_longest_tenure_original = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    possible_longest_tenure = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    if row.get_senior == 1:
        possible_longest_tenure.remove(row.get_tenure)
    if row.get_senior1 == 1:
        possible_longest_tenure.remove(row.get_tenure1)
    if row.get_senior2 == 1:
        possible_longest_tenure.remove(row.get_tenure2)
    if possible_longest_tenure == []:
        return(float("NaN"))
    else:
        req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
    return(req_index)

def all_three_mixed_with_author(row):
    # if all three are visiting or senior:
    # first exclude visiting status judges
    possible_longest_tenure_original = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    possible_longest_tenure = [row.get_tenure, row.get_tenure1, row.get_tenure2]
    if row.get_visiting_judge == 1:
        possible_longest_tenure.remove(row.get_tenure)
    if row.get_visiting_judge1 == 1:
        possible_longest_tenure.remove(row.get_tenure1)
    if row.get_visiting_judge2 == 1:
        possible_longest_tenure.remove(row.get_tenure2)
    if possible_longest_tenure == []:
        return(float("NaN"))
    else:
        req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))

    return(req_index)

def all_three_mixed_noauthor_final(row):
    # if all three are visiting or senior:
    # first exclude visiting status judges
    possible_longest_tenure_original = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    possible_longest_tenure = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    if row.j1_senior == 1:
        possible_longest_tenure.remove(row.j1_tenure)
    if row.j2_senior == 1:
        possible_longest_tenure.remove(row.j2_tenure)
    if row.j3_senior == 1:
        possible_longest_tenure.remove(row.j3_tenure)
    if possible_longest_tenure == []:
        return(float("NaN"))
    else:
        req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
    return(req_index)

def all_three_mixed_noauthor(row):
    # if all three are visiting or senior:
    # first exclude visiting status judges
    possible_longest_tenure_original = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    possible_longest_tenure = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
    if row.j1_visiting_judge == 1:
        possible_longest_tenure.remove(row.j1_tenure)
    if row.j2_visiting_judge == 1:
        possible_longest_tenure.remove(row.j2_tenure)
    if row.j3_visiting_judge == 1:
        possible_longest_tenure.remove(row.j3_tenure)
    if possible_longest_tenure == []:
        return(float("NaN"))
    else:
        req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
    return(req_index)

def determine_presiding_judge(row,ret_val):
    # check with or without author

    author_pj = 0
    normal_case = 0
    author_absent = isNaN(row.author_fullname)
    req_index, author_index = '',''
    if author_absent == True:
        j1_index = 0
        j2_index = 1
        j3_index = 2
        possible_judge_names = [row.judge_names.split(',')[0].strip(), row.judge_names.split(',')[1].strip(),
                                row.judge_names.split(',')[2].strip()]
        # the following pattern for checking chief judge (which goes in the order in which the names are present in the judge names list)
        # also works for the 3 exceptions: filenames: 11092911, 4322479
        # for these three rows the first judge identified as the chief judge is the correct one
        # this has been confirmed by using publicly available dates for chief judge status:
        # edwards harry: September 19, 1994 – July 16, 2001
        # ginsburg douglas: July 16, 2001 – February 11, 2008
        # traxler William: July 8, 2009 – July 8, 2016
        # gregory roger: July 8, 2016 –
        if row.j1_chief == 1.0:
            case_pj = possible_judge_names[j1_index]
            req_index = j1_index
        elif row.j2_chief == 1.0:
            case_pj = possible_judge_names[j2_index]
            req_index = j2_index
        elif row.j3_chief == 1.0:
            case_pj = possible_judge_names[j3_index]
            req_index = j3_index
        else:
            possible_longest_tenure_original = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
            possible_longest_tenure = [row.j1_tenure, row.j2_tenure, row.j3_tenure]
            if row.j1_senior == 1 or row.j1_visiting_judge== 1:
                possible_longest_tenure.remove(row.j1_tenure)
            if row.j2_senior == 1 or row.j2_visiting_judge== 1:
                possible_longest_tenure.remove(row.j2_tenure)
            if row.j3_senior == 1 or row.j3_visiting_judge== 1:
                possible_longest_tenure.remove(row.j3_tenure)
            if possible_longest_tenure==[]:

                req_index = check_pj_special_case_without_author(row)
                if not(math.isnan(req_index)):
                    case_pj = row.judge_names.split(',')[req_index].strip()
                else:
                    # determine if it is all or mixed
                    visiting_vals = [row.j1_visiting_judge, row.j2_visiting_judge,row.j3_visiting_judge]
                    senior_vals = [row.j1_senior, row.j2_senior,row.j3_senior]
                    if (sum(visiting_vals)==3 and sum(senior_vals)==0) or (sum(visiting_vals)==0 and sum(senior_vals)==3):
                        req_index = all_three_senior_or_visiting_noauthor(row)
                        normal_case = 1
                    else:
                        req_index = all_three_mixed_noauthor(row)
                    if not (math.isnan(req_index)):
                        case_pj = row.judge_names.split(',')[req_index].strip()
                    else:
                        req_index = all_three_mixed_noauthor_final(row)
                        if not (math.isnan(req_index)):
                            case_pj = row.judge_names.split(',')[req_index].strip()
                        else:
                            case_pj = float("NaN")
            else:
                req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
                case_pj = row.judge_names.split(',')[req_index].strip()

    if author_absent == False:

        # check if chief judge is on panel
        # author is chief judge
        author_index = int(row['index'])
        j1_index = [0,1]
        if author_index in j1_index: j1_index.remove(author_index)
        j1_index = j1_index[0]
        j2_index = [0,1,2]
        j2_index.remove(author_index)
        j2_index.remove(j1_index)
        j2_index = j2_index[0]

        possible_judge_names = [row.judge_names.split(',')[0].strip(), row.judge_names.split(',')[1].strip(), row.judge_names.split(',')[2].strip()]
        if row.get_chief == 1.0:
            case_pj = possible_judge_names[author_index]
            req_index = author_index
        elif row.get_chief1 == 1.0:
            case_pj = possible_judge_names[j1_index]
            req_index = j1_index
        elif row.get_chief2 == 1.0:
            case_pj = possible_judge_names[j2_index]
            req_index = j2_index
        else:
            possible_longest_tenure_original = [row.get_tenure, row.get_tenure1, row.get_tenure2]
            possible_longest_tenure = [row.get_tenure, row.get_tenure1, row.get_tenure2]
            if row.get_senior == 1 or row.get_visiting_judge == 1:
                possible_longest_tenure.remove(row.get_tenure)
            if row.get_senior1 == 1 or row.get_visiting_judge1 == 1:
                possible_longest_tenure.remove(row.get_tenure1)
            if row.get_senior2 == 1 or row.get_visiting_judge2 == 1:
                possible_longest_tenure.remove(row.get_tenure2)

            if possible_longest_tenure==[]:
                req_index = check_pj_special_case_with_author(row)
                if not(math.isnan(req_index)):
                    case_pj = row.judge_names.split(',')[req_index].strip()

                else:
                    # determine if it is all or mixed
                    visiting_vals = [row.get_visiting_judge, row.get_visiting_judge1, row.get_visiting_judge2]
                    senior_vals = [row.get_senior, row.get_senior1, row.get_senior2]
                    if (sum(visiting_vals)==3 and sum(senior_vals)==0) or (sum(visiting_vals)==0 and sum(senior_vals)==3):
                        req_index = all_three_visiting_or_senior_with_author(row)
                        normal_case = 1
                    else:
                        req_index = all_three_mixed_with_author(row)
                    if not (math.isnan(req_index)):
                        case_pj = row.judge_names.split(',')[req_index].strip()
                    else:
                        req_index = all_three_mixed_with_author_final(row)
                        if not (math.isnan(req_index)):
                            case_pj = row.judge_names.split(',')[req_index].strip()
                        else:
                            case_pj = float("NaN")
            else:
                req_index = possible_longest_tenure_original.index(max(possible_longest_tenure))
                case_pj = row.judge_names.split(',')[req_index].strip()

    if str(req_index) == str(row['index']):
        author_pj = 1
    elif row['index']=='None' or row['index']=='per_curiam_in_opinion_name' or row['index']=='not_found':
        author_pj = float("NaN")

    if ret_val == "case_pj":
        return(case_pj)
    elif ret_val == "case_pj_type":
        return(normal_case)
    else:
        return(author_pj)




if __name__ == "__main__":
    working_dir = os.path.join(sys.argv[1], 'output_dir')
    check_header = True
    all_files = os.listdir(working_dir + '/final_add')
    for f in all_files:
        file = pd.read_csv(working_dir + '/final_add/'+f)

        file['n_men'] = file.apply(lambda x: calculate_male_judges(x.judge_gender_list), axis=1)
        file['n_white'] = file.apply(lambda x: calculate_white_judges(x.judge_races_list), axis=1)

        # create presiding judge variable
        file['case_pj'] = file.apply(lambda x: determine_presiding_judge(x,"case_pj"), axis=1)
        file['author_pj'] = file.apply(lambda x: determine_presiding_judge(x, "author_pj"), axis=1)


        # keep required columns
        columns_keep = ['filename','caseTitle',
                        'circuitNum','judge_names','us_party','corp_party','opinion_author_split','type_split','reporter', # CHANGE THIS TO THE OPINION LEVEL
                        'docket_number','decision_date','citations','all_judges',
                        'cited_from','cites_to','case_index','raw_score','percentile','case_docketnum_nor','case_decision_date_nor','csl_id',
                        'CIRCUIT','DOCKET','USAPT','USAPE','PUBSTAT','PROSEFLE','PROSETRM','ENBANC','IDB_ID', 'APPTYPE','NOS',
                        'year_decision','topics_clean',
                        'has_concurrence',
                        'has_dissent', 'get_publication_type', 'published_caselaw','get_dist_judge',
                        'get_visiting_judge', 'get_tenure', 'get_elite', 'get_gender',
                        'get_race', 'get_specific_race','get_party', 'get_age', 'get_opinion_length', 'get_chief',
                        'get_senior', 'get_ideology',
                        'get_dist_judge1', 'get_visiting_judge1', 'get_tenure1','get_elite1', 'get_gender1', 'get_race1', 'get_specific_race1','get_party1', 'get_age1',
                        'get_chief1', 'get_senior1', 'get_ideology1',
                        'get_dist_judge2','get_visiting_judge2', 'get_tenure2', 'get_elite2', 'get_gender2',
                        'get_race2', 'get_specific_race2', 'get_party2', 'get_age2', 'get_chief2','get_senior2','get_ideology2','author_fullname',
                        'n_men','n_white','case_pj','author_pj',
                        'get_judge1_fn', 'get_judge2_fn',

                        # additional judge variables (for rows without an author
                        'j1_fullname', 'j1_dist_judge', 'j1_visiting_judge', 'j1_tenure', 'j1_elite',
                        'j1_gender', 'j1_race', 'j1_specific_race', 'j1_party', 'j1_age', 'j1_chief',
                        'j1_senior', 'j1_ideology',
                        'j2_fullname', 'j2_dist_judge', 'j2_visiting_judge', 'j2_tenure', 'j2_elite',
                        'j2_gender', 'j2_race', 'j2_specific_race', 'j2_party', 'j2_age', 'j2_chief',
                        'j2_senior', 'j2_ideology',
                        'j3_fullname', 'j3_dist_judge', 'j3_visiting_judge', 'j3_tenure', 'j3_elite',
                        'j3_gender', 'j3_race', 'j3_specific_race', 'j3_party', 'j3_age', 'j3_chief',
                        'j3_senior', 'j3_ideology'
                        ]


        file_keep = file[columns_keep]

        # replace author column names
        file_keep.rename(columns={'get_dist_judge': 'author_dist_judge', 'get_visiting_judge': 'author_visiting_judge',
                                  'get_tenure': 'author_tenure', 'get_elite': 'author_elite', 'get_gender': 'author_gender',
                                  'get_race': 'author_race', 'get_party': 'author_party', 'get_age': 'author_age',
                                   'get_chief': 'author_chief', 'get_senior': 'author_senior',
                                  'get_ideology':'author_ideology','get_opinion_length':'opinion_length','get_specific_race':'author_specific_race'},
                         inplace=True)

        # replace judge1 column names
        file_keep.rename(columns={'get_judge1_fn': 'judge1_fullname','get_dist_judge1': 'judge1_dist_judge', 'get_visiting_judge1': 'judge1_visiting_judge',
                                  'get_tenure1': 'judge1_tenure', 'get_elite1': 'judge1_elite',
                                  'get_gender1': 'judge1_gender', 'get_race1': 'judge1_race', 'get_party1': 'judge1_party',
                                  'get_age1': 'judge1_age', 'get_chief1': 'judge1_chief',
                                  'get_senior1': 'judge1_senior','get_ideology1':'judge1_ideology','get_specific_race1':'judge1_specific_race'}, inplace=True)

        # replace judge2 column names
        file_keep.rename(columns={'get_judge2_fn': 'judge2_fullname', 'get_dist_judge2': 'judge2_dist_judge', 'get_visiting_judge2': 'judge2_visiting_judge',
                                  'get_tenure2': 'judge2_tenure', 'get_elite2': 'judge2_elite',
                                  'get_gender2': 'judge2_gender', 'get_race2': 'judge2_race', 'get_party2': 'judge2_party',
                                  'get_age2': 'judge2_age', 'get_chief2': 'judge2_chief',
                                  'get_senior2': 'judge2_senior','get_ideology2':'judge2_ideology','get_specific_race2':'judge2_specific_race'}, inplace=True)

        file_keep.rename(columns={'opinion_author_split': "opinion_author_name", "type_split": "opinion_type"}, inplace = True)

        # changing final names according to NV's suggestions
        file_keep.rename(columns={'caseTitle':'case_name',
                                  'opinion_author_name':'author',
                                  'docket_number':'docket_num',
                                  'panel_ideology':'judge_ideology_list',
                                  'raw_score':'pagerank_rawscore',
                                  'percentile':'pagerank_percentile',
                                  'dockernum_nor':'docket_num_nor',
                                  'case_decision_date_nor':'case_date_nor',
                                  'topics_clean':'topic',
                                  'has_concurrence':'case_has_concurrence',
                                  'has_dissent':'case_has_dissent',
                                  'get_publication_type':'published',
                                  'author_dist_judge':'author_district',
                                  'author_visiting_judge':'author_visiting',
                                  'judge1_dist_judge':'judge1_district',
                                  'judge1_visiting_judge':'judge1_visiting',
                                  'judge2_dist_judge': 'judge2_district',
                                  'judge2_visiting_judge': 'judge2_visiting',
                                  'decision_date':'case_date',
                                  'year_decision':'case_year',
                                  'circuitNum':'court',
                                  'csl_id':'caselaw_idb_merge_id'
                                  },

                         inplace=True)
        file_keep.loc[:,'author_elite'] = file_keep['author_elite'].map({True: 1, False: 0})
        file_keep.loc[:,'judge1_elite'] = file_keep['judge1_elite'].map({True: 1, False: 0})
        file_keep.loc[:,'judge2_elite'] = file_keep['judge2_elite'].map({True: 1, False: 0})
        file_keep.loc[:,'us_party'] = file_keep['us_party'].map({True: 1, False: 0})
        file_keep.loc[:,'corp_party'] = file_keep['corp_party'].map({True: 1, False: 0})


        file_keep.to_csv(working_dir + '/filter/' + f, index=False)
        # Combine all CSVs that are written out
        file_keep.to_csv(working_dir + '/filter/'+'combined.csv',index=False, mode = 'a', header=check_header)
        check_header = False
