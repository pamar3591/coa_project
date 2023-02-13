# match judge opinion names to the appropriate judge on the panel
# this approach is better than matching against *all* judges as it reduces sample against which names need to be compared
# marking errors against the ones with errors and writing out to file

import os
import re
import pandas as pd
import unidecode
from tqdm import tqdm
import sys

def check_per_curiam(author):
    a = author
    if a == 'per curiam' or a == "pe r curiam" or a == "per curlam" or a == "by the court" or a == "pur curiam" or a == 'pee cueiam' or a == 'p r curiam' or a.replace(" ","")=="percuriam" or a =="by the panel" or a == "memorandum and order" or a == "pee curiam" or a == "er curiam" or a == "per ctjriam":
        return(True)
    if len(a)<15 and "per cur" in a or "per curiam" in author: # for cases like 'per curiafd' or 'per curium' other variants:
        return(True)
    return(False)

def many_judges_check(author,all_judges):
    # do >1 judges have the same last name?
    # sometimes judge names are repeated but they are not really different judges
    # for example: ';RANDOLPH, Senior Circuit Judge:;SRINIVASAN, Circuit Judge,;SRINIVASAN, Circuit Judge,'
    # for cases like this, we require two tests. 1 tests it using author names, and second, also the sitting judges
    test_authors = check_multiple(author)
    test_judges = check_multiple(all_judges)
    if test_judges and test_authors:
        return(True)
    return(False)

def check_multiple(list):
    for a in list:
        if(list.count(a)>1):
            return(True)
        full_name = a.strip().split(' ')
        last_name = full_name[1] if len(full_name) == 2 else full_name[2] if len(full_name)==3 else full_name[0]
        if(len(full_name)!=1):
            for x in list:
                if x!=a and last_name==x:
                    return(True)
    return(False)

# function checks
# many_judges_check(['smith', 'nicholas', 'adam smith'])
# many_judges_check(['smith', 'nicholas', 'smith'])
# many_judges_check(['smith', 'nicholas', 'adam m smith'])
# many_judges_check(['jon smith', 'nicholas jon', 'adam'])

def clean_author_list(author):
    original_str = author
    author = author.split(';')
    author = [x for x in author if x != ""]
    author = [unidecode.unidecode(x) for x in author]  # getting rid of accents
    author = [re.sub('[^A-Za-z0-9\']+', ' ', x) for x in author]  # remove all special characters from list which are not alphabets
    author = [re.sub('[\']+', '', x) for x in author]  # handle apostrophe separately
    author = [x.lower().replace('concurring in part and dissenting in part',"").replace('gircuit','').replace('dissenting in part and concurring in part','').replace("jr.", "").replace('.', "").replace("chief judge", "").replace("chief district judge","").replace(',', '').replace("circuit judge", "").replace(":", "").replace("senior", "").replace("district", "").replace("judge", "").replace("dissenting","").replace("concurring","").replace("in part and in part","").replace("chief","").replace("united states","").replace("specially","").strip().replace('opinion','').replace('associate justice retired','').replace('associate justice','').replace('associate justice ret','').replace('gireuit','').replace('circuit','').replace('opinion','').replace('of the court','').replace('by the panel','') for x in author]
    author = [re.sub('^by ','',x) for x in author]
    author = [x.replace("van ", "") if x == "van antwerpen" else x for x in author]
    author = [re.sub(" jr$","",x) for x in author] # GREENAWAY JR to GREENAWAY
    author = [x for x in author if x != ""]  # to avoid one error
    author = [x.strip() for x in author]

    # if everything is getting deleted, add a check for empty [] author and then retrieve the original author string
    if author == []: # in this case we do not replace the string
        author = original_str
        author = author.split(';')
        author = [x for x in author if x != ""]
        author = [unidecode.unidecode(x) for x in author]  # getting rid of accents
        author = [re.sub('[^A-Za-z0-9]+', ' ', x) for x in author]  # remove all special characters from list which are not alphabets
        author = [x for x in author if x != ""]  # to avoid one error
        author = [x.strip() for x in author]
    return(author)

