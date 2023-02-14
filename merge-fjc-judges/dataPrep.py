import os
import sys
import csv
import random

import importlib # adapted for Python 3
importlib.reload(sys) # added for Python 3
sys.path.append(os.getcwd() + '/merge-fjc-judges')
# sys.setdefaultencoding('utf-8') # removed for Python 3, since the default on Python 3 is UTF-8
import caseClass
import helpers
import io
import json
from findActiveJudgePeriods import findActivePeriods

def createJudgePermutations(judgeInstances):

	#we will generate a list of lists of permuted within each circuit judge attributes to use as pseudo data later for the topic modeling
	judgePartyPermutations = {}
	judgeGenderPermutations = {}
	judgeRacePermutations = {}

	for circuitName in judgeInstances:
		judgePartyPermutations[circuitName] = []
		judgeGenderPermutations[circuitName] = []
		judgeRacePermutations[circuitName] = []



		judgeParties = [j.party for j in judgeInstances[circuitName]]
		for i in range(numPermsToGeneratePerAttribute):
			judgePartyPermutations[circuitName].append(random.sample(judgeParties,len(judgeParties)))

		judgeGenders = [j.gender for j in judgeInstances[circuitName]]
		for i in range(numPermsToGeneratePerAttribute):
			judgeGenderPermutations[circuitName].append(random.sample(judgeGenders,len(judgeGenders)))

		judgeRaces = [j.race for j in judgeInstances[circuitName]]
		for i in range(numPermsToGeneratePerAttribute):
			judgeRacePermutations[circuitName].append(random.sample(judgeRaces,len(judgeRaces)))


	return judgePartyPermutations,judgeGenderPermutations,judgeRacePermutations

def createCSVs(outPutDir,procYears,circuitList,judgeFileName,dataFolder,resultsSummaryFileName,numPermsToGeneratePerAttribute,permOutFileName,textLengthsFileName):

	helpers.maybeMakeDirStructure(outPutDir)

	judgeInstances = findActivePeriods(judgeFileName,minYear=procYears[0]-5)

	judgePartyPermutations,judgeGenderPermutations,judgeRacePermutations = createJudgePermutations(judgeInstances)

	with open(permOutFileName,'w') as permFile:
		permCSV =  csv.writer(permFile)
		permHeaders =['judge']
		for i in range(numPermsToGeneratePerAttribute):
			permHeaders.append('permutedParty'+str(i+1))
		for i in range(numPermsToGeneratePerAttribute):
			permHeaders.append('permutedGender'+str(i+1))
		for i in range(numPermsToGeneratePerAttribute):
			permHeaders.append('permutedRace'+str(i+1))


		permCSV.writerow(permHeaders)

		writeJudgeAttPermFile(judgeInstances,permCSV,judgePartyPermutations,judgeGenderPermutations,judgeRacePermutations)

		with open(resultsSummaryFileName,'w') as resultsSummaryFile, open(textLengthsFileName,'w') as textLengthsFile:

			textLengthCSV = csv.writer(textLengthsFile)
			for circuitName in circuitList:
				print('creating file for ' + circuitName)
				createCircuitCSV(circuitName,outPutDir,judgeInstances,dataFolder,resultsSummaryFile,numPermsToGeneratePerAttribute,permCSV,
					textLengthCSV,judgePartyPermutations,judgeGenderPermutations,judgeRacePermutations)


def writeJudgeAttPermFile(judgeInstances,permCSV,judgePartyPermutations,judgeGenderPermutations,judgeRacePermutations):

	for circuitName in judgeInstances:
		for permJudge in judgeInstances[circuitName]:
			judgePermOutRow = [permJudge]

			for permNum in range(numPermsToGeneratePerAttribute):
				judgePermOutRow.append(permJudge.partyCodes[judgePartyPermutations[circuitName][permNum][judgeInstances[circuitName].index(permJudge)]])

			for permNum in range(numPermsToGeneratePerAttribute):
				judgePermOutRow.append(permJudge.genderCodes[judgeGenderPermutations[circuitName][permNum][judgeInstances[circuitName].index(permJudge)]])

			for permNum in range(numPermsToGeneratePerAttribute):
				if judgeRacePermutations[circuitName][permNum][judgeInstances[circuitName].index(permJudge)] in permJudge.raceCodes:
					judgePermOutRow.append(permJudge.raceCodes[judgeRacePermutations[circuitName][permNum][judgeInstances[circuitName].index(permJudge)]])
				else:
					judgePermOutRow.append(permJudge.raceCodes['Other'])



			permCSV.writerow(judgePermOutRow)


