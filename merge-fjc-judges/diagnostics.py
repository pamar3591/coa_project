import pandas as pd
import os

# proportion of caselaw cases that have a majority or plural opinion author that we failed to match

# two sources of these errors:
# 1. Docket normalization
# count of failed docket normalization by court-year

def check_for_majority_or_plurality(type):
    if 'majority' in type or 'plurality' in type:
        return(True)
    return(False)

def count_judges(judge_names):
    return(len(judge_names.split(',')))

working_dir = os.path.join(sys.argv[1], 'output_dir')

### compute number of cases at every stage

def create_distribution(file_list, addr, output_fname):
    check_header = True
    for i in file_list:
        file_name = addr + i
        file = pd.read_csv(file_name)
        # remove duplicate filename (to generate this at the case level)
        file = file.drop_duplicates(subset=['filename'])

        file['count'] = 1
        try:
            file['year_decision'] = file['decision_date'].str[:4]
        except:
            file['year_decision'] = file['case_date'].str[:4]

        agg = file[['year_decision', 'count']].groupby(['year_decision']).count().reset_index()
        agg['file'] = i
        agg.to_csv(output_fname, index=False, mode='a',
                              header=check_header)
        check_header = False



# output of dataPrep: First stage
file_addr = working_dir + '/coaCSV/'
all_files_dataprep = os.listdir(file_addr)
all_files_dataprep = [x for x in all_files_dataprep if 'expanded' not in x]  # to avoid errors during rerun as same folder structure
diagnostics_output = working_dir + '/diagnostics/' + 'dataprep_diag.csv'
all_files_dataprep.sort()
create_distribution(all_files_dataprep, file_addr, diagnostics_output)

# next step: output of split_csv
file_addr = working_dir + '/coaCSV/'
all_files_dataprep = os.listdir(file_addr)
all_files_dataprep = [x for x in all_files_dataprep if 'expanded' in x]  # to avoid errors during rerun as same folder structure
diagnostics_output = working_dir + '/diagnostics/' + 'expanded_diag.csv'
create_distribution(all_files_dataprep, file_addr, diagnostics_output)

# next step: output of match opinion judges: just print out total length
file_addr = working_dir + '/processedFiles/'
all_files_match_opinions = os.listdir(file_addr)
for i in all_files_match_opinions:
    file = pd.read_csv(file_addr + i)
    print(len(file))

# NO LOSS HERE. SAME LENGTHS SO FAR

# next step: merging IDB etc.
file_addr = working_dir + '/final/'
all_files_dataprep = os.listdir(file_addr)
all_files_dataprep.sort()
diagnostics_output = working_dir + '/diagnostics/' + 'final_diag.csv'
create_distribution(all_files_dataprep, file_addr, diagnostics_output)

# next step: add variables
file_addr = working_dir + '/final_add/'
all_files_dataprep = os.listdir(file_addr)
all_files_dataprep.sort()
diagnostics_output = working_dir + '/diagnostics/' + 'final_add_diag.csv'
create_distribution(all_files_dataprep, file_addr, diagnostics_output)

# final step: filter
file_addr = working_dir + '/filter/'
all_file = os.listdir(file_addr)
all_file = [x for x in all_file if 'combined' not in x]
diagnostics_output = working_dir + '/diagnostics/' + 'filter_diag.csv'
all_file.sort()
create_distribution(all_file, file_addr, diagnostics_output)

# concatenate and analyse:
all_diag_files = os.listdir(working_dir + '/diagnostics/')
all_diag_files = [working_dir + '/diagnostics/' + x for x in all_diag_files if 'diag' in x]
all_diag_files.sort()
file1 = pd.read_csv(all_diag_files[0])

file2 = pd.read_csv(all_diag_files[4], usecols=['count'])
file3 = pd.read_csv(all_diag_files[3], usecols=['count'])
# file4 = pd.read_csv(all_diag_files[3], usecols=['count'])
file5 = pd.read_csv(all_diag_files[2], usecols=['count'])

concat_file = pd.concat([file1, file2, file3, file5], axis=1)
concat_file.columns = ['year_decision','count_dataprep','file','final','final_add_vars','filter']
concat_file['perc_loss'] = concat_file['filter'] / concat_file['count_dataprep']
write_file_name = working_dir + '/diagnostics/' + 'unique_cases_output_scriptwise.csv'
concat_file.to_csv(write_file_name, index=False)

