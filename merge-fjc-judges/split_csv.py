# creates a separate row for each opinion given by judge

import pandas as pd
import os
import re
import csv
import unidecode
from tqdm import tqdm
import sys

def clean_author_list(author):
    try:
        author = author.split(';')
    except:
        author = []
    author = [x for x in author if x != ""]
    author = [unidecode.unidecode(x) for x in author]  # getting rid of accents
    author = [x for x in author if x != ""]  # to avoid one error
    author = [x.strip() for x in author]
    return(author)

def write_data_to_file(filename, row_data):
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row_data)

def separate_opinions_in_file(read_file):
    count = 0
    for i in range(0, len(read_file)):
        try:
            opinion_text = [x for x in read_file.text.iloc[i].split(';opinion_text_begin') if x != '']
        except:
            opinion_text = "" # for missing opinion text
        if len(opinion_text) > 1:
            count = count + 1
    return(count)

def separate_types_in_file(read_file):
    count = 0
    for i in range(0, len(read_file)):
        try:
            type = [x for x in read_file.type.iloc[i].split(';') if x != '']
        except:
            type = ""
        if len(type) > 1:
            count = count + 1
    return (count)

def clean_text_split(text):
    try:
        text = text.split(';opinion_text_begin')
        text = [x for x in text if x != ""]
        text = [unidecode.unidecode(x) for x in text]  # getting rid of accents
        text = [x for x in text if x != ""]  # to avoid one error
        text = [x.strip() for x in text]
    except:
        text = []
    return(text)

def clean_all_judges(text):
    try:
        text = unidecode.unidecode(text)  # getting rid of accents
        text = text.strip()
    except:
        return(text)
    return (text)

def clean_type_split(type):
    try:
        type = type.split(';')
        type = [x for x in type if x != ""]
        type = [unidecode.unidecode(x) for x in type]  # getting rid of accents
        type = [re.sub('[^A-Za-z0-9]+', ' ', x) for x in type]  # remove all special characters from list which are not alphabets
        type = [x for x in type if x != ""]  # to avoid one error
        type = [x.strip() for x in type]
    except:
        type = []
    return(type)

def split_rows(read_file,file, working_dir):
    # working_dir = sys.argv[1]
    working_dir = os.path.join(working_dir, 'output_dir')
    for i in range(0, len(read_file)):
        author = read_file['author'].iloc[i]
        author = clean_author_list(author)
        if author == []:  # to handle type 'nan' for author from clean_author_list
            write_data = list(read_file.iloc[i].values) + ['nan_author', 'nan_type', 'nan_text', clean_judges]
            write_data_to_file(working_dir + '/diagnostics/' + 'empty_author_check.csv', write_data)
            continue
        type = clean_type_split(read_file['type'].iloc[i])
        text = clean_text_split(read_file['text'].iloc[i])
        clean_judges = clean_all_judges(read_file['judge_names'].iloc[i])
        for a in range(0, len(type)):
            if len(author) == len(type):
                write_data = list(read_file.iloc[i].values) + [author[a], type[a], text[a],clean_judges]
            else:
                write_data = list(read_file.iloc[i].values) + [author[0], float("NaN"), text[0],clean_judges]
                for_error_file = [read_file.iloc[i].filename, read_file.iloc[i].author, author, read_file.iloc[i].type, type, read_file.iloc[i].judge_names,file]
                write_data_to_file(working_dir + '/diagnostics/' + 'multi_author_doubt.csv', for_error_file)
            write_data_to_file(write_filename, write_data)

if __name__ == "__main__":

    working_dir = sys.argv[1]

    all_files = os.listdir(os.path.join(working_dir, 'output_dir/coaCSV/'))
    all_files = [x for x in all_files if 'expanded' not in x]  # to avoid errors during rerun as same folder structure
    print("Splitting by author name - opinion on each row")
    for f in tqdm(all_files):

        # read file
        filename = working_dir + '/output_dir/coaCSV/' + f
        print(filename)
        read_file = pd.read_csv(filename)

        # write header row
        write_filename = filename.replace('.csv','_expanded.csv')

        headerRow = ['', 'filename', 'caseTitle', 'judge_parties_list','judge_gender_list','judge_races_list','judge_races_fulltext','judges_births_list', 'year_filed',
					'circuitNum','judge_names','us_party','corp_party','len_text','includeInSTM','author','type','text','reporter','headMatter','docket_number',
					 'decision_date','court_name_abbv','court_name','court_id','citations',
                     'panel_ideology','judge_birth_year','judge_elite',
					 'court_type1','court_type2','court_type3','court_type4','court_type5','court_type6',
					 'commission_date1','commission_date2','commission_date3','commission_date4','commission_date5','commission_date6',
					 'court_name1','court_name2','court_name3','court_name4','court_name5','court_name6',
					 'chief11','chief12', 'chief21','chief22', 'chief31','chief32','chief41','chief42','chief51','chief52','chief61','chief62',
					 'chief11e', 'chief12e', 'chief21e', 'chief22e', 'chief31e', 'chief32e', 'chief41e', 'chief42e', 'chief51e',
					 'chief52e', 'chief61e', 'chief62e',
					 'senior1','senior2','senior3','senior4','senior5','senior6','opinion_author_split','type_split','text_split','clean_judges']
        write_data_to_file(write_filename, headerRow)

        # split rows by author
        split_rows(read_file, filename, working_dir)