def find_index(author, all_judges,index):
    if len(author)!=0:
        if author[0] == "wilkins" and  sum(["wilkins" in x for x in all_judges])>1:
            author[0] = "wilkins williams" # hard reset to remove errors associated with wilkins
        if author[0] == "barkett" and sum(["barkett" in x for x in all_judges])==0:
            author[0] = "barrett"  # hard reset to remove errors associated with barkett
    for a in author:
        switch = True

        for b in all_judges:
            if a in b or b in a:
                index = index + ';' + str(all_judges.index(b))
                switch = False
        if(switch):
            index = index + "not_found"
    return(index)

def split_and_find_index(author, all_judges,index):
    if len(author)!=0:
        if author[0] == "wilkins" and  sum(["wilkins" in x for x in all_judges])>1:
            author[0] = "wilkins williams" # hard reset to remove errors associated with wilkins
        if author[0] == "barkett" and sum(["barkett" in x for x in all_judges])==0:
            author[0] = "barrett"  # hard reset to remove errors associated with barkett
    switch = True
    author = author.split(',')[0].strip()
    for b in all_judges:
        if author in b:
            index = index + ';' + str(all_judges.index(b))
            switch = False
    if(switch):
        index = index + "not_found"
    return(index)

def get_consec_caps(text):
    pattern = "[A-Z][A-Z]+"
    return(re.findall(pattern, text))

def check_author_in_opinion_text(text, all_judges):
    caps_list = get_consec_caps(text)
    index = 'not_found'
    if len(caps_list) > 1: # check only if the first name in the list matches something in the judge list (is this ok?)
        # attempt finding name in author list
        index = find_index([caps_list[0].lower()], all_judges,'')
    return(index)



def clean_names_find_index(author, all_judges,index):
    new_author = []
    for a in author:
        new_author.append(clean_names(a))
    new_judges = []
    for b in all_judges:
        new_judges.append(clean_names(b))
    index = find_index(new_author, new_judges,index)
    return(index)

def clean_names(a):
    a = a.strip()
    a = re.sub(r"\s+[a-zA-Z]*\s+", " ",  a) # exclude middle name --> "robert john thompson" --> "robert thompson"
    words = a.split(' ')
    words = [x for x in words if len(x) != 1]

    words.sort()
    words = ' '.join(words)
    return(words)

def isNaN(string):
    # check if string is nan
    return string != string
# checking if function is ok
# print(isNaN("hello"))
# print(isNaN(np.nan))