def no_presiding_judge(row,author_absent):
    # 2 visiting and 1 senior?
    if author_absent == True:
        visiting_list = [row.j1_visiting_judge, row.j2_visiting_judge, row.j3_visiting_judge]
        senior_list = [row.j1_senior, row.j2_senior, row.j3_senior]
    else:
        visiting_list = [row.get_visiting_judge, row.get_visiting_judge1 , row.get_visiting_judge2]
        senior_list = [row.get_senior, row.get_senior1, row.get_senior2]
    if sum(visiting_list) == 3:
        return(float("NaN"))

all_files = os.listdir(working_dir + '/final_add/')
check_header = True
for f in all_files:
    file = pd.read_csv(working_dir + '/final_add/'+f)
    file['case_pj'] = file.apply(lambda x: determine_presiding_judge(x, "case_pj"), axis=1)
    nd = file[file['case_pj'].isna()]
    # nd['count_senior'] = 0
    # nd['count_visiting'] = 0
    nd.drop("text", axis=1, inplace=True)
    nd.drop("text_split", axis=1, inplace=True)
    sum_senior_list = []
    sum_visiting_list = []
    for i in range(0, len(nd)):
        row = nd.iloc[i]
        author_absent = isNaN(row.author_fullname)
        if author_absent == True:
            visiting_list = [row.j1_visiting_judge, row.j2_visiting_judge, row.j3_visiting_judge]
            senior_list = [row.j1_senior, row.j2_senior, row.j3_senior]
        else:
            visiting_list = [row.get_visiting_judge, row.get_visiting_judge1, row.get_visiting_judge2]
            senior_list = [row.get_senior, row.get_senior1, row.get_senior2]
        sum_senior_list.append(sum(senior_list))
        sum_visiting_list.append(sum(visiting_list))

    nd['count_senior'] = pd.Series(sum_senior_list).values
    nd['count_visiting'] = pd.Series(sum_visiting_list).values

    nd.to_csv(working_dir + '/diagnostics/presiding_judge_errors.csv', index=False, mode='a', header=check_header)
    check_header = False

            # if exactly 1 senior_judge;
            if sum(senior_list)==1:
                case_pj_index = row.judge_names.split(',')[req_index].strip()[senior_list.index(1.0)]

            if sum(visiting_list)!=3:
                if sum(senior_list)!=3:
                    print(sum(visiting_list),sum(senior_list),i)



for i in range(0, len(file)):
    row = file.iloc[i]
    judge_indices = [0, 1, 2]
    for j in judge_indices:
        presiding_judge = determine_presiding_judge(row, j)


for i in range(0, len(file)):
    row = file.iloc[i]
    judge_indices = [0, 1, 2]
    for j in judge_indices:
        get_dist_judge = check_district_judge(row, j)


# count >1 chief judge
all_files = os.listdir(working_dir + '/final_add/')
# all_files = [all_files[0]]
check_header = True
for f in all_files:
    nd = pd.read_csv(working_dir + '/final_add/'+f)
    nd['count_chief_judge'] = 0
    nd.drop("text", axis=1, inplace=True)
    nd.drop("text_split", axis=1, inplace=True)
    sum_chief_list = []
    for i in range(0, len(nd)):
        row = nd.iloc[i]
        author_absent = isNaN(row.author_fullname)
        if author_absent == True:
            chief_list = [row.j1_chief, row.j2_chief, row.j3_chief]
            # if chief judge is visiting then remove from chief_list
            visiting_list = [row.j1_visiting_judge,row.j2_visiting_judge, row.j3_visiting_judge]
            keep_chief = []
            for a in range(0, len(visiting_list)):
                if visiting_list[a]!=1: keep_chief.append(chief_list[a])
        else:
            chief_list = [row.get_chief, row.get_chief1, row.get_chief2]
            visiting_list = [row.get_visiting_judge, row.get_visiting_judge1, row.get_visiting_judge2]
            keep_chief = []
            for a in range(0, len(visiting_list)):
                if visiting_list[a] != 1: keep_chief.append(chief_list[a])
        sum_chief_list.append(sum(keep_chief))

    nd['count_chief_judge'] = pd.Series(sum_chief_list).values

    nd = nd[nd['count_chief_judge']>1]
    nd.to_csv(working_dir + '/diagnostics/multiple_chief_judge.csv', index=False, mode='a', header=check_header)
    check_header = False


