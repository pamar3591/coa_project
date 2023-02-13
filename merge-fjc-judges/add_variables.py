# adds additional variables that are required for analysis
# replaces files with the added variables

import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import itertools
import sys


def get_list(var,opinion_index):
    return(var.replace('[', '').replace(']', '').replace('\'', '').split(',')[opinion_index].strip())

def get_list_from_str(var):
    return (var.replace('[', '').replace(']', '').replace('\'', '').split(','))


def which_corresponding_data(row,opinion_index):
    decision_date = datetime.strptime(row['decision_date'], '%Y-%m-%d')
    # make a list of commission dates for index
    commission_dates = []
    for i in range(1,7):
        var_name = "commission_date" + str(i)
        # convert to date format or append ""
        try:
            cdate = datetime.strptime(get_list(row[var_name.format()], opinion_index).replace(" ",""), '%Y-%m-%d')
        except:
            cdate = ""
        commission_dates.append(cdate)

    # get indices of list vars which do not have values
    indices = [i for i, x in enumerate(commission_dates) if x == ""]
    indices_filled = [x for x in range(0,6) if x not in indices]
    return(get_return_index(indices_filled,decision_date,commission_dates))

def get_return_index(indices_filled,decision_date,commission_dates):
    if(len(indices_filled)==1 and indices_filled[0]==0):
        return(1)
    else:
        # loop over all indices in list and compare dates
        for i in range(0, len(indices_filled)):
            if i == len(indices_filled)-1:
                return(indices_filled[i]+1)
            else:
                # decision date should be within commission date range
                if decision_date >= commission_dates[indices_filled[i]] and decision_date < commission_dates[indices_filled[i-1]]:
                    return(indices_filled[i]+1)


def check_district_judge(row,opinion_index):
    dec_date = datetime.strptime(row['decision_date'], '%Y-%m-%d')
    court_vals = []
    commission_date_vals = []
    for i in range(1, 7):
        cname = 'court_name' + str(i)
        court_vals.append(get_list(row[cname.format()], opinion_index).replace("U.S.", "United States"))
        cdate = 'commission_date' + str(i)
        commission_date_vals.append(get_list(row[cdate.format()], opinion_index).replace("U.S.", "United States"))
    # check_positions_in_order(commission_date_vals)
    commission_date_vals_keep = []
    courts_keep = []
    index_keep = [idx for idx, s in enumerate(court_vals) if s != '']
    for i in index_keep:
        # added this condition to remove cases wherein commission dates are after the date of decision
        try:
            cdate = datetime.strptime(commission_date_vals[i].strip(), '%Y-%m-%d')
            if cdate <= dec_date:  # this condition will ensure that the tenure of a visiting judge is 0
                commission_date_vals_keep.append(commission_date_vals[i])
                courts_keep.append(court_vals[i])
        except:
            continue


    # now we just take the most recent one: this will be the last element in the list

    try:
        check_court = courts_keep[-1] # sometimes, the date of decision is BEFORE the commission date so this creates an issue
        # these are errors and thus "NA" is returned here.
        if "District Court" in check_court:
            return 1
        else:
            return 0
    except:
        return(float("NaN")) # only if there are no VALID dates of judge commission date

def check_visiting_judge(row, opinion_index, court_name):
    dec_date = datetime.strptime(row['decision_date'], '%Y-%m-%d')
    court_vals = []
    commission_date_vals = []
    for i in range(1, 7):
        cname = 'court_name' + str(i)
        court_vals.append(get_list(row[cname.format()], opinion_index).replace("U.S.", "United States"))
        cdate = 'commission_date' + str(i)
        commission_date_vals.append(get_list(row[cdate.format()], opinion_index).replace("U.S.", "United States"))
    # check_positions_in_order(commission_date_vals)
    commission_date_vals_keep = []
    courts_keep = []
    index_keep = [idx for idx, s in enumerate(court_vals) if s!='']
    for i in index_keep:
        # added this condition to remove cases wherein commission dates are after the date of decision
        try:
            cdate = datetime.strptime(commission_date_vals[i].strip(), '%Y-%m-%d')
            if cdate <= dec_date:  # this condition will ensure that the tenure of a visiting judge is 0
                commission_date_vals_keep.append(commission_date_vals[i])
                courts_keep.append(court_vals[i])
        except:
            continue
    # now we just take the most recent one: this will be the last element in the list

    try:
        check_court = courts_keep[-1]

        opinion_court_name = check_court.replace("United States","U.S.")
        court_name = court_name.replace("United States","U.S.")
        if not(opinion_court_name==court_name):
            return(1)
        else:
            return(0)
    except:
        return(float("NaN")) # due to error: see the note in check_district_judge above 