def fix_judge_name_typos(author):

    # To correct more typo, add the following pattern to the mapper:
    # re.compile(r"(^.*)WRONG_NAME(.*$)", flags=re.IGNORECASE): r"\1CORRECT_NAME\2"
    # Replace WRONG_NAME with the original name and the CORRECT_NAME with the corrected name
    # Note that raw strings are used in this mapper (meaning that it cannot take formatted strings)
    # Do not use formatted string, i.e., use "KRAVITCH" instead of "karvitch".upper() in the replace parameter

    # all judge names can be cleaned like this (including both the opinion author and panel judges)

    # should be: (change all to this format)
    # from typo mapper <ipynb>
    author = re.sub(r'^kravttch$',"kravitch",author)
    author = re.sub(r"^kravttch$", "kravitch",author)
    author = re.sub(r"^higgingson$", "higginson",author)
    author = re.sub(r"^manton$", "manion",author)
    author = re.sub(r"^hcudahy$", "cudahy",author)
    author = re.sub(r"^mekeague$", "mckeague",author)
    author = re.sub(r"^roberta. katzmann$", "robert a. katzmann",author)
    author = re.sub(r"^roberta. katzmann$", "robert a. katzmann",author)
    author = re.sub(r"^flectcher$", "fletcher",author)

    # mappings added by SB
    author = re.sub(r"^kayanaugh$", "kavanaugh",author)
    author = re.sub(r"^kayanaugh$", "kavanaugh", author)
    author = re.sub(r"^silbe rman$", "silberman",author)

    author = re.sub(r"^sel ya$", "selya",author)
    author = re.sub(r"^chiny$", "chin",author)
    author = re.sub(r'^jo hn m walker$', "walker john",author)
    author = re.sub(r'^card amone$', 'cardamone',author)
    author = re.sub(r"^raqgi$", "raggi",author)

    author = re.sub(r"^hard iman$", "hardiman",author)
    author = re.sub(r"^puentes$", "fuentes",author) # pull up cite and share
    # author = re.sub(r"^jones ii$", "jones",author) # pull up cite and share
    author = re.sub(r"^stephens f williams$","williams stephen",author) # pull up cite and share

    # which one to keep? Check
    author = re.sub(r'^barrett barrett$', "barkett", author)  # this is ok
    # needs to be fixed for specific rows: fix barrett to barkett only if
    # if author is barrett and there is a barrett on the panel --> do nothing
    # else author is barrett and there is a barkett on the panel --> change to barkett (handled in function with wilkins)
    

    author = re.sub(r'^gould gould$', "gould", author)  # check about this


    # merges from 'author error' column
    author = re.sub(r"^$", "tatenhove", author)
    author = re.sub(r"^van tatenhove$", "tatenhove",author)
    author = re.sub(r"^j o brien$", "brien",author)
    author = re.sub(r"^o brien j$", "brien", author)
    author = re.sub(r"^leon jordan$", "jordan",author)
    author = re.sub(r"^van graafeiland$", "graafeilan",author)
    # author = re.sub(r"^wilkins$", "wilkins william",author) # MIGHT STILL CREATE ISSUES - CHECK - yes it does. how to handle? Right at the end?
    author = re.sub(r"^debevoise court$", "debevoise",author)
    author = re.sub(r"^ward law$", "wardlaw",author)
    author = re.sub(r"^john g heyburn ii$", "heyburn",author)
    author = re.sub(r"^royner$", "rovner",author)
    author = re.sub(r"^coaven$", "cowen",author)
    author = re.sub(r"^omeara$", "o meara",author)
    author = re.sub(r"^van bokkelen$", "bokkelen",author)
    author = re.sub(r'^m smith$', "smith", author)
    author = re.sub(r'^tymkoyich$', "", author)
    author = re.sub(r'^marbley court$', "marbley", author)
    author = re.sub(r'^boyce f martin jr circuit$', "boyce", author)
    author = re.sub(r'^ilana diamond royner$', "rovner", author)
    author = re.sub(r'^smith camp$', "camp", author)
    author = re.sub(r'^meconnell$', "mcconnell", author)
    author = re.sub(r'^b d parker$', "parker", author)
    author = re.sub(r'^sloyiter$', "sloviter", author)
    author = re.sub(r'^niemeyer niemeyer$', "niemeyer", author)
    author = re.sub(r'^daniel p jordan iii$', "jordan", author)
    author = re.sub(r'^suhrhe inrich$', "suhrheinrich", author)
    author = re.sub(r'^opinion boggs$', "boggs", author)
    author = re.sub(r'^w fletcher j$', "fletcher", author)
    author = re.sub(r'^w fletcher$', "fletcher", author)
    author = re.sub(r'^robert e baeharach$', "bacharach", author)
    author = re.sub(r'^robert e bacharaeh$', "bacharach", author)
    author = re.sub(r'^timothy m tymkovieh$', "tymkovich", author)
    author = re.sub(r'^j o brien$', "terrence", author)
    author = re.sub(r'^van graafeiland j$', "graafeiland", author)
    author = re.sub(r'^leyal$', "leval", author)
    author = re.sub(r'^o neill court$', "neill", author)
    author = re.sub(r'^pogue court of international trade$', "pogue", author)
    author = re.sub(r'^roth circuit court$', "roth", author)
    author = re.sub(r'^opinion of the court jordan$', "jordan", author)
    author = re.sub(r'^ambro in part$', "ambro", author)
    author = re.sub(r'^reayley$', "reavley", author)
    author = re.sub(r'^guy$', "ransey", author)
    author = re.sub(r'^opinion julia smith gibbons$', "gibbons", author)
    author = re.sub(r'^jon p mecalla$', "mccalla", author)
    author = re.sub(r'^omalley$', "o malley", author)
    author = re.sub(r'^clay j clay$', "clay", author)
    author = re.sub(r'^algenon l marbley court$', "marbley", author)
    author = re.sub(r'^shadid chief court$', "shadid", author)
    author = re.sub(r'^eanne$', "kanne", author)
    author = re.sub(r'^opinion by reinhardt$', "reinhardt", author)
    author = re.sub(r'^berzon berzon$', "berzon", author)
    author = re.sub(r'^kymer$', "rymer", author)
    author = re.sub(r'^opinion by clifton$', "clifton", author)
    author = re.sub(r'^o scannlain j$', "o scannlain", author)
    author = re.sub(r'^abarcon$', "alarcon", author)
    author = re.sub(r'^grajber$', "graber", author)
    author = re.sub(r'^opigraber$', "graber", author)
    author = re.sub(r'^grader$', "graber", author)
    author = re.sub(r'^paez paez$', "paez", author)
    author = re.sub(r'^opinion by clifton$', "clifton", author)
    author = re.sub(r'^thomas thomas$', "thomas", author)
    author = re.sub(r'^micheal daly hawkins$', "hawkins", author)
    author = re.sub(r'^opinion by reinhardt$', "reinhardt", author)
    author = re.sub(r'^silverman silverman$', "silverman", author)
    author = re.sub(r'^memillian$', "mcmillian", author)
    author = re.sub(r'^order and judgment mary beck briscoe$', "briscoe", author)
    author = re.sub(r'^timothy m tymkoyich$', "tymkovich", author)

    author = re.sub(r'^opinion by bea$', "bea", author)
    author = re.sub(r'^opinion graber$', "graber", author)
    author = re.sub(r'^j o brien concurring$', "brien", author)
    author = re.sub(r'^j o brien concurring in$', "brien", author)
    author = re.sub(r'^o brien j concurring$', "brien", author)
    author = re.sub(r'^mcckee$', "mckee", author)
    return (author)

