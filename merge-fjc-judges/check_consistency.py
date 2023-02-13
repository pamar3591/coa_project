import pandas as pd
import os
import statistics

# idea is to check all variables and see if there are any inconsistencies in the way they are coded

# important variations could be in: author, type

all_files = os.listdir('/Volumes/SaloniWD/CoA-setup/output_dir/filter/')
all_files.remove('combined.csv')
# file = pd.read_csv('/Volumes/SaloniWD/PA Back up/data/us_text_20200604/data/filter/' + all_files[0])
# new_vars = list(file.columns)
# del(file)



keep_vars = ['court', 'us_party',
       'corp_party','opinion_type', 'case_has_concurrence', 'case_has_dissent',
       'published', 'published_caselaw', 'author_district', 'author_visiting','author_elite', 'author_gender', 'author_race',
       'author_party', 'author_chief',
       'author_senior', 'judge1_district',
       'judge1_visiting', 'judge1_elite', 'judge1_gender',
       'judge1_race', 'judge1_party', 'judge1_chief',
       'judge1_senior', 'judge2_district',
       'judge2_visiting', 'judge2_elite', 'judge2_gender',
       'judge2_race', 'judge2_party', 'judge2_chief',
       'judge2_senior']

avg_var_list = ['get_words','year_decision','get_age','get_tenure']
avg_var_list = ['opinion_length','author_age','author_ideology','judge1_age','judge1_ideology','judge2_age','judge2_ideology']
# def check_numeric_values(num):

    # return(min, max, average and median)

variables_df = pd.DataFrame(columns=['variable_name','value'])
min_max_df = pd.DataFrame(columns=['file_name','variable_name','min','max','average','median'])
row = 0
row_m = 0
for f in all_files:
    file = pd.read_csv('/Volumes/SaloniWD/CoA-setup/output_dir/filter/' + f)
    # check what the unique values of type are
    # do this for each variable and write out to csv file?

    # set of variables to check: do this only for the additional variables!
    for k in keep_vars:
        all_variations = list(set(file[k.format()].dropna()))
        # all_variations = list(set(file[k.format()]))
        for variations in all_variations:
            variables_df.loc[row] = [k, variations]
            row = row + 1
            # print(k,variations)
    for a in avg_var_list:
        select_col = file[a.format()].dropna()
        if len(select_col)!=0:
            min_val, max_val = min(select_col),max(select_col)
            avg_val = sum(select_col)/ len(select_col)
            median_val = statistics.median(select_col)
            min_max_df.loc[row_m] = [f, a, min_val, max_val, avg_val, median_val]
            row_m = row_m + 1
    print(f)

variables_df = variables_df.drop_duplicates()
variables_df.to_csv('check_variable_consistency.csv',index=False)
min_max_df.to_csv('numeric_variable_consistency.csv',index=False)



# negative judge tenures - why?!
# write out these rows in a new file
# all of these are visiting judges!!
# file = pd.read_csv('/Volumes/SaloniWD/PA Back up/data/us_text_20200604/data/final_add/' + all_files[0])
#     # negative judge rows only
# judge_tenures_negative = file[file['get_tenure'].notna()]
# judge_tenures_negative = judge_tenures_negative[judge_tenures_negative['get_tenure']<0]
# judge_tenures_negative = judge_tenures_negative[['filename','decision_date','court_name','commission_date1','commission_date2','commission_date3','commission_date4','commission_date5',
#                                                      'commission_date6','index','author','all_judges','get_tenure','court_name1','court_name2','court_name3','get_visiting_judge']]
# judge_tenures_negative.to_csv('judge_tenures_negative.csv', mode='a', index=False)
# for f in all_files[1:]:
#     file = pd.read_csv('/Volumes/SaloniWD/PA Back up/data/us_text_20200604/data/final_add/' + f)
#     # negative judge rows only
#     judge_tenures_negative = file[file['get_tenure'].notna()]
#     judge_tenures_negative = judge_tenures_negative[judge_tenures_negative['get_tenure']<0]
#     judge_tenures_negative = judge_tenures_negative[['filename','decision_date','court_name','commission_date1','commission_date2','commission_date3','commission_date4','commission_date5',
#                                                      'commission_date6','index','author','all_judges','get_tenure','court_name1','court_name2','court_name3','get_visiting_judge']]
#     judge_tenures_negative.to_csv('judge_tenures_negative.csv', mode='a', index=False, header=False)
#     print(f)

# judges_tenure_negative = pd.read_csv('judge_tenures_negative.csv')
# judges_tenure_negative = judges_tenure_negative.drop([''])
check_index=True
for f in all_files:
    file = pd.read_csv('/Volumes/SaloniWD/CoA-setup/output_dir/filter/' + f)
    # check what the unique values of type are
    # do this for each variable and write out to csv file?
    df = file['opinion_type'].value_counts().rename_axis('unique_values').reset_index(name='counts')
    df['file'] = f
    df.to_csv('type_counts.csv',mode='a',header=check_index,index=False)

    # example of 'rehearing'
    rehearing_df = file[file['opinion_type']=='rehearing']
    rehearing_df.to_csv('rehearing.csv',mode='a',header=check_index,index=False)
    check_index = False
    # set of variables to check: do this only for the additional variables!

for f in all_files:
    file = pd.read_csv('/Volumes/SaloniWD/CoA-setup/output_dir/filter/' + f)
    print(set(file['topic']))