def check_positions_in_order(commission_date_vals):
    commission_date_vals = [x.strip() for x in commission_date_vals]
    commission_date_vals = [x for x in commission_date_vals if x!='']
    for i in range(0, len(commission_date_vals)):
        if i == len(commission_date_vals)-1:
            break
        else:
            curr_date = datetime.strptime(commission_date_vals[i].strip(), '%Y-%m-%d')
            next_date = datetime.strptime(commission_date_vals[i+1].strip(), '%Y-%m-%d')
            if next_date < curr_date:
                print("Date Error found")


def tenure(row, opinion_index):
    # for all positions
    dec_date = datetime.strptime(row['decision_date'], '%Y-%m-%d')
    court_vals = []
    commission_date_vals = []
    for i in range(1,7):
        cname = 'court_name' + str(i)
        court_vals.append(get_list(row[cname.format()], opinion_index).replace("U.S.", "United States"))
        cdate = 'commission_date' + str(i)
        commission_date_vals.append(get_list(row[cdate.format()], opinion_index).replace("U.S.", "United States"))
    check_positions_in_order(commission_date_vals)
    #
    index_keep = [idx for idx, s in enumerate(court_vals) if 'Court of Appeals' in s]
    commission_date_vals_keep = []
    for i in index_keep:
        # added this condition to remove cases wherein commission dates are after the date of decision
        cdate = datetime.strptime(commission_date_vals[i].strip(), '%Y-%m-%d')
        if cdate <= dec_date: # this condition will ensure that the tenure of a visiting judge is 0
            commission_date_vals_keep.append(commission_date_vals[i])
    total_exp = 0
    for j in range(0, len(commission_date_vals_keep)):
        cdate = datetime.strptime(commission_date_vals_keep[j].strip(), '%Y-%m-%d')
        if j == (len(commission_date_vals_keep) - 1):
            total_exp = total_exp + relativedelta(dec_date,cdate).years + (relativedelta(dec_date,cdate).months/ 12)
        else:
            next_date = datetime.strptime(commission_date_vals_keep[j+1].strip(), '%Y-%m-%d')
            total_exp = total_exp + relativedelta(next_date, cdate).years + (relativedelta(next_date, cdate).months / 12)
    return(total_exp)

def generate_topics_from_apptype_topiccode(apptype,topic_code):
    # only 8 topics remain unclassified using this approach
    # classification adopted from Hinkle, 2021
    try:
        apptype = int(apptype)
    except:
        apptype = "NA"
    if topic_code == 510 or topic_code == 530 or topic_code == 535 or topic_code == 540:
        return("prisoner_petitions")
    elif topic_code == 440 or topic_code==441 or topic_code==442 or topic_code==443 or topic_code==444 or topic_code==550 or topic_code==555:
        return("civil_civil_rights")
    elif apptype == 1 or apptype == 2:
        return("administrative")
    elif apptype == 3 or apptype == 4:
        return ("civil")
    elif apptype == 10 or apptype == 11 or apptype == 12:
        return("bankruptcy")
    elif apptype == 6:
        return("original_jurisdiction")
    elif apptype == 13 or apptype == 14 or apptype == 15 or apptype == 16 or apptype == 17 or apptype == 18 or apptype == 19 or apptype == 20 or apptype == 21 or apptype == 22:
        return("criminal")
    elif topic_code == -9:
        return("NA")
    else:
        return('none')

def get_generic_vars(val, opinion_index):
    opinion_var = get_list(val, opinion_index).replace(" ","")
    if opinion_var == '1' or opinion_var == "TRUE":
        opinion_var = 1
    elif opinion_var == '0' or opinion_var == "FALSE":
        opinion_var = 0
    return(opinion_var)

def publication_type(val):
    # tot_str = "F.3d","F. 3d","F. App'x","F. App’x","Fed.Appx","F.App\'x","Fed. App\'x","Fed.App\'x"
    tot_str = ["F.3d", "F. 3d", "F. App'x", "F. App’x", "Fed.Appx", "F.App\'x", "Fed. App\'x", "Fed.App\'x"]
    # but this is just both conditions so not using tot_str
    pub = ["F.3d","F. 3d"]
    unpub = ["F. App\'x","F. App’x","Fed.Appx","F.App\'x","Fed. App\'x","Fed.App\'x"]
    detect_pub = [1 for x in pub if x in val]
    detect_unpub = [1 for x in unpub if x in val]
    if 1 in detect_pub:
        return(1)
    elif 1 in detect_unpub:
        return(0)
    else:
        return('NA')

