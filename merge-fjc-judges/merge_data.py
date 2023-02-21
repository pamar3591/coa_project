# merge IDB, citations, pagerank data

import os
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import csv
import sys

def load_idb_data(working_dir_data):
    try:
        idb_df_pre = pd.read_csv(working_dir_data + "/ap08on.txt", delimiter="\t", low_memory=False)   # Here we are importing the data. The original data is available on file with Nina Varsava.
        idb_df_07 = pd.read_csv(working_dir_data + "/ap71to07.txt", delimiter="\t", low_memory=False)
                 # Here we are importing the data. The original data is available on file with Nina Varsava.
    except:
        print("IDB files not found")
        sys.exit(1)
    # Concatanate
    idb = pd.concat([idb_df_pre, idb_df_07], ignore_index=True, sort=False)
    del (idb_df_pre)
    del (idb_df_07)
    return(idb)

# Normalize DOCKET to str (with leading zeroes)
# eg. 917 -> 0000917
def normalize_docket(i):
    # 7-digits str is expected
    DIGITS = 7
    number_str = str(i)
    zero_filled_number = number_str.zfill(DIGITS)
    return zero_filled_number

def normalize_ddate(s):
    # Normalize decision date: JUDGDATE
    # A str with following sequence: Year Month Day, eg. 20071128
    # eg. 11/28/2007 -> 20071128
    date_time_str = datetime.strptime(s, '%m/%d/%Y').strftime("%Y%m%d")
    return date_time_str

def normalize_idb(idb):
    idb['CIRCUIT'] = idb['CIRCUIT'].replace(0, 12)
    idb['CIRCUIT_STR'] = idb['CIRCUIT'].astype(int).astype(str)
    idb['DOCKET_STR'] = idb.DOCKET.apply(normalize_docket)
    idb['JUDGDATE_NOR'] = idb['JUDGDATE'].apply(normalize_ddate)
    idb['IDB_ID'] = idb['CIRCUIT_STR'] + "_" + idb['DOCKET_STR'] + "_" + idb['JUDGDATE_NOR']

    return(idb)

def normalize_csl_court_names(csl):
    # Normalize courts to 12 courts
    csl['case_court_num'] = csl['circuitNum']
    # circuitNum has already been normalized

    # Normalize courts to numbers
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca1', '1')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca2','2')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca3','3')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca4','4')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca5','5')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca6','6')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca7','7')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca8','8')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca9','9')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca10','10')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'ca11', '11')
    csl['case_court_num'] = csl['case_court_num'].str.replace(r'cadc', '12')
    return(csl)