def clean_all_judges(all_judges):
    all_judges = [unidecode.unidecode(x) for x in all_judges]  # avoiding errors in names like josé
    # all_judges = [re.sub('[^A-Za-z0-9]+', ' ', x) for x in all_judges]  # remove all special characters from list which are not alphabets
    all_judges = [re.sub('[^A-Za-z0-9\']+', ' ', x) for x in all_judges]  # remove all special characters from list which are not alphabets
    all_judges = [re.sub('[\']+', '', x) for x in all_judges]  # handle apostrophe separately
    all_judges = [x.strip() for x in all_judges]
    return(all_judges)

def process(file):
    file['all_judges'] = file['judge_names'].str.replace("  ", " ")  # get rid of double spaces
    file['all_judges'] = file['judge_names'].str.split(',')  # get list of judges for all rows split by ','
    file['opinion_author_split'] = file['opinion_author_split'].str.replace("  ",
                                                                            " ")  # get list of judges for all rows split by ','
    file['opinion_author_split'] = file['opinion_author_split'].str.replace("  ", " ")
    cleanJudge_index = [] # keeps track of correct
    errors = []
    many_judges_error = []
    # now we loop over each opinion judge to clean out the data
    for i in range(0, len(file)):
        no_author_found = 0
        multijudge = False
        author = file['opinion_author_split'].iloc[i]
        author = author.lower()

        all_judges = file['all_judges'].iloc[i]
        all_judges = clean_all_judges(all_judges)

        if(isNaN(author) or author == ";None" or author == "none"):
            cleanJudge_index.append([i,"None",author,all_judges,no_author_found])

        else:
            author = clean_author_list(author)
            author = fix_judge_name_typos(author[0])

            if(check_per_curiam(author)):
                cleanJudge_index.append([i, "per_curiam_in_opinion_name",author, all_judges,no_author_found])

            else: # last but two condition
                # author = clean_author_list(author)
                # check if author is per curiam only - exclude and cleanJudge_index.append("per curiam")
                author = [author]
                index = find_index(author, all_judges,'')
                multijudge = many_judges_check(author,all_judges)

                if index=='not_found': # last but final condition
                    # here we split by the comma and just match to the first one
                    author = file['opinion_author_split'].iloc[i].split(',')[0]
                    author = fix_judge_name_typos(author)
                    author = clean_author_list(author)
                    index = find_index(author, all_judges,'')
                    if index=='not_found': # final condition - look for author name in consecutive capital letters in the text
                        text = file.iloc[i].text_split[0:250]
                        index = check_author_in_opinion_text(text, all_judges)


            # check mismatch and keep track of errors
                if len(author) != index.count(';') and (file['opinion_author_split'].iloc[i] != ";None" or file['opinion_author_split'].iloc[i] != "none" or file['opinion_author_split'].iloc[i] != "nan_author"):
                    index = clean_names_find_index(author, all_judges, '')
                    if len(author) != index.count(';'): # if issue still not fully resolved
                        errors.append([i,author, all_judges, file['decision_date'].iloc[i],file['citations'].iloc[i],file['text_split'].iloc[i][0:250]])
                        no_author_found = 1
                cleanJudge_index.append([i, index,author,all_judges,no_author_found])
        many_judges_error.append(multijudge)

    return(many_judges_error, errors, cleanJudge_index)