def get_opinion_length(val):
    opinion_length = len(val.split(' '))
    return opinion_length

def publication_type_reporter(val):
    # tot_str = "F.3d","F. 3d","F. App'x","F. App’x","Fed.Appx","F.App\'x","Fed. App\'x","Fed.App\'x"
    # but this is just both conditions so not using tot_str
    pub = ["Series"]
    unpub = ["Appendix"]
    detect_pub = [1 for x in pub if x in val]
    detect_unpub = [1 for x in unpub if x in val]
    if 1 in detect_pub:
        return(1)
    elif 1 in detect_unpub:
        return(0)


def get_judge_age(val, opinion_index,dec_date):
    dec_date = datetime.strptime(dec_date, '%Y-%m-%d')
    judge_birth_year = datetime.strptime(get_list(val, opinion_index).strip(),"%Y")
    return(relativedelta(dec_date, judge_birth_year).years)

def get_case_type_concurrence(case_type_all):
    if "concurring" in case_type_all or 'concurrence' in case_type_all:
        return(1)
    return(0)

def get_case_type_dissent(case_type_all):
    if "dissenting" in case_type_all or 'dissent' in case_type_all:
        return(1)
    return(0)

def get_author_fullname(val, opinion_index):
    return_val = get_list(val, opinion_index)
    if return_val == '':
        return_val = float('NaN')
    return(return_val)

def is_chief_judge(row, opinion_index):
    # we need to check for all chief judge vars: 1 to 6
    dec_date = datetime.strptime(row['decision_date'], '%Y-%m-%d')
    chief_judge_start = []
    chief_judge_end = []
    for i in range(1, 7):
        for j in range(1,3):
            var_name_start = 'chief' + str(i) + str(j)
            var_name_end = 'chief' + str(i) + str(j) + "e"
            chief_judge_start.append(get_list(row[var_name_start.format()], opinion_index).strip())
            chief_judge_end.append(get_list(row[var_name_end.format()], opinion_index).strip())
    index_keep = [idx for idx, s in enumerate(chief_judge_start) if s !='']
    chief_judge_start_keep = []
    chief_judge_end_keep = []
    for i in index_keep:
        chief_judge_start_keep.append(chief_judge_start[i])
        if chief_judge_end[i] == "":
            chief_judge_end[i] = '2021.0'
        chief_judge_end_keep.append(chief_judge_end[i])

    for j in range(0, len(chief_judge_start_keep)):
        start_date = datetime.strptime(str(chief_judge_start_keep[j]).replace(".0","") + '-06-01', '%Y-%m-%d')
        end_date =datetime.strptime(str(chief_judge_end_keep[j]).replace(".0","") + '-06-01', '%Y-%m-%d')
        if start_date <= dec_date <= end_date:
            return(1)
    return(0)

def is_senior_judge(row, opinion_index):
    dec_date = datetime.strptime(row['decision_date'], '%Y-%m-%d')
    senior_judge = []
    for i in range(1, 7):
        var_name = 'senior' + str(i)
        senior_judge.append(get_list(row[var_name.format()], opinion_index).strip())
    index_keep = [idx for idx, s in enumerate(senior_judge) if s != '']
    senior_judge_keep = []

    for i in index_keep:
        senior_judge_keep.append(senior_judge[i])

    for j in range(0, len(senior_judge_keep)):
        start_date = datetime.strptime(str(senior_judge_keep[j]).strip(), '%Y-%m-%d')
        if start_date <= dec_date:
            return (1)
    return (0)