def createCircuitCSV(circuitName,outPutDir,judgeInstances,dataFolder,resultsSummaryFile,numPermsToGeneratePerAttribute,permCSV,textLengthCSV,
						judgePartyPermutations,judgeGenderPermutations,judgeRacePermutations):

	minCaseCharactersForSTM = 900

	circuitNameShort= circuitLongToShort[circuitName]

	stmOutFileName = os.path.join(outPutDir,circuitNameShort + 'DataForCOA.csv')

	resultsSummaryFile.write(circuitName + ':\n')




	with open(stmOutFileName,'w') as stmFile:

		stmCSVFile = csv.writer(stmFile,quoting=csv.QUOTE_ALL)


		headerRow = ['', 'filename', 'caseTitle', 'judge_parties_list','judge_gender_list','judge_races_list','judge_races_fulltext','judges_births_list', 'year_filed',
					'circuitNum','judge_names','us_party','corp_party','len_text','includeInSTM','author','type','text','reporter','headMatter','docket_number',
					 'decision_date','court_name_abbv','court_name','court_id','citations','panel_ideology',
					 'judge_birth_year','judge_elite',
					 'court_type1','court_type2','court_type3','court_type4','court_type5','court_type6',
					 'commission_date1','commission_date2','commission_date3','commission_date4','commission_date5','commission_date6',
					 'court_name1','court_name2','court_name3','court_name4','court_name5','court_name6',
					 'chief11','chief12', 'chief21','chief22', 'chief31','chief32','chief41','chief42','chief51','chief52','chief61','chief62',
					 'chief11e', 'chief12e', 'chief21e', 'chief22e', 'chief31e', 'chief32e', 'chief41e', 'chief42e', 'chief51e',
					 'chief52e', 'chief61e', 'chief62e',
					 'senior1','senior2','senior3','senior4','senior5','senior6']

		for i in range(numPermsToGeneratePerAttribute):
			headerRow.append('permutedParty'+str(i+1))
		for i in range(numPermsToGeneratePerAttribute):
			headerRow.append('permutedGender'+str(i+1))
		for i in range(numPermsToGeneratePerAttribute):
			headerRow.append('permutedRace'+str(i+1))


		stmCSVFile.writerow(headerRow)

		rownum = 1
		totalCaseCount = 0
		matchedCircuit=0
		not3JudgeCount = 0

		for fname in os.listdir(dataFolder):

			year = int(fname[:4])
			if year not in procYears:
				continue

			dataJsonName = os.path.join(dataFolder,fname)

			with io.open(dataJsonName,encoding='UTF-8') as jsonFile:

				fileType = dataJsonName.split('/')[-1][4:-5]

				allLines = jsonFile.readlines()

				lineCount=0
				for line in allLines:
					lineCount+=1
					totalCaseCount+=1
					dataJson = json.loads(line)

					caseInst = caseClass.case(dataJson)


					if caseInst.circuitNum!=circuitName:
						continue

					matchedCircuit +=1
					caseInst.assignJudges(judgeInstances[caseInst.circuitNum],secondaryJudgeLists=judgeInstances)

					caseInst.removeTextHeaders()
					caseInst.assignUSParty()
					caseInst.assignCorpParty()


					#skip cases where we couldn't identify 3 judges
					if len(caseInst.caseJudges)!=3:
						not3JudgeCount +=1
						with open('not3judge_dates.csv', 'a') as file:
							fileCSV = csv.writer(file)
							fileCSV.writerow([caseInst.decision_date,caseInst.dataBaseJudges, caseInst.opinionFileName, caseInst.caseJudges, caseInst.docket_number])
						continue

					outputJudges = [c.fullName for c in caseInst.caseJudges]


					includeInSTM = 0
					if len(caseInst.cleanText)>minCaseCharactersForSTM:
						includeInSTM = 1

					headerRow = ['', 'filename', 'caseTitle', 'judge_parties_list', 'judge_gender_list',
								 'judge_races_list', 'judge_races_fulltext', 'judges_births_list', 'year_filed',
								 'circuitNum', 'judge_names', 'us_party', 'corp_party', 'len_text', 'includeInSTM',
								 'author', 'type', 'text', 'reporter', 'headMatter', 'docket_number',
								 'decision_date', 'court_name_abbv', 'court_name', 'court_id', 'citations',
								 'panel_ideology',
								 'judge_birth_year', 'judge_elite',
								 'court_type1', 'court_type2', 'court_type3', 'court_type4', 'court_type5',
								 'court_type6',
								 'commission_date1', 'commission_date2', 'commission_date3', 'commission_date4',
								 'commission_date5', 'commission_date6',
								 'court_name1', 'court_name2', 'court_name3', 'court_name4', 'court_name5',
								 'court_name6',
								 'chief11', 'chief12', 'chief21', 'chief22', 'chief31', 'chief32', 'chief41', 'chief42',
								 'chief51', 'chief52', 'chief61', 'chief62',
								 'chief11e', 'chief12e', 'chief21e', 'chief22e', 'chief31e', 'chief32e', 'chief41e',
								 'chief42e', 'chief51e',
								 'chief52e', 'chief61e', 'chief62e',
								 'senior1', 'senior2', 'senior3', 'senior4', 'senior5', 'senior6']
					outRow = [rownum,caseInst.opinionFileName,caseInst.caseTitle,
							  # caseInst.cleanText,
							  caseInst.getJudgePartiesList(),caseInst.getJudgeGendersList(),
									caseInst.getJudgeRacesList(),caseInst.getJudgeRacesFullText(),caseInst.getJudgeBirthsList(),caseInst.yearFiled,circuitLongToShort[caseInst.circuitNum],caseInst.getJudgeNames(),
									caseInst.USParty,caseInst.corpParty,len(caseInst.cleanText),includeInSTM,caseInst.author,caseInst.type, caseInst.text,
							  caseInst.reporter , caseInst.headMatter , caseInst.docket_number ,caseInst.decision_date ,caseInst.court_name_abbv ,
							  caseInst.court_name , caseInst.court_id , caseInst.citations,caseInst.get_panel_ideology(), caseInst.get_birth_year(), caseInst.get_judge_elite(),
							  caseInst.get_judge_data_generic(getVar="court_type1"),caseInst.get_judge_data_generic(getVar="court_type2"),caseInst.get_judge_data_generic(getVar="court_type3"),caseInst.get_judge_data_generic(getVar="court_type4"),caseInst.get_judge_data_generic(getVar="court_type5"),caseInst.get_judge_data_generic(getVar="court_type6"),
							  caseInst.get_judge_data_generic(getVar="commission_date1"),caseInst.get_judge_data_generic(getVar="commission_date2"),caseInst.get_judge_data_generic(getVar="commission_date3"),caseInst.get_judge_data_generic(getVar="commission_date4"),caseInst.get_judge_data_generic(getVar="commission_date5"),caseInst.get_judge_data_generic(getVar="commission_date6"),
							  caseInst.get_judge_data_generic(getVar="court_name1"),caseInst.get_judge_data_generic(getVar="court_name2"),caseInst.get_judge_data_generic(getVar="court_name3"),caseInst.get_judge_data_generic(getVar="court_name4"),caseInst.get_judge_data_generic(getVar="court_name5"),caseInst.get_judge_data_generic(getVar="court_name6"),
							  caseInst.get_judge_data_generic(getVar="chief11"),caseInst.get_judge_data_generic(getVar="chief12"),caseInst.get_judge_data_generic(getVar="chief21"),caseInst.get_judge_data_generic(getVar="chief22"),caseInst.get_judge_data_generic(getVar="chief31"),caseInst.get_judge_data_generic(getVar="chief32"),
							  caseInst.get_judge_data_generic(getVar="chief41"),caseInst.get_judge_data_generic(getVar="chief42"),caseInst.get_judge_data_generic(getVar="chief51"),caseInst.get_judge_data_generic(getVar="chief52"),caseInst.get_judge_data_generic(getVar="chief61"),caseInst.get_judge_data_generic(getVar="chief62"),
							  caseInst.get_judge_data_generic(getVar="chief11e"),caseInst.get_judge_data_generic(getVar="chief12e"),caseInst.get_judge_data_generic(getVar="chief21e"),caseInst.get_judge_data_generic(getVar="chief22e"),caseInst.get_judge_data_generic(getVar="chief31e"),caseInst.get_judge_data_generic(getVar="chief32e"),caseInst.get_judge_data_generic(getVar="chief41e"),caseInst.get_judge_data_generic(getVar="chief42e"),caseInst.get_judge_data_generic(getVar="chief51e"),caseInst.get_judge_data_generic(getVar="chief52e"),caseInst.get_judge_data_generic(getVar="chief61e"),caseInst.get_judge_data_generic(getVar="chief62e"),
							  caseInst.get_judge_data_generic(getVar="senior1"),caseInst.get_judge_data_generic(getVar="senior2"),caseInst.get_judge_data_generic(getVar="senior3"),caseInst.get_judge_data_generic(getVar="senior4"),caseInst.get_judge_data_generic(getVar="senior5"),caseInst.get_judge_data_generic(getVar="senior6")]

					#add the permuted party data to the row before we write it

					for permNum in range(numPermsToGeneratePerAttribute):
						permJudgeList = []
						for nextJudge in caseInst.caseJudges:
							permJudgeList.append(judgePartyPermutations[nextJudge.circuit][permNum][judgeInstances[nextJudge.circuit].index(nextJudge)])
						outRow.append(caseInst.getJudgePartiesList(judgeParties=permJudgeList))


					for permNum in range(numPermsToGeneratePerAttribute):
						permJudgeList = []
						for nextJudge in caseInst.caseJudges:
							permJudgeList.append(judgeGenderPermutations[nextJudge.circuit][permNum][judgeInstances[nextJudge.circuit].index(nextJudge)])

						outRow.append(caseInst.getJudgeGendersList(judgeGenders=permJudgeList))


					for permNum in range(numPermsToGeneratePerAttribute):
						permJudgeList = []
						for nextJudge in caseInst.caseJudges:
							permJudgeList.append(judgeRacePermutations[nextJudge.circuit][permNum][judgeInstances[nextJudge.circuit].index(nextJudge)])
						
						outRow.append(caseInst.getJudgeRacesList(judgeRaces=permJudgeList))


					stmCSVFile.writerow(outRow)
					textLengthCSV.writerow([len(str(caseInst.cleanText))])
					rownum += 1


		resultsSummaryFile.write('Total Cases: ' + str(totalCaseCount) +'\n')
		resultsSummaryFile.write('matchedCircuit: ' + str(matchedCircuit)+'\n')
		resultsSummaryFile.write('Not 3 judges: ' + str(not3JudgeCount)+'\n')
		resultsSummaryFile.write('Usable Cases: ' + str(rownum-1) +'\n'+'\n')