def normalize_csl_docket(working_dir, csl,l):
    csl['case_docketnum_nor'] = csl['docket_number']

    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{4})$",lambda x: x.group(1) + '0' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{5})$",lambda x: x.group(1) + x.group(2), regex=True)

    # sb: check the different variants - for instance, for 'Nos. 12-1573, 12-1653' - matches the first docket
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r'^[^0-9]*([0-9]{2})-([0-9]{4})(\D.*|$)',lambda x: x.group(1) + '0' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r'^[^0-9]*([0-9]{2})-([0-9]{5})(\D.*|$)',lambda x: x.group(1) + x.group(2), regex=True)

    # handling cases for circuit number 2
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"Docket ","")
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{3})$",lambda x: x.group(1) + '00' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{2})$",lambda x: x.group(1) + '000' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{1})$",lambda x: x.group(1) + '0000' + x.group(2),regex=True)

    # cases like: 15-715, 15-71 (adding 0s to adjust)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^([0-9]{2})-([0-9]{3})$",lambda x: x.group(1) + '00' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^([0-9]{2})-([0-9]{2})$",lambda x: x.group(1) + '000' + x.group(2),regex=True)

    # cases like: 15-715-cr, 15-71-cr (adding 0s to adjust and ignoring characters)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^([0-9]{2})-([0-9]{3})(\D.*|$)",lambda x: x.group(1) + '00' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^([0-9]{2})-([0-9]{2})(\D.*|$)",lambda x: x.group(1) + '000' + x.group(2),regex=True)

    # cases like: No. 06—0136—ag, No. 06—136—ag, No. 06—36—ag or No. 06—6—ag (adding 0s to adjust)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{4})(\D.*|$)",lambda x: x.group(1) + '0' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{3})(\D.*|$)",lambda x: x.group(1) + '00' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{2})(\D.*|$)",lambda x: x.group(1) + '000' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^No\. ([0-9]{2})-([0-9]{1})(\D.*|$)",lambda x: x.group(1) + '0000' + x.group(2),regex=True)


    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^Nos\. ([0-9]{2})-([0-9]{3})(\D.*|$)",lambda x: x.group(1) + '00' + x.group(2),regex=True)
    csl['case_docketnum_nor'] = csl['case_docketnum_nor'].str.replace(r"^Nos\. ([0-9]{2})-([0-9]{2})(\D.*|$)",lambda x: x.group(1) + '000' + x.group(2),regex=True)

    # sb: there seems to be only one such case in courtno_1 - with 6 digits but that is handled (only here it is No. O5-1096 and not No. 05-1096) - note the wrong "0")
    remaining_data = csl[csl['case_docketnum_nor'].str.contains("^[0-9]{7}$") == False]
    i = csl[csl['case_docketnum_nor'].str.contains("^[0-9]{7}$") == False]['case_docketnum_nor'].index
    # write detail for each row
    for r in range(0, len(remaining_data)):
        row_data = [l, remaining_data.iloc[r].decision_date,  remaining_data.iloc[r].filename]
        with open(working_dir+'/diagnostics/docket_normalization_errors.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(row_data)
    csl.loc[i, 'case_docketnum_nor'] = '-1'
    return(csl)

def normalize_csl_decision_id(csl):
    # Normalize case decision date
    csl['case_decision_date_nor'] = csl['decision_date']
    csl['case_decision_date_nor'] = csl['case_decision_date_nor'].str.replace(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$",lambda x: x.group(1) + x.group(2) + x.group(3), regex=True)
    # Generate caselaw id for merging purpose
    csl['csl_id'] = csl['case_court_num'] + "_" +  csl['case_docketnum_nor'] + "_" + csl['case_decision_date_nor']
    return(csl)

if __name__ == "__main__":
    working_dir = os.path.join(sys.argv[1], 'output_dir')
    working_dir_data = os.path.join(sys.argv[1], 'data-raw')
    all_files = os.listdir(working_dir + '/coaCSV/')
    all_files = [x for x in all_files if 'expanded' in x]

    row_data = ['circuit_file_name', 'decision_date','filename']
    with open(working_dir+'/diagnostics/docket_normalization_errors.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(row_data)

    processed_files = os.listdir(working_dir + '/processedFiles/')
    processed_files = [x for x in processed_files if 'expanded' in x]



    print("Loading citation data...")
    try:
        cited_from = pd.read_csv(working_dir_data + '/cited_from.csv.gz',compression='gzip')  # case_index is unique so can be directly merged
        #  Here we are importing the data. The original data is available on file with Nina Varsava.
        cited_to = pd.read_csv(working_dir_data + '/cited_to.csv.gz',compression='gzip')  # case_index is unique so can be directly merged
                         # Here we are importing the data. The original data is available on file with Nina Varsava.
    except:
        print("Citation data not found")
        sys.exit(1)

    print("Loading pagerank data...")
    try:
        pagerank = pd.read_csv(working_dir_data + '/pagerank_scores_renamed.csv')  # case_index is unique so can be directly merged
                         # Here we are importing the data. The original data is available on file with Nina Varsava.
                         
    except:
        print("Pagerank data not found")
        sys.exit(1)

    # IDB data load
    print("Loading IDB data...")
    idb = load_idb_data(working_dir_data)
    idb = normalize_idb(idb) # this uses entire date to create IDB_ID
    idb = idb.drop_duplicates(subset=['IDB_ID'], keep="first") # we can drop duplicate IDs since the data is the same
    # we checked whether duplicates for the same IDB_ID had different values for NOS and APPTYPE - there were none
    idb['count'] = idb.groupby('IDB_ID')['IDB_ID'].transform('count')

    for f in tqdm(range(0,len(all_files))):
        filename = working_dir + '/coaCSV/' + all_files[f]
        read_file = pd.read_csv(filename)
        merge_file_name = working_dir + '/processedFiles/computed_index_' + all_files[f]
        index_file_read = pd.read_csv(merge_file_name)

        # add columns
        merged_data = pd.concat([read_file, index_file_read], axis=1)

        # merge citations
        merged_data = merged_data.merge(cited_from, left_on='filename',right_on='case_index', how='left')
        merged_data = merged_data.merge(cited_to, left_on='filename',right_on='case_index', how='left')

        # pagerank data
        pagerank['case_index'] = pagerank['case_index'].astype(int)
        merged_data = merged_data.merge(pagerank, left_on='filename',right_on='case_index', how='left')

        merged_data = normalize_csl_court_names(merged_data)
        merged_data = normalize_csl_docket(working_dir, merged_data,all_files[f])
        merged_data = normalize_csl_decision_id(merged_data)

        # merge IDB data
        # this step merges 98% of cases in case law with the IDB data
        # by default this is an inner merge
        merged = merged_data.merge(idb, left_on='csl_id', right_on='IDB_ID',how="inner")

        # write out unmerged file for diagnostics
        get_unmerged = pd.merge(merged_data, merged, how='outer', left_on='csl_id', right_on='IDB_ID', indicator=True)
        get_unmerged = get_unmerged[get_unmerged['_merge'] == 'left_only']
        write_unmerged_file_name = working_dir + '/diagnostics/unmerged_csl/' + all_files[f].replace('ForCOA_expanded', '')
        get_unmerged.to_csv(write_unmerged_file_name, index=False)



        # write merged file
        write_file_name = working_dir + '/final/' + all_files[f].replace('ForCOA_expanded','')
        print("Generated: ", write_file_name)
        merged.to_csv(write_file_name, index=False)