def get_additional_vars(file):
    new_vars_df = pd.DataFrame(columns=['author_fullname','get_dist_judge', 'get_visiting_judge', 'get_tenure', 'get_elite',
                                        'get_gender', 'get_race', 'get_specific_race','get_party', 'get_age', 'get_words', 'get_chief',
                                        'get_senior','get_ideology'])
    all_vars = []
    for i in range(0, len(file)):
        row = file.iloc[i]
        # get_dist_judge, get_visiting_judge, get_tenure, get_elite = float("NaN"),float("NaN"),float("NaN"), float("NaN")
        # get_gender, get_race, get_party, get_age, get_words, get_chief, get_senior = float("NaN"),float("NaN"),float("NaN"), float("NaN"),\
        #                                                                              float("NaN"),float("NaN"),float("NaN")
        try:
            get_index = int(file.iloc[i]['index'])
        except:
            append_list = [[float("NaN")] * 14] # null values by default if missing
            all_vars = all_vars + append_list
            continue
        if get_index!=0 and get_index!=1 and get_index!=2:
            append_list = [[float("NaN")] * 14]  # null values by default if missing
            all_vars = all_vars + append_list
            continue
        append_list = compute_vars(row, get_index)
        all_vars = all_vars + append_list
    df2 = pd.DataFrame(all_vars, columns=new_vars_df.columns)
    new_vars_df = pd.concat([new_vars_df, df2])
    # new_vars_df = new_vars_df.append(pd.DataFrame(all_vars, columns=new_vars_df.columns))
    return(new_vars_df)


def compute_vars(row,index):
    # get_dist_judge, get_visiting_judge, get_tenure, get_elite = [float("NaN")]*4
    # get_gender, get_race, get_party, get_age, get_words, get_chief, get_senior = [float("NaN")]*7

    var_req_index = which_corresponding_data(row, index)
    court_var = 'court_name' + str(var_req_index)
    get_dist_judge = check_district_judge(row, index)
    get_author_fn = get_author_fullname(row['all_judges'],index)
    get_visiting_judge = check_visiting_judge(row, index, row['court_name'])
    get_tenure = tenure(row, index)
    get_elite = get_generic_vars(row['judge_elite'], index)
    get_gender = get_generic_vars(row['judge_gender_list'], index)  # here 1 = female
    get_race = get_generic_vars(row['judge_races_list'], index)  # here 1 = ??
    get_specific_race = get_generic_vars(row['judge_races_fulltext'],index)
    get_party = get_generic_vars(row['judge_parties_list'], index)  # here 1 = ??
    get_age = get_judge_age(row['judge_birth_year'], index, row['decision_date'])
    get_words = len(row['text_split'].split(' '))
    get_chief = is_chief_judge(row, index)
    get_senior = is_senior_judge(row, index)
    get_ideology = get_generic_vars(row['panel_ideology'], index)
    append_list = [[get_author_fn,get_dist_judge, get_visiting_judge, get_tenure, get_elite,
                    get_gender, get_race, get_specific_race, get_party, get_age, get_words, get_chief, get_senior,get_ideology]]
    return(append_list)

def get_additional_vars_non_author(file):
    new_vars_df = pd.DataFrame(columns=['get_judge1_fn','get_dist_judge1', 'get_visiting_judge1', 'get_tenure1', 'get_elite1',
                                        'get_gender1', 'get_race1', 'get_specific_race1' , 'get_party1', 'get_age1', 'get_words1', 'get_chief1',
                                        'get_senior1', 'get_ideology1',
                                        'get_judge2_fn', 'get_dist_judge2', 'get_visiting_judge2', 'get_tenure2', 'get_elite2',
                                        'get_gender2', 'get_race2', 'get_specific_race2', 'get_party2', 'get_age2', 'get_words2',
                                        'get_chief2','get_senior2','get_ideology2'])
    all_vars = []
    for i in range(0, len(file)):
        row = file.iloc[i]
        # get_dist_judge1, get_visiting_judge1, get_tenure1, get_elite1 = [float("NaN")]*4
        # get_gender1, get_race1, get_party1, get_age1, get_words1, get_chief1, get_senior1 = [float("NaN")]*7
        # get_gender2, get_race2, get_party2, get_age2, get_words2, get_chief2, get_senior2 = [float("NaN")] * 7
        # get_dist_judge2, get_visiting_judge2, get_tenure2, get_elite2 = [float("NaN")] * 4
        try:
            get_index = int(file.iloc[i]['index'])
        except:
            # assuming we do not need data for the rows without an 'index' - check with prof
            append_list = [[float("NaN")] * 28] # missing values
            all_vars = all_vars + append_list
            # append all Null values to lists
            continue
        if get_index!=0 and get_index!=1 and get_index!=2:
            append_list = [[float("NaN")] * 28]  # null values by default if missing
            all_vars = all_vars + append_list
            continue
        judge_indices = list(range(0, len(get_list_from_str(row.judge_gender_list))))
        if get_index==0 or get_index==1 or get_index==2: # excluding '12' and other similar error index
            judge_indices.remove(get_index)

        append_list_of_lists = []
        for j in judge_indices:
            append_list = compute_vars(row, j)
            append_list_of_lists = append_list_of_lists + append_list

        all_vars = all_vars + [list(itertools.chain.from_iterable(append_list_of_lists))]
    df2 = pd.DataFrame(all_vars, columns=new_vars_df.columns)
    new_vars_df = pd.concat([new_vars_df, df2])
    # new_vars_df = new_vars_df.append(pd.DataFrame(all_vars, columns=new_vars_df.columns))
    return(new_vars_df)