if __name__ == "__main__":
	print("Adding judge-panel level variables to data")
	#seed the random generator so future runs are consistent with reported results
	random.seed(12345)
	working_dir = sys.argv[1]
	outPutDir = os.path.join(working_dir, 'output_dir', 'coaCSV')

	dataFolder = os.path.join(working_dir, 'output_dir', 'Data', 'yearData')

	# procYears = range(2001,2002) # use this to process test smaller amounts of data
	procYears = range(2001, 2018)

	numPermsToGeneratePerAttribute = 0

	#
	resultsSummaryFileName = os.path.join(working_dir, 'output_dir', 'Results', 'dataPrepResults.txt')
	textLengthsFileName = os.path.join(working_dir, 'output_dir', 'Results', 'caseTextLengths.csv')

	permOutFileName = os.path.join(working_dir, 'output_dir', 'permData', 'judgeAttPermutations.csv')


	circuitList = ['U.S. Court of Appeals for the District of Columbia Circuit',
							'U.S. Court of Appeals for the First Circuit',
							'U.S. Court of Appeals for the Second Circuit',
							'U.S. Court of Appeals for the Third Circuit',
							'U.S. Court of Appeals for the Fourth Circuit',
							'U.S. Court of Appeals for the Fifth Circuit',
							'U.S. Court of Appeals for the Sixth Circuit',
							'U.S. Court of Appeals for the Seventh Circuit',
							'U.S. Court of Appeals for the Eighth Circuit',
							'U.S. Court of Appeals for the Ninth Circuit',
							'U.S. Court of Appeals for the Tenth Circuit',
							'U.S. Court of Appeals for the Eleventh Circuit']


	circuitLongToShort = {'U.S. Court of Appeals for the District of Columbia Circuit':'cadc',
							'U.S. Court of Appeals for the Federal Circuit':'cafc',
							'U.S. Court of Appeals for the First Circuit':'ca1',
							'U.S. Court of Appeals for the Second Circuit':'ca2',
							'U.S. Court of Appeals for the Third Circuit':'ca3',
							'U.S. Court of Appeals for the Fourth Circuit':'ca4',
							'U.S. Court of Appeals for the Fifth Circuit':'ca5',
							'U.S. Court of Appeals for the Sixth Circuit':'ca6',
							'U.S. Court of Appeals for the Seventh Circuit':'ca7',
							'U.S. Court of Appeals for the Eighth Circuit':'ca8',
							'U.S. Court of Appeals for the Ninth Circuit':'ca9',
							'U.S. Court of Appeals for the Tenth Circuit':'ca10',
							'U.S. Court of Appeals for the Eleventh Circuit':'ca11'}

	judgeFileName = os.path.join(working_dir, 'output_dir', 'judges',
								 'FJC_alljudge_clean_ideology.csv')

	createCSVs(outPutDir,procYears,circuitList,judgeFileName,dataFolder,resultsSummaryFileName,numPermsToGeneratePerAttribute,permOutFileName,textLengthsFileName)




