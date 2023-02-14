import os
import pandas
import judgeClass
import numpy as np
import re
import csv

def findSchool(x):
	elite_schools_rev = ["yale", "harvard", "stanford", "columbia ", "university of chicago", "new york university",
						 "pennsylvania", "university of virginia",
						 "berkeley", 'duke', "university of michigan", "cornell", "georgetown"]
	for i in range(len(elite_schools_rev)):
		if isinstance(x,str): #  The isinstance() function returns True if the specified object is of the specified type, otherwise False.
			if len(re.findall(elite_schools_rev[i],x.lower())) > 0: ##
				return(True)
	return(False)


def findDegree(x):
	degrees = ["J.D.", "LL.B."]
	for i in range(len(degrees)):
		if isinstance(x,str):
			if len(re.findall(degrees[i],x)) > 0:
				return(True)
	return(False)

# apply(lambda...) makes code tidier and speeds up tasks as well

def find_school_degree(var, judge_combined):
	elite_var = "elite" + str(var)
	school_var = "School (" + str(var) + ")"
	law_var = "lawdegree" + str(var)
	degree_var = "Degree (" + str(var) + ")"
	judge_combined[elite_var] = judge_combined[school_var].apply(lambda x:findSchool(x))
	judge_combined[law_var] = judge_combined[degree_var].apply(lambda x:findDegree(x))
	judge_combined[elite_var] = (judge_combined[elite_var] == True) & (judge_combined[law_var] == True)
	return(judge_combined)