# in the _expanded files, what is the number of CASES with a majority/plurality opinion author

# create case distribution

def create_case_distribution(file_list, working_dir, output_fname):
    check_header = True
    for f in file_list:
        try:
            data = pd.read_csv(working_dir + '/coaCSV/' + f)
        except:
            data = pd.read_csv(working_dir + '/final/' + f)
        # only get the CASES with a majority / plurality opinion author
        # data = data[data['type_split'].notna()]
        data = data[(data['type_split'] == 'majority') | (data['type_split'] == 'plurality')]
        if f == 'ca5DataForCOA_expanded.csv':
            data = data[~((data['filename'] == 5752031) & (data['type_split'] == 'plurality'))]  # HARD CODED
        if f == 'ca6DataForCOA_expanded.csv':
            data = data[~((data['filename'] == 3600356) & (data['type_split'] == 'plurality'))]  # HARD CODED

        data['count'] = 1
        try:
            data['year_decision'] = data['decision_date'].str[:4]
        except:
            data['year_decision'] = data['case_date'].str[:4]

        agg = data[['year_decision', 'count']].groupby(['year_decision']).count().reset_index()
        agg['circuit_no'] = f[0:4]
        agg.to_csv(output_fname, index=False, mode='a',
                              header=check_header)
        check_header = False



all_files = os.listdir(working_dir + '/coaCSV/')
all_files = [a for a in all_files if 'expanded' in a]
#we create a list with the total number of cases, by circuit-year
create_case_distribution(all_files, working_dir, 'output_dir/diagnostics/total_cases.csv'

# then we calculate which CASES we were not able to match to authors (from remaining_errors)
remaining_errors = pd.read_csv('output_dir/diagnostics/remaining_errors.csv')
remaining_errors['circuit_no'] = remaining_errors['source'].str[0:4]
remaining_errors['count'] = 1
remaining_errors['year_decision'] = remaining_errors['decision_date'].str[:4]
agg = remaining_errors[['year_decision', 'circuit_no','count']].groupby(['year_decision','circuit_no']).count().reset_index()
agg.to_csv('output_dir/diagnostics/author_error_summary.csv', index=False)

# then we calculate which data we were not able to match to IDB
docket_normalization_errors = pd.read_csv('output_dir/diagnostics/docket_normalization_errors.csv')
docket_normalization_errors['circuit_no'] = docket_normalization_errors['circuit_file_name'].str[0:4]
docket_normalization_errors['count'] = 1
docket_normalization_errors['year_decision'] = docket_normalization_errors['decision_date'].str[:4]
agg = docket_normalization_errors[['year_decision', 'circuit_no','count']].groupby(['year_decision','circuit_no']).count().reset_index()
agg.to_csv('output_dir/diagnostics/docket_normalization_errors_summary.csv', index=False)

### final folder aggregate
all_files = os.listdir(working_dir + '/final/')
#we create a list with the total number of cases, by circuit-year
create_case_distribution(all_files, working_dir, 'output_dir/diagnostics/final_cases.csv')


## dropped cases summary
total_cases = pd.read_csv(working_dir + '/diagnostics/total_cases.csv')
missing_author_summary = pd.read_csv(working_dir + '/diagnostics/author_error_summary.csv')
docket_error_summary = pd.read_csv(working_dir + '/diagnostics/docket_normalization_errors_summary.csv')
remaining_cases = pd.read_csv(working_dir + '/diagnostics/final_cases.csv')

# now merging all these we have:
missing_author_summary.columns = ['missing_authors'....]
docket_error_summary.columns = ['missing_authors'....]
remaining_cases.columns = ['missing_authors'....]

total_cases = total_cases.merge(missing_author_summary, on=['circuit_no','...'], how = 'left')
total_cases = total_cases.merge(docket_error_summary, on=['circuit_no','...'], how = 'left')
total_cases = total_cases.merge(remaining_cases, on=['circuit_no','...'], how = 'left')