def write_file(filename, data,read_file):
    data = pd.DataFrame(data, columns=['val'])
    data['source'] = read_file
    with open(filename, 'a') as f:
        data.to_csv(f, header=f.tell() == 0,index=False)

def write_file_index(filename, data,read_file):
    data = pd.DataFrame(data, columns=['val','index','author','all_judges','error_flags'])
    data['index'] = data['index'].str.replace(';','')
    data['source'] = read_file
    with open(filename, 'w') as f:
        data.to_csv(f, header=f.tell() == 0,index=False)

def write_file_errors(filename, data,read_file):
    data = pd.DataFrame(data, columns=['val','author','judge_name','decision_date','citations','text_beginning'])
    data['source'] = read_file
    counts = data['author'].value_counts()
    df = pd.DataFrame()
    df['author'] = counts.index
    df['count'] = counts.values
    df['author'] = df['author'].astype(str)
    data['author'] = data['author'].astype(str)
    data = pd.merge(data, df, left_on="author" ,right_on="author",how="left" )
    data = data.sort_values(by=['count'],ascending=False)
    with open(filename, 'a') as f:
        data.to_csv(f, header=f.tell() == 0,index=False)


# read all files in dir and process
if __name__ == "__main__":

    working_dir = sys.argv[1]
    working_dir = os.path.join(working_dir, 'output_dir')
    all_files = os.listdir(working_dir + '/stmCSV/')
    all_files = [x for x in all_files if 'expanded' in x]
    print("Matching opinion writing judges")

    remaining_error_filename = working_dir + '/diagnostics/remaining_errors.csv'
    computed_index_filename = working_dir + '/processedFiles/computed_index'
    for f in tqdm(all_files):
        filename = working_dir + '/stmCSV/' + f
        read_file = pd.read_csv(filename)
        many_judges_error,remaining_errors, computed_index = process(read_file)
        # write out correct files after checking everything with the additional data columns
        add_computed_filename = computed_index_filename + '_' + f
        write_file_errors(remaining_error_filename, remaining_errors, f)
        write_file_index(add_computed_filename, computed_index, f)