def findActivePeriods(dataFileName,minYear=1950,byYear=False,maxYear=2019):

	judgeData = pandas.read_csv(dataFileName)
	for i in range(1, 6):
		judgeData = find_school_degree(i, judgeData)

	judgeData["judge_elite"] = (judgeData.elite1 == True) | (judgeData.elite2 == True) | (judgeData.elite3 == True) | (judgeData.elite4 == True) | (judgeData.elite5 == True)
	judgeData = judgeData.drop(columns=["elite1", "elite2", "elite3", "elite4", "elite5", "lawdegree1", "lawdegree2", "lawdegree3","lawdegree4", "lawdegree5"])

	judgeData = judgeData.replace(np.nan, '', regex=True)
	judgeRecords = judgeData.to_dict('records')
	
	judgeInstances = {}
	for judgeRow in judgeRecords:
		for apptNum in range(1,7):

			apptStrMod = ' (' + str(apptNum) + ')'
			if (judgeRow['Court Type'+ apptStrMod] == 'U.S. Court of Appeals' or judgeRow['Court Type'+ apptStrMod] =='U.S. District Court' or
					judgeRow['Court Type'+ apptStrMod] == 'Other' or judgeRow['Court Type' + apptStrMod] == 'Supreme Court'):
				
				if str(judgeRow['Commission Date'+ apptStrMod]) =='':
					continue
				circuit = judgeRow['Court Name'+ apptStrMod]
				

				start = judgeRow['Commission Date'+ apptStrMod].split('-')[0]
				if str(judgeRow['Termination Date'+ apptStrMod]) == '':
					end = '9999'
				else:
					end = judgeRow['Termination Date'+ apptStrMod].split('-')[0]

				if int(end)<minYear-1:
					continue

				if str(judgeRow['Senior Status Date'+ apptStrMod]) == '':
					senior = '9999'
				else:
					senior = judgeRow['Senior Status Date'+ apptStrMod].split('-')[0]

				if str(judgeRow['Service as Chief Judge, Begin'+ apptStrMod]) == '':
					chiefStart = '9999'
				else:
					chiefStart = str(int(judgeRow['Service as Chief Judge, Begin'+ apptStrMod])).strip()

				if str(judgeRow['Service as Chief Judge, End'+ apptStrMod]) == '':
					chiefEnd = '9999'
				else:
					chiefEnd = str(int(judgeRow['Service as Chief Judge, End'+ apptStrMod])).strip()

				party = judgeRow['Party of Appointing President'+ apptStrMod]

				tempApptNum = apptNum - 1
				while (party=='None (reassignment)' or party=='None (assignment)') and tempApptNum>=1:
					tempApptStrMod = ' (' + str(tempApptNum) + ')'
					tempApptNum = tempApptNum-1
					party = judgeRow['Party of Appointing President'+ tempApptStrMod]


				gender = judgeRow['Gender']
				race = judgeRow['Race or Ethnicity']
				birth = str(int(judgeRow['Birth Year'])%2)
				
				firstName = judgeRow['First Name'].strip()
				lastName = judgeRow['Last Name'].strip().split(' ')[-1].strip()
                
                

				ideology = judgeRow['JCS2018']
				birth_year = judgeRow['Birth Year']
				judge_elite = judgeRow['judge_elite']
				court_type1 = judgeRow['Court Type (1)']
				court_type2 = judgeRow['Court Type (2)']
				court_type3 = judgeRow['Court Type (3)']
				court_type4 = judgeRow['Court Type (4)']
				court_type5 = judgeRow['Court Type (5)']
				court_type6 = judgeRow['Court Type (6)']

				commission_date1 = judgeRow['Commission Date (1)']
				commission_date2 = judgeRow['Commission Date (2)']
				commission_date3 = judgeRow['Commission Date (3)']
				commission_date4 = judgeRow['Commission Date (4)']
				commission_date5 = judgeRow['Commission Date (5)']
				commission_date6 = judgeRow['Commission Date (6)']

				court_name1 = judgeRow['Court Name (1)']
				court_name2 = judgeRow['Court Name (2)']
				court_name3 = judgeRow['Court Name (3)']
				court_name4 = judgeRow['Court Name (4)']
				court_name5 = judgeRow['Court Name (5)']
				court_name6 = judgeRow['Court Name (6)']


				# assuming varname is chiefxy where y = 1 when "service as chief judge" and y = 2 when "2nd Service as Chief Judge"
				# chiefxye - the 'e' indicates end
				# x indicates the nth time the judge takes the chief judge position. For instance, x = 1 would indicate (1)th position
				# and x = 2 would indicate (2)th position
				chief11 = judgeRow['Service as Chief Judge, Begin (1)']
				chief11e = judgeRow['Service as Chief Judge, End (1)']
				chief12 = judgeRow['2nd Service as Chief Judge, Begin (1)']
				chief12e = judgeRow['2nd Service as Chief Judge, End (1)']

				chief21 = judgeRow['Service as Chief Judge, Begin (2)']
				chief21e = judgeRow['Service as Chief Judge, End (2)']
				chief22 = judgeRow['2nd Service as Chief Judge, Begin (2)']
				chief22e = judgeRow['2nd Service as Chief Judge, End (2)']

				chief31 = judgeRow['Service as Chief Judge, Begin (3)']
				chief31e = judgeRow['Service as Chief Judge, End (3)']
				chief32 = judgeRow['2nd Service as Chief Judge, Begin (3)']
				chief32e = judgeRow['2nd Service as Chief Judge, End (3)']

				chief41 = judgeRow['Service as Chief Judge, Begin (4)']
				chief41e = judgeRow['Service as Chief Judge, End (4)']
				chief42 = judgeRow['2nd Service as Chief Judge, Begin (4)']
				chief42e = judgeRow['2nd Service as Chief Judge, End (4)']

				chief51 = judgeRow['Service as Chief Judge, Begin (5)']
				chief51e = judgeRow['Service as Chief Judge, End (5)']
				chief52 = judgeRow['2nd Service as Chief Judge, Begin (5)']
				chief52e = judgeRow['2nd Service as Chief Judge, End (5)']

				chief61 = judgeRow['Service as Chief Judge, Begin (6)']
				chief61e = judgeRow['Service as Chief Judge, End (6)']
				chief62 = judgeRow['2nd Service as Chief Judge, Begin (6)']
				chief62e = judgeRow['2nd Service as Chief Judge, End (6)']

				senior1 = judgeRow['Senior Status Date (1)']
				senior2 = judgeRow['Senior Status Date (2)']
				senior3 = judgeRow['Senior Status Date (3)']
				senior4 = judgeRow['Senior Status Date (4)']
				senior5 = judgeRow['Senior Status Date (5)']
				senior6 = judgeRow['Senior Status Date (6)']



				middleName = judgeRow['Middle Name'].strip()
				suffix = str(judgeRow['Suffix']).strip()
				

				fullName = lastName + '<' +' ' +firstName
				if middleName!='':
					fullName=fullName+' ' + middleName
				if suffix!='':
					fullName=fullName+' ' + suffix

				judgeInst = judgeClass.judge(circuit,start,end,party,gender,race,birth,fullName,lastName,firstName,ideology,birth_year,judge_elite,
											 court_type1,court_type2,court_type3,court_type4,court_type5,court_type6,
											 commission_date1,commission_date2,commission_date3,commission_date4,commission_date5,commission_date6,
											 court_name1, court_name2, court_name3, court_name4, court_name5, court_name6,
											 chief11, chief12, chief21, chief22, chief31, chief32, chief41, chief42, chief51, chief52, chief61, chief62,
											 chief11e, chief12e, chief21e, chief22e, chief31e, chief32e, chief41e, chief42e,chief51e, chief52e, chief61e, chief62e,
											 senior1,senior2, senior3, senior4, senior5, senior6,
											 seniorStart=senior,chiefStart=chiefStart,chiefEnd=chiefEnd ,middleName=middleName)

				
				if byYear:
					if circuit not in judgeInstances:
						judgeInstances[circuit] = {}
					for loopYear in range(max(int(start),minYear)-1,min((int(end),maxYear))+2):
						if loopYear not in judgeInstances[circuit]:
							judgeInstances[circuit][loopYear] = []
						judgeInstances[circuit][loopYear].append(judgeInst)
				else:
					if circuit not in judgeInstances:
						judgeInstances[circuit] = []
					judgeInstances[circuit].append(judgeInst)

				
				

	return judgeInstances
if __name__ == "__main__":	

	dataFileName = os.path.join('..','Data','judges','judges.csv')
	judgeInstances = findActivePeriods(dataFileName,byYear=True)
	print(judgeInstances['U.S. District Court for the District of Massachusetts'][2002])

