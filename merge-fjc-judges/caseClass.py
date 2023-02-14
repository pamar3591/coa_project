#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from bs4 import BeautifulSoup
import helpers
import sys
import re
import string

#This class holds information associated with a single case in our corpus

class case(object):
   

    def __init__(self,caseJSON):
        
        onlyMajorityText = True

        self.opinionFileName = caseJSON['id']
        self.court_name = caseJSON['court']['name']
        self.circuitNum = caseJSON['court']['name'].replace('United ','U.').replace('States','S.')

    
        #We'll standardize here
        if (self.circuitNum == 'U.S. Circuit Court of the District of Columbia' or
            self.circuitNum =='U.S. Court of Appeals for the District of Columbia' or
            self.circuitNum == 'U.S. Court of Appeals, District of Columbia Circuit' or
            self.circuitNum == 'U.S. Court of Appeals for the District of Columbia Circuit'):

            self.circuitNum = 'U.S. Court of Appeals for the District of Columbia Circuit'

        self.caseJudges = None
        self.cleanText = ''
        
        opinions = caseJSON['casebody']['data']['opinions']
        authors = ''
        type = ''
        text = ''
        for opinion in opinions:
            opinion_author = opinion['author']
            opinion_type = opinion['type']
            opinion_text = opinion['text'].replace('”','"').replace('’',"'").replace('“','"').replace("‘","'").replace('\n',' ').replace('\t',' ') + ' '

            # Run again for type (produce files again)
            type = type + ';' + str(opinion_type)
            text = text + ';opinion_text_begin' + str(opinion_text)
            authors = authors + ';' + str(opinion_author)
        self.author = authors
        self.type = type
        self.text = text
        

        self.cleanText = self.cleanText.replace('\n',' ').replace('\t',' ')
        self.yearFiled = int(caseJSON['decision_date'].split('-')[0])
        self.headMatter = caseJSON['casebody']['data']['head_matter']
        self.dataBaseJudges = caseJSON['casebody']['data']['judges']
        self.caseTitle = caseJSON['name_abbreviation']
        
        self.reporter = caseJSON['reporter']
        self.citations = caseJSON['citations']
        self.court_id = caseJSON['court']['id']

        self.court_name_abbv = caseJSON['court']['name_abbreviation']
        self.decision_date = caseJSON['decision_date']
        self.docket_number = caseJSON['docket_number']
        self.citationNum =caseJSON['citations'][0]['cite']
        self.headMatter = caseJSON['casebody']['data']['head_matter']

        correctCourtLookups={'district of columbia circuit':'U.S. Court of Appeals for the District of Columbia Circuit',
                                'first circuit':'U.S. Court of Appeals for the First Circuit',
                                'second circuit':'U.S. Court of Appeals for the Second Circuit',
                                'third circuit':'U.S. Court of Appeals for the Third Circuit',
                                'fourth circuit':'U.S. Court of Appeals for the Fourth Circuit',
                                'fifth circuit':'U.S. Court of Appeals for the Fifth Circuit',
                                'sixth circuit':'U.S. Court of Appeals for the Sixth Circuit',
                                'seventh circuit':'U.S. Court of Appeals for the Seventh Circuit',
                                'eighth circuit':'U.S. Court of Appeals for the Eighth Circuit',
                                'ninth circuit':'U.S. Court of Appeals for the Ninth Circuit',
                                'tenth circuit':'U.S. Court of Appeals for the Tenth Circuit',
                                'eleventh circuit':'U.S. Court of Appeals for the Eleventh Circuit',
                                }
        checkNext=False
        for line in self.headMatter.split('\n'):
            if checkNext:
                checkNext=False
                for convertToCorrectCourtKey in correctCourtLookups:
                    if convertToCorrectCourtKey in line.lower():
                        self.circuitNum=correctCourtLookups[convertToCorrectCourtKey]
            if len(line)>4 and line[:4] == 'No. ' or line[:5] == 'Nos. ':
                checkNext=True
    
    def __str__(self):
        return str(self.opinionFileName) + ' Title: ' + str(self.caseTitle) + ' Judges: ' + str(self.caseJudges) +' Year: ' +str(self.yearFiled) + ' Circuit: ' +str(self.circuitNum)
    def __repr__(self):
        return str(self.opinionFileName) + ' Title: ' + str(self.caseTitle) + ' Judges: ' + str(self.caseJudges) +' Year: ' +str(self.yearFiled) + ' Circuit: ' +str(self.circuitNum)
    
    #uses cleanText and judgeList to try to find the judges on this case.
    def assignJudges(self, judgeList,secondaryJudgeLists=None):

        if str(self.opinionFileName)=='none currently':
            
            self.caseJudges = helpers.findJudges(self.headMatter, judgeList, self.yearFiled,self.circuitNum,debugOut=True,secondaryJudgeLists=secondaryJudgeLists)
            quit()
        else:
        
            self.caseJudges = helpers.findJudges(self.headMatter, judgeList, self.yearFiled,self.circuitNum,debugOut=False,secondaryJudgeLists=secondaryJudgeLists)


        
        #if we didn't find a full panel of judges in the headmatter, see if we can find any in the judges list in metadata
        if len(self.caseJudges)<3:
        
            dbCaseJudges = helpers.findJudges('before ' + ' '.join(self.dataBaseJudges), judgeList, self.yearFiled,self.circuitNum,debugOut=False,secondaryJudgeLists=secondaryJudgeLists)

            if len(dbCaseJudges)>len(self.caseJudges):
                self.caseJudges = dbCaseJudges
            
    def removeTextHeaders(self):

        judgeLastNames = [j.lastName.upper() for j in self.caseJudges]
        self.cleanText = helpers.removeCaseHeaders(self.cleanText,judgeLastNames)

    #uses the title of the case to identify if the US is one of exactly two parties involved in the case
    def assignUSParty(self):
        self.USParty = False

        caseBetween = self.caseTitle.split(' v. ')
        stripPunctRE = re.compile('[%s]' % re.escape(string.punctuation))
        if len(caseBetween) == 2:
            
            if (stripPunctRE.sub(' ',caseBetween[0].strip().lower()) == 'united states' or stripPunctRE.sub(' ',caseBetween[0].strip().lower()) == 'united states of america' or
                        stripPunctRE.sub(' ',caseBetween[1].strip().lower()) == 'united states' or stripPunctRE.sub(' ',caseBetween[1].strip().lower()) == 'united states of america' ):
                self.USParty = True


    #uses title of the case to identify if a corporation is a party on the case
    def assignCorpParty(self):
        self.corpParty =  False
        corpTitleWords =['llc','inc','incorporated','co','corp','corporation','ltd','llp','company']

        stripPunctRE = re.compile('[%s]' % re.escape(string.punctuation))
        cleanCaseTitle = stripPunctRE.sub(' ',self.caseTitle.lower())
        cleanTitleWords = cleanCaseTitle.split(' ')

        if len([word for word in corpTitleWords if (word in cleanTitleWords or word+'.' in cleanTitleWords)]) >0:
            self.corpParty = True

    #creates a plain text version of the opinion's html and stores it in cleanText
    def assignCleanText(self):
        self.cleanText = self.soup.get_text().strip()

    #goes through clean text and removes all occurrences of the names of U.S. states, judges, 'united','states','america', and corporation words from the case.
    #Removes only if they appear as a whole word or followed by an "'s" (which covers possessive usage)
    def removeTargetWordsFromText(self):
        judgeLastNames = [j.lastName.lower() for j in self.caseJudges]
        judgeFirstNames = [j.firstName.lower() for j in self.caseJudges]
        judgeNames = judgeFirstNames+judgeLastNames
        usWords = ['united','states','america']
        corpWords = ['llc','inc','incorporated','co','corp','corporation','ltd','llp','company']

        stateNames = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia',
                        'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts',
                        'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey',
                        'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island',
                        'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia',
                        'wisconsin', 'wyoming','columbia']

        targetWords = judgeNames+usWords+corpWords+stateNames

        cleanWordList = re.split('(\s|,|\.)+',self.cleanText)
        stripPunctRE = re.compile('[%s]' % re.escape(string.punctuation))
        remainingWords = []

        #go through the text one word at a time
        for wordInd in range(len(cleanWordList)):
            curWord = cleanWordList[wordInd]

            #strip off "'s" if its there
            if len(curWord) >2 and curWord[-2:] =='\'s':
                curWord=curWord[:-2]

            #replace all punctuation and remove any whitespace
            curWord = stripPunctRE.sub('',curWord.lower()).replace(' ','')

            #if the word isn't one we want to remove
            if curWord not in targetWords:
                if wordInd<len(cleanWordList)-1:

                    #grab the next word too, so we can check for two word state names
                    nextWord = cleanWordList[wordInd+1]

                    #strip off "'s" if its there
                    if len(nextWord) >2 and nextWord[-2:] =='\'s':
                        nextWord=nextWord[:-2]

                    nextWord = stripPunctRE.sub('',nextWord.lower()).replace(' ','')
                #and if the combination of the word and the next word isn't in our list
                if wordInd>=len(cleanWordList)-1 or curWord + ' ' + nextWord not in targetWords:
                    #add the word to our "kept" words list
                    remainingWords.append(cleanWordList[wordInd])
        self.cleanText = ' '.join(remainingWords)
        self.cleanText = re.sub(' +',' ', self.cleanText)


    #returns number of bytes that would be in a file containing cleanText
    def getTextSize(self):
        return sys.getsizeof(unidecode(self.cleanText))
        
    def get_panel_ideology(self, panelIdeology=None):

        if panelIdeology == None:
            panelIdeology = [j.ideology for j in self.caseJudges]

        fileIdeology = [jp for jp in panelIdeology]

        return fileIdeology

    def get_birth_year(self, birthYear=None):

        if birthYear == None:
            birthYear = [j.birth_year for j in self.caseJudges]

        filebirthYear = [jp for jp in birthYear]

        return filebirthYear

    def get_judge_elite(self, elite=None):
        if elite == None:
            elite = [j.judge_elite for j in self.caseJudges]
        fileJudgeElite = [jp for jp in elite]
        return fileJudgeElite

    def get_judge_data_generic(self, getVar,var=None):
        if var == None:
            var = [getattr(j, getVar) for j in self.caseJudges]
        fileData = [jp for jp in var]
        return fileData


    #returns a list of the parties of the judges
    def getJudgePartiesList(self,judgeParties=None):
        partyCodes = {'Republican':'0','Democratic':'1'}
        if judgeParties==None:
            judgeParties=[j.party for j in self.caseJudges]

        fileParties = [partyCodes[jp] for jp in judgeParties]
        
        return fileParties

    def getJudgeGendersList(self,judgeGenders=None):
        genderCodes = {'Male':'0','Female':'1'}
        if judgeGenders==None:
            judgeGenders = [j.gender for j in self.caseJudges]
        fileGenders = [genderCodes[jg] for jg in judgeGenders]

        return fileGenders

    def getJudgeRacesList(self,judgeRaces=None):
        raceCodes = {'White':'0','Other':'1'}
        if judgeRaces==None:
            judgeRaces = [j.race for j in self.caseJudges]
        fileRaces = []
        for jr in judgeRaces:
            if jr in raceCodes:
                fileRaces.append(raceCodes[jr])
            else:
                fileRaces.append(raceCodes['Other'])
        return fileRaces

    def getJudgeRacesFullText(self):
        judgeRaces = [j.race for j in self.caseJudges]
        return judgeRaces
        
    def getJudgeBirthsList(self,judgeBirths=None):
        birthCodes = {'0':0,'1':1}
        if judgeBirths==None:
            judgeBirths = [j.birthCode for j in self.caseJudges]
        fileBirths = [birthCodes[jg] for jg in judgeBirths]

        return fileBirths

    #returns a string of the names of the judges
    def getJudgeNames(self):
        fileJudgeNames = ''
        for judge in self.caseJudges:
            fileJudgeNames += judge.lastName+ ' ' + judge.firstName +', '
        return fileJudgeNames[:-2]

