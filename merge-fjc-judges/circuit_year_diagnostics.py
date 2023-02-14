import pandas as pd
import os

working_dir = os.path.join(sys.argv[1], 'output_dir')


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

### something is an issue: not able to figure out why there are MORE missing cases than those dropped due to
# author mismatch, #docker drop and #IDB drop