def isNaN(string):
    return string != string

def add_new_variables(file):
    new_vars_df = pd.DataFrame(
        columns=['j1_fullname','j1_dist_judge', 'j1_visiting_judge', 'j1_tenure', 'j1_elite',
                'j1_gender', 'j1_race', 'j1_specific_race' , 'j1_party', 'j1_age','j1_words', 'j1_chief',
                'j1_senior', 'j1_ideology',
                 'j2_fullname', 'j2_dist_judge', 'j2_visiting_judge', 'j2_tenure', 'j2_elite',
                 'j2_gender', 'j2_race', 'j2_specific_race', 'j2_party', 'j2_age','j2_words', 'j2_chief',
                 'j2_senior', 'j2_ideology',
                 'j3_fullname', 'j3_dist_judge', 'j3_visiting_judge', 'j3_tenure', 'j3_elite',
                 'j3_gender', 'j3_race', 'j3_specific_race', 'j3_party', 'j3_age','j3_words', 'j3_chief',
                 'j3_senior', 'j3_ideology'
                 ])
    all_vars = []
    for i in range(0, len(file)):
        row = file.iloc[i]
        if not(isNaN(row.author_fullname)):
            # assuming we do not need data for the rows without an 'index' - check with prof
            append_list = [[float("NaN")] * 42]  # missing values
            all_vars = all_vars + append_list
            # append all Null values to lists
            continue

        judge_indices = [0,1,2]
        append_list_of_lists = []
        for j in judge_indices:
            append_list = compute_vars(row, j)
            append_list_of_lists = append_list_of_lists + append_list

        all_vars = all_vars + [list(itertools.chain.from_iterable(append_list_of_lists))]
    df2 = pd.DataFrame(all_vars, columns=new_vars_df.columns)
    new_vars_df = pd.concat([new_vars_df, df2])
    # new_vars_df = new_vars_df.append(pd.DataFrame(all_vars, columns=new_vars_df.columns))
    return (new_vars_df)
# now add these additional variables to each file and over-write files

if __name__ == "__main__":
    working_dir = os.path.join(sys.argv[1], 'output_dir')
    # working_dir = '/Volumes/SaloniWD/CoA-setup/output_dir'
    all_files = os.listdir(working_dir + '/final/')
    keep_rows = pd.DataFrame()
    print("Creating additional variables")
    for f in tqdm(all_files):
        file_name = working_dir + '/final/' + f
        file = pd.read_csv(file_name)

        # fixing multiple author rows
        file.loc[file['index'] == '01', 'index'] = 'not_found'
        file.loc[file['index'] == '02', 'index'] = 'not_found'
        file.loc[file['index'] == '12', 'index'] = 'not_found'
        file.loc[file['index'] == '012', 'index'] = 'not_found'

        # remove all unmerged data - already dropped??? - yes it is an inner merge
        file['year_decision'] = file['decision_date'].str[:4]
        file["topics_clean"] = file.apply(lambda x: generate_topics_from_apptype_topiccode(x.APPTYPE, x.NOS), axis=1)
        file["has_concurrence"] = file.apply(lambda x: get_case_type_concurrence(x.type), axis=1)
        file["has_dissent"] = file.apply(lambda x: get_case_type_dissent(x.type), axis=1)
        file["get_publication_type"] = file.apply(lambda x: publication_type(x.citations), axis=1)
        file['published_caselaw'] = file.apply(lambda x: publication_type_reporter(x.reporter), axis = 1)
        file['get_opinion_length'] = file.apply(lambda x: get_opinion_length(x.text_split), axis = 1)

        # loop to add more variables
        add_vars = get_additional_vars(file)
        non_author_vars = get_additional_vars_non_author(file)
        file = file.join(add_vars)
        file = file.join(non_author_vars)
        new_vars = add_new_variables(file) # for those with no author only
        file = file.join(new_vars)


        file_name=file_name.replace("final","final_add") # remove this to replace same file - this is added only for trial
        # print(file_name)
        file.to_csv(file_name,index=False)
