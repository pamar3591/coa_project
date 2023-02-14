import os
import pandas as pd
import re
import sys


def get_judge_ideology():
    try:
        ideology_loc = os.path.join(sys.argv[1], "data-raw/judge_ideology_JCS.sav") # Here we are importing the data. The original data is available on file with Nina Varsava. Please contact for any question or issues
        ideology = pd.read_spss(ideology_loc)
    except:
        print("Ideology data not found")
        print(ideology_loc)
        sys.exit(1)

    dic = {1: "first", 2: "second", 3: "third", 4: "fourth",
           5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth",
           9: "ninth", 10: "tenth", 11: "eleventh", 12: "twelfth", 13: "fed"
           }
    ideology.circuit = ideology.circuit.replace(dic)
    return (ideology)


def get_full_name_ide(judge_combined, dataset_type):
    match_names = []
    for j in range(0, len(judge_combined)):
        elem = judge_combined.iloc[j]
        try:
            name = (elem["Last Name"] + ", " + elem["First Name"]).strip()
        except:
            if dataset_type == "judge_ideology":
                name = (elem["Last Name"] + ", " + elem["First Name"] + " " + (
                    elem['Middle Name'][0] + "." if elem['Middle Name'] != " " else "")).strip()
            elif dataset_type == "judge_cases1":
                name = (elem["First Name"] + " " + (
                    elem['Middle Name'][0] if elem['Middle Name'] != " " else "") + " " + elem[
                            "Last Name"]).strip().lower()
        finally:
            name = name.replace("  ", " ")
            match_names.append(name)
    return (pd.Series(match_names).values)


def merge_judge_ideology(judge_combined):
    judge_combined.loc[:, "court_name"] = judge_combined.court_name.replace(
        {"U.S. Court of Appeals for the Federal Circuit": "fed"})

    courts = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh",
              "twelfth", "fed"]
    judge_combined.loc[:, 'full_name_match_ide_middle_initial'] = get_full_name_ide(judge_combined, "judge_ideology")
    judge_combined.loc[:, 'full_name_match_ide'] = (
                judge_combined["Last Name"] + ", " + judge_combined["First Name"]).str.strip()
    matchedIdeology = pd.DataFrame()
    ideology = get_judge_ideology()

    total_judges = 0
    for court in courts:
        sub_judge = judge_combined[judge_combined.court_name == court]
        total_judges = total_judges + len(sub_judge)

    for court in courts:
        subIde = ideology[ideology.circuit == court].copy()

        sub_judge = judge_combined[judge_combined.court_name == court]
        
        match_judges = sub_judge.merge(subIde, left_on="full_name_match_ide", right_on="name", how="left")
        merged = match_judges[match_judges['name'].notnull()]
        unmerged = match_judges[match_judges['name'].isnull()].drop(['name', 'JCS2018', 'circuit'], axis=1)

        # key: "John Preston Bailey" --> Bailey, John P.
        merge_using_middle = unmerged.merge(subIde, left_on="full_name_match_ide_middle_initial", right_on="name",
                                            how="left")
        merge_using_middle_keep = merge_using_middle[merge_using_middle['name'].notnull()]
        unmerged_2 = merge_using_middle[merge_using_middle['name'].isnull()].drop(['name', 'JCS2018', 'circuit'],
                                                                                  axis=1)
        subIde.loc[:, 'name_modified'] = subIde.name.apply(lambda x: re.sub(r'[A-Z]+\.', "", x).strip())

        # here Cyr, Conrad K. got merged to Cyr, Conrad F. (Not sure if this is right)
        final_merge = unmerged_2.merge(subIde, left_on="full_name_match_ide", right_on="name_modified",
                                       how="left").drop(["name_modified"], axis=1)

        required_df = pd.concat([merged, merge_using_middle_keep, final_merge])
        matchedIdeology = pd.concat([matchedIdeology,required_df])
        # to check if there are any errors (there are none)
        if (len(required_df) != len(sub_judge)):
            print("Issue in merging for court:", court)
    return (matchedIdeology)

#

if __name__ == "__main__":
    print("Merging judge ideology with fjc data")
    working_dir = sys.argv[1]
    try:
        judge_combined = pd.read_csv(working_dir + '/data-raw/federal_judges_organized_by_judge.csv')  # Here we are importing the data. The original data is available on file with Nina Varsava. Please contact for any question or issues
    except:
        print("Federal judges data missing")
        sys.exit(1)

    circuitLongToShort = {'U.S. Court of Appeals for the District of Columbia Circuit': 'twelfth',
                          'U.S. Court of Appeals for the Federal Circuit': 'fed',
                          'U.S. Court of Appeals for the First Circuit': 'first',
                          'U.S. Court of Appeals for the Second Circuit': 'second',
                          'U.S. Court of Appeals for the Third Circuit': 'third',
                          'U.S. Court of Appeals for the Fourth Circuit': 'fourth',
                          'U.S. Court of Appeals for the Fifth Circuit': 'fifth',
                          'U.S. Court of Appeals for the Sixth Circuit': 'sixth',
                          'U.S. Court of Appeals for the Seventh Circuit': 'seventh',
                          'U.S. Court of Appeals for the Eighth Circuit': 'eighth',
                          'U.S. Court of Appeals for the Ninth Circuit': 'ninth',
                          'U.S. Court of Appeals for the Tenth Circuit': 'tenth',
                          'U.S. Court of Appeals for the Eleventh Circuit': 'eleventh'}

    judge_combined.loc[:,'court_name'] = judge_combined['Court Name (1)'].replace(circuitLongToShort, regex=True)

    merged_ideology_df = merge_judge_ideology(judge_combined)

    # now we write out the file: all merged (with ideology) + all unmerged (without ideology - here it will be NA)
    # keep columns
    merged_data = merged_ideology_df[['jid', 'name', 'JCS2018', 'circuit']]

    judge_combined = judge_combined.merge(merged_data, on="jid", how="left")
    judge_combined.to_csv(working_dir + '/output_dir/judges/FJC_alljudge_clean_ideology.csv', index=False)
