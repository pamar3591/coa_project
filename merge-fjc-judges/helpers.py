# -*- coding: utf-8 -*-
import os
import judgeClass
import unidecode
import re
import pandas
import numpy as np
import csv
csv.field_size_limit(3000000)
#contains methods which are generally useful for our analysis and are referenced by multiple files.  Not meant to be run directly
"""
circList = ['U.S. Court of Appeals for the District of Columbia Circuit',
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


"""
#Reads dataFileName which should be the judges csv.  Creates and returns a dictionary of circuit names as keys and lists of
#instances of judgeClass as the values
#if byYear=True there is an extra layer in dictionary so it is circuit->year->list of judgeClass
#only restriction on dates for judge is commission date and termination date, i.e. senior judges, chief judges etc, are
#included in the lists
"""
def findActivePeriods(dataFileName,minYear=1950,byYear=False,maxYear=2019):

    judgeData = pandas.read_csv(dataFileName)
    judgeData = judgeData.replace(np.nan, '', regex=True)
    judgeRecords = judgeData.to_dict('records')
    
    judgeInstances = {}
    for judgeRow in judgeRecords:
        for apptNum in range(1,7):

            apptStrMod = ' (' + str(apptNum) + ')'
            if (judgeRow['Court Type'+ apptStrMod] == 'U.S. Court of Appeals' or judgeRow['Court Type'+ apptStrMod] =='U.S. District Court' or
                    judgeRow['Court Type'+ apptStrMod] == 'Other' or judgeRow['Court Type'+ apptStrMod] == 'Supreme Court'):
                
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
                birth = str(int(judgeRow['Birth Year']))

                firstName = judgeRow['First Name'].strip()
                lastName = judgeRow['Last Name'].strip().split(' ')[-1].strip()

                middleName = judgeRow['Middle Name'].strip()
                suffix = str(judgeRow['Suffix']).strip()

                fullName = lastName + '<' +' ' +firstName
                if middleName!='':
                    fullName=fullName+' ' + middleName
                if suffix!='':
                    fullName=fullName+' ' + suffix

                judgeInst = judgeClass.judge(circuit,start,end,party,gender,race,birth,fullName,lastName,firstName,seniorStart=senior,
                                                chiefStart=chiefStart,chiefEnd=chiefEnd,middleName=middleName)

                
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
"""
#checks if path dirPath exists and if not makes it and any higher level directories needed
def maybeMakeDirStructure(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

def findJudgePanelsCirc(circFileName,judgeList,yearRange):

    judgePanels = {}
    for year in yearRange:
        judgePanels[year] = {}

    with open(circFileName,'rb') as circFile:
        circFileCSV = csv.reader(circFile)
        circHeaders = circFileCSV.next()
        for line in circFileCSV:
            if line[circHeaders.index('year')].strip().isdigit() and int(line[circHeaders.index('year')].strip()) in yearRange:

                year = int(line[circHeaders.index('year')])
                judges = line[circHeaders.index('judges')].split(',')
                
                #for each judge on the case
                judgesOnCase = []

                for lj in [j.strip() for j in judges]:
                    #for each judge active in the case's year
                    for pj in [j for j in judgeList if j.start-1<=year and j.end+1>=year]:

                        if pj.lastName == lj.split(' ')[0].strip() and pj.firstName == lj.split(' ')[1].strip():

                            judgesOnCase.append(pj)
                            #since we were getting an error for Robert Wilkins in 2014 when he was on a
                            #district court and later the circuit court, just take the first judge with a name match
                            break
                if len(judgesOnCase)!=3:
                    print('wrong number of judges identified for ' + str(judges) + ' year: ' + str(year))
                    print(judgesOnCase)
                    quit()
                judgesOnCase = sorted(judgesOnCase)
                judgesOnCase = (judgesOnCase[0],judgesOnCase[1],judgesOnCase[2])
                if judgesOnCase not in judgePanels[year]:
                    judgePanels[year][judgesOnCase] = 0
                judgePanels[year][judgesOnCase] = judgePanels[year][judgesOnCase] + 1
    return judgePanels
    
    
    
def removeCaseHeaders(caseText,judgeLastNames):

    caseWords = caseText.split(' ')
    modifiedCaseText=caseText


    headerEndingRoots = ['ORDERED','CURIAM','MEMORANDUM','ORDER','ADJUDGED','DECREED','AFFIRMED']
    headerEndingWords = []
    for endRoot in headerEndingRoots:
        headerEndingWords.append(endRoot)
        headerEndingWords.append(endRoot+'.')
        headerEndingWords.append(endRoot+':')

    #for wordIndex in range(len(caseWords)/2):
    for wordIndex in range(min(int(len(caseWords)/2),100)):
        checkWord = caseWords[wordIndex]

        judgeCheckWord = caseWords[wordIndex].replace(',','')

        #since some names, like McKEE appear in the case text with a single lower case letter, lets try to correct that
        if sum(1 for c in judgeCheckWord if c.islower())==1:
            judgeCheckWord=judgeCheckWord.upper()

        if checkWord in headerEndingWords:
            stillCapIndex = wordIndex
            while caseWords[stillCapIndex].isupper():
                stillCapIndex+=1
            modifiedCaseText=' '.join(caseWords[stillCapIndex:])

        if judgeCheckWord in judgeLastNames:
            modIndex=wordIndex+1
            while modIndex<wordIndex+5 and caseWords[modIndex].lower() not in ['judge','judge.','judge:'] and caseWords[modIndex][-1]!=':':
                modIndex+=1
            if modIndex<wordIndex+5:
                modifiedCaseText = ' '.join(caseWords[modIndex+1:])


    return modifiedCaseText


#looks through file text and identifies the judges on the case
#it considers the judges in judgeList(who should only be judges from the circuit of this case) who were active within 1 year of fileYear
#also will try to use secondaryJudgeLists if needed (this has people who may be sitting by designation)
def findJudges(fileText, judgeList, fileYear,fileCirc, windowSize=40,debugOut=False,secondaryJudgeLists=None,suspectDesignation=False):
        
    ignoreJudgeWords= ['u.s','court','of','for','customs','patent','appeals','united','states','southern','northern','eastern','western']
    
    
    ignoreJudgeWords = ignoreJudgeWords + ['justice','justices','supreme']

    #suffixes might be a problem, lets try to remove them here
    ignoreJudgeWords = ignoreJudgeWords + ['iii','jr.','sr.','iv']

    #find all judges who were active during this cases year that we should consider searching for
    potentialFileJudges = [judge for judge in judgeList if judge.start <= fileYear+1 and judge.end >=fileYear-1]

    if secondaryJudgeLists!=None:
        secondaryPotFileJudges = []
        for desCirc in secondaryJudgeLists:
            for desJudge in secondaryJudgeLists[desCirc]:
                if desJudge.start<= fileYear+1 and desJudge.end >=fileYear-1:
                    secondaryPotFileJudges.append(desJudge)


    ogFileText = fileText

    #replace tab to make splitting easier
    fileText = fileText.replace('\t',' ')

    #put a space before these brackets that are used to mark notes and around commas, semicolons, asterisks, and parentheses
    fileText = fileText.replace('[',' [').replace(',',' , ').replace(';',' ; ').replace('(',' (').replace('*',' * ').replace('’',"'")
    fileText = fileText.replace('"',"'")
    fileText=fileText.replace("' ","'").replace('1','i').replace('0','o').replace('designalion','designation')

    
    #sometimes spaces are missing around judge last names, causing them to not be caught.
    #Fix cases that appear to be a last name combined with "and" or period etc.
    foundCombTok=False
    for maybeCombinedToken in fileText.split(' '):
        

        if len(maybeCombinedToken)>6 and (maybeCombinedToken[-4:]=='.and' or maybeCombinedToken[-4:]=="'and"
                                            or maybeCombinedToken[-4:]=="-and") and maybeCombinedToken[:-4].isupper():

            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[:-4] + ' ' + 'and')
            foundCombTok=True

        if len(maybeCombinedToken)>5 and maybeCombinedToken[-3:]=='and' and maybeCombinedToken[:-3].isupper():

            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[:-3] + ' ' + 'and')
            foundCombTok=True
            
        if len(maybeCombinedToken)>3 and (maybeCombinedToken[-1:]=='.') and maybeCombinedToken[:-1].isupper() and maybeCombinedToken.count('.')==1:
            
            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[:-1] )
            foundCombTok=True

        if len(maybeCombinedToken)>3 and (maybeCombinedToken[-1:]=="'") and maybeCombinedToken[:-1].isupper():
            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[:-1] )
            foundCombTok=True

        if len(maybeCombinedToken)>3 and (maybeCombinedToken[0]=='.') and maybeCombinedToken[1:].isupper() and maybeCombinedToken.count('.')==1:
            
            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[1:] )
            foundCombTok=True

        if len(maybeCombinedToken)>3 and (maybeCombinedToken[0]==':') and maybeCombinedToken[1:].isupper() and maybeCombinedToken.count(':')==1:
            
            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[1:] )
            foundCombTok=True

        if len(maybeCombinedToken)>3 and (maybeCombinedToken[0]=="'") and maybeCombinedToken[1:].isupper() and maybeCombinedToken.count("'")==1:
            
            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[1:] )
            foundCombTok=True

        if len(maybeCombinedToken)>6 and (maybeCombinedToken[:4]=='.and' or maybeCombinedToken[:4]=="'and") and maybeCombinedToken[4:].isupper():

            fileText = fileText.replace(maybeCombinedToken,' and' + maybeCombinedToken[4:])
            foundCombTok=True

        if len(maybeCombinedToken)>6 and maybeCombinedToken[:4] =="and'":
            fileText = fileText.replace(maybeCombinedToken,'and ' + maybeCombinedToken[4:])
            foundCombTok=True

        #handle middle initials of judges often having a single quote after the period due to OCR error
        if len(maybeCombinedToken)>=3 and maybeCombinedToken[1:3]==".'":
            fileText = fileText.replace(maybeCombinedToken,maybeCombinedToken[:2]+' ' +maybeCombinedToken[3:])
    
    fileText=fileText.lower()
    if debugOut:
        print(fileText)

    
    #normalize the text used to announce judges
    fileText = fileText.replace("before:'",'before ')
    fileText = fileText.replace("present:",'before ').replace('b e f o r e','before ').replace('.before','before').replace('before:.','before ')
    fileText = fileText.replace('before:','before ').replace('before.','before ').replace("'before",'before ')
    fileText = fileText.replace("before'",'before ').replace("present",'before ').replace('before-','before ')

    #correct a list of typos of judgelast names
    judgeNameCorrectionsTuples = [('kravttch','kravitch'),('higgingson','higginson'), ('manton','manion'), ('hcudahy','cudahy'),
                                     ('mekeague','mckeague'), ('roberta. katzmann','robert a. katzmann'), ('flectcher','fletcher'),
                                     ('bartz','hartz'), ('alarcon','alarcón'), ('saldana','saldaña'), ('roman','román'),
                                     ('sanchez','sánchez'), ('vazquez','vázquez'), ('carreno','carreño'),
                                     ('delgado hernandez','delgado hernández'), ('colon','colón'), ('dominguez','domínguez'),
                                     ('fuste','fusté'), ('gelpi','gelpí'), ('perez','pérez'), ('marquez','márquez')]

    
    
    judgeNameCorrectionsTuples = judgeNameCorrectionsTuples + [('silbe rman','silberman'), ('kayanaugh','kavanaugh'), ('eavanaugh','kavanaugh'),
                                         ('kavanaugu','kavanaugh'), ('griffifth','griffith'), ('sriniyasan','srinivasan'), ('pillará','pillard'),
                                         ('sjlberman','silberman')]

    
    judgeNameCorrectionsTuples = judgeNameCorrectionsTuples +[("porfirio", "porfilio"), ("boocheyer", "boochever"), ("rawlins on", "rawlinson"),
                                        ("suhrheinich", "suhrheinrich"), ("card amone", "cardamone"), ("levad", "leval"),
                                        ("mcmcmillian", "mcmillian"), ("token", "loken"), ("widened", "widener"), ("walace", "wallace"),
                                        ("ward law", "wardlaw"), ("ryajst", "ryan"), ("leayy", "leavy"), ("be lot", "belot"), ("gartpi", "garth"),
                                        ("■selya", "selya"), ("before-tjoflat", "tjoflat"), ("higginbothom", "higginbotham"),
                                        ("browing", "browning"), ("he vans", "evans"), ("memillian", "mcmillian"), ("murphy'", "murphy"),
                                        ("wldener", "widener"), ("royner", "rovner"), ("mekay", "mckay"), ("heaney-and", "heaney"),
                                        ("yining", "vining"), ("sckwarzer", "schwarzer"), ("ungaro-benages", "ungaro"),
                                        ("daughtrey-", "daughtrey"), ("cambpell", "campbell"), ("running", "banning"), ("hbauer", "bauer"),
                                        ("thomas find", "thomas"), ("tymkovtch", "tymkovitch"), ("heasterbrook", "easterbrook"),
                                        ("ajsíderson", "anderson"), ("mekee", "mckee"), ("wtdener", "widener"), ("slovtter", "sloviter"),
                                        ("barrsdale", "barksdale"), ("fago", "fagg"), ("mewilliams", "mcwilliams"), ("melloy'", "melloy"),
                                        ("shad ur", "shadur"), ("reayley", "reavley"), ("gibbsons", "gibbons"), ("gergory", "gregory"),
                                        ("duhe'", "duhe"), ("tymkovjch", "tymkovitch"), ("sloyiter", "sloviter"), ("plaum", "flaum"),
                                        ("mcmilllan", "mcmillian"), ("barb adoro", "barbadoro"), ("cabbanes", "cabranes"), ("loren", "loken"),
                                        ("pollan", "pollak"), ("solviter", "sloviter"), ("evan's", "evans"), ("gad ola", "gadola"),
                                        ("•gregory", "gregory"), ("hcoffey", "coffey"), ("dub ina", "dubina"), ("pagg", "fagg"),
                                        ("wood-", "wood"), ("puentes", "fuentes"), ("howard!", "howard"), ("roavster", "rovner"),
                                        ("birc.h", "birch"), ("vanantwerpen", "van antwerpen"), ("tymkoyich", "tymkovich"),
                                        ("varean", "varlan"), ("trakler", "traxler"), ("miils", "mills"), ("easterbrooe", "easterbrook"),
                                        ("restan!", "restani"), ("mekeown", "mckeown"), ("singad", "singal"), ("leyal", "leval"),
                                        ("mcgonnell", "mcconnell"), ("tordella", "toruella"), ("slovitee", "sloviter"),
                                        ("o'scannlaln", "o'scannlain"), ("katzmlann", "katzmann"), ("hard iman", "hardiman"),
                                        ("uoflat", "tjoflat"), ("reavely", "reavley"), ("delgadocolón", "delgado-colón"), ("elartz", "hartz"),
                                        ("al argón", "alarcón"), ("babee", "bybee"), ("kaztmann", "katzmann"), ("kjng", "king"),
                                        ("middle brooks", "middlebrooks"), ("o’brien", "o'brien"), ("o’neill", "o'neill"),
                                        ("b.d. parkier", "parker"), ("meclure", "mcclure"), ("pajez", "paez"), ("krayitch", "kravitch"),
                                        ("mccconnell", "mcconnell"), ("delgado-coln", "delgado-colón"), ("tymkovtch", "tymkovich"),
                                        ("coaven", "cowen"), ("scpiroeder", "schroeder"), ("southwtck", "southwick"),
                                        ("garcía-gre gory", "garcia-gregory"), ("laughlin", "mclaughlin"), ("eanne", "kanne"),
                                        ("suhrhei rch", "suhrheinrich"), ("be sosa", "besosa"), ("golloton", "colloton"),
                                        ("edmonson", "edmondson"), ("davts", "davis"), ("reenaraggi", "raggi"), ("wolman", "wollman"),
                                        ("wilrinson", "wilkinson"), ("beforemelloy", "melloy"), ("deryeghiayan", "der-yeghiayan"),
                                        ("ga jars a", "gajarsa"), ("bareett", "barkett"), ("moore-", "moore"), ("green berg", "greenberg"),
                                        ("bajetrett", "barrett"), ("gwtn", "gwin"), ("amero", "ambro"), ("flotd", "floyd"),
                                        ("a. wallace tashlma", "tashima"), ("smith .", "smith"), ("uarnes", "carnes"), ("abarcón", "alarcón"),
                                        ("yanaskie", "vanaskie"), ("and-graves", "graves"), ("calajbresi", "calabresi"), ("reith", "keith"),
                                        ("blacr", "black"), ("kaizen", "kazen"), ("bright •", "bright"), ("greenaway jr", "greenaway"),
                                        ("drone", "droney"), ("ckagares", "chagares"), ("before-niemeyer", "niemeyer"),
                                        ("higgingbotham", "higginbotham"), ("daughtery", "daughtrey"), ("williams'", "williams"),
                                        ("mecafferty", "mccafferty"), ("coor", "cook"), ("mcreague", "mckeague"), ("murgula", "murguia"),
                                        ("smitf-i", "smith"), ("sgirica", "scirica"), ("wopd", "wood"), ("■rosenbaum", "rosenbaum"),
                                        ("and-farris", "farris"), ("barksdale’", "barksdale"), ("sutton.", "sutton"), ("murtela", "murtha"),
                                        ("andposner", "posner"), ("dye", "dyk"), ("before-wood", "wood"), ("mehugh", "mchugh"),
                                        ("diaz'", "diaz"), ("jqrdan", "jordan"), ("le melle", "lemelle"), ("niemeyer/", "niemeyer"),
                                        ("and-prado", "prado"), ("goesuch", "gorsuch"), ("rosenbaum-", "rosenbaum"), ("hull arid", "hull"),
                                        ("callahan)", "callahan"), ("and-kelly", "kelly"), ("stanceú", "stanceu"), ("coon", "cook"),
                                        ("bachrach", "bacharach"), ("ghuang", "chuang"), ("buckle w", "bucklew"), ("wilkinson'", "wilkinson"),
                                        ("s.tranch", "stranch"), ("traxper", "traxler"), ("weight", "wright"), ("southwiok", "southwick"),
                                        ("rosenbuam", "rosenbaum"), ("surhenrich", "suhrheinrich"), ("rosenbaum:", "rosenbaum"),
                                        ("w^tte", "white"), ("before-loken", "loken"), ("eayatta", "kayatta"), ("william'pryor", "pryor"),
                                        ("tallman.", "tallman"), ("daug-htry", "daughtrey"), ("clelvfent", "clement"), ("* manion", "manion"),
                                        ("manion '", "manion"), ("tjoplat", "tjoflat"), (",-mckeague", "mckeague"), (",-jones", "jones"),
                                        ("so,uthwick", "southwick"), ("alargón", "alarcón"),("van bebber",'vanbebber'),
                                        ("mcmclaughlin","mclaughlin"),("droneyy","droney")]
    

    
    judgeNameCorrectionsTuples = judgeNameCorrectionsTuples + [("cardamons",'cardamone'),("calabeesi",'calabresi'),("hleval",'leval'),
                                        ("hkatzmann",'katzmann'),("graaeeiland",'graafeiland'),("sotomlayor",'sotomayor'),
                                        ("äôscannlain","o'scannlain"),("melaughlin",'mclaughlin'),("cabranls",'cabranes'),
                                        ("ke arse",'kearse'),("s.berzon",'berzon'),("parke",'parker'),("berz.on",'berzon'),
                                        ("ikuta-",'ikuta'),("r.-thomas",'thomas'),("owenp",'owen'),("n.elson",'nelson'),
                                        ("haul",'hall'),("sessions hi",'sessions'),("parkerr","parker"),("richman",'owen')]

    
    
    judgeNameCorrectionsTuples = judgeNameCorrectionsTuples + [("deyer",'dever'),("bung",'king'),("jrawlinson",'rawlinson'),
                                        ("b.d.parker",'b. parker'),("konzinski",'kozinski'),("steeh hi",'steeh iii'),
                                        ("s.-lasnik",'s. lasnik'),("hartz-",'hartz'),("'mchugh",'mchugh')]



    for (searchName,replName) in judgeNameCorrectionsTuples:
        fileText=fileText.replace(searchName,replName)


    #remove the ignored words from the text
    myRegex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, ignoreJudgeWords)))
    fileText = myRegex.sub("", fileText)

    
    #replace multiple consecutive spaces with just one
    fileText = re.sub ('[^\S\n]+',' ',fileText).strip()

    origLines = fileText.split('\n')
    

    #since we find some errors where names are incorrectly accented/not accented we try it also with accents removed
    altText = unidecode.unidecode(fileText)
    altLines = altText.split('\n')
    


    fileJudges = []

    for lineset in [origLines,altLines]:
        for line in lineset:
            words = line.split(' ')
            for i in range(len(words)):

                windowEnd = min(i+windowSize,len(words))
                
                consideredWords = words[i:windowEnd]

                
                #should start with our now standardized "before" word
                #or "before" should never appear at all, but in this case we must have reason to expect a judge sitting by designation
                #or only be searching over the circuit's actual judges
                if 'before' == consideredWords[0] or ('before' not in fileText and (suspectDesignation or secondaryJudgeLists!=None)):
                    if debugOut:
                        print([pj.fullName for pj in potentialFileJudges])
                        print(consideredWords)
                                        
                    #end window early if a period seems to be ending the sentence
                    for posEndWord in consideredWords:
                        if len(posEndWord)<1:
                            continue
                        

                    if debugOut:
                        print(consideredWords)

                    ##find overlap of text and potential judges
                    foundJudges = []
                    

                    for wordIndex in range(len(consideredWords)):
                        word = consideredWords[wordIndex]

                        #make sure that this name/word is right before a comma or 'and', otherwise we may confuse
                        #the first name of a judge for the last name of a different judge and add the wrong one
                        #also add a few other words we saw in testing which follow a judge last name but are definitely
                        #not a judge's first name
                        if wordIndex+1< len(consideredWords) and consideredWords[wordIndex+1] not in [',','and','circuit','and.',';',
                                                                                                'and:','&','chief','judge','judges','district',
                                                                                                'judge.','judges.','senior']:
                            continue
                        for judge in potentialFileJudges:
                            if word == judge.lastName and judge not in foundJudges:
                                foundJudges.append(judge)

                                    
                            
                    ###if there are two potential judges with the same last name try to figure out which of them is actually on the case
                    removeJudges = []

                    for first in foundJudges:
                        if first in removeJudges:
                            continue
                        for second in foundJudges:
                            if second in removeJudges:
                                continue

                            if first!=second and first.lastName == second.lastName and consideredWords.count(first.lastName) <2:
                                
                                #we will consider the word before the confusing last name
                                prevWord = consideredWords[consideredWords.index(first.lastName)-1]
                                secondPrev = ""

                                #if there are two words before the confusing name we will consider the word 2 before it as well
                                if consideredWords.index(first.lastName) >1:
                                    secondPrev = consideredWords[consideredWords.index(first.lastName)-2]
                                
                                
                                #if the word before is the name or first initial of one of the judges get rid of the other
                                if prevWord.replace('.','')==first.firstName or prevWord.split('.')[0] == first.firstName[0]:
                                    
                                    removeJudges.append(second)
                                elif prevWord.replace('.','')==second.firstName or prevWord.split('.')[0] == second.firstName[0]:
                                    
                                    removeJudges.append(first)
                                
                                #else if the word 2 spaces before is the first name or initial of a judge get rid of the other
                                elif secondPrev.replace('.','')==first.firstName or secondPrev.split('.')[0] == first.firstName[0]:
                                    
                                    removeJudges.append(second)
                                elif secondPrev.replace('.','')==second.firstName or secondPrev.split('.')[0] == second.firstName[0]:
                                    
                                    removeJudges.append(first)

                                #if the full name of one of the judges appears towards the end of the text we are looking at
                                #throw out the other one as it is probably describing the judge sitting by designation
                                
                                elif first.firstName.split(' ')[0]+' '+first.lastName.split(' ')[0] in fileText:
                                    removeJudges.append(second)
                                elif second.firstName.split(' ')[0]+' '+second.lastName.split(' ')[0] in fileText:
                                    removeJudges.append(first)

                                #similarly, search for first name, middle initial, last name of either judge in the text.
                                elif len(first.middleName)>0 and first.firstName.split(' ')[0]+' ' + first.middleName[0]+'. '+first.lastName.split(' ')[0] in fileText:
                                    removeJudges.append(second)
                                elif len(second.middleName)>0 and second.firstName.split(' ')[0]+' ' + second.middleName[0]+'. '+second.lastName.split(' ')[0] in fileText:
                                    removeJudges.append(first)

                                #and for full first, middle, last name
                                elif len(first.middleName)>0 and first.firstName.split(' ')[0]+' ' + first.middleName.split(' ')[0] +' '+first.lastName.split(' ')[0] in fileText:
                                    removeJudges.append(second)
                                elif len(second.middleName)>0 and second.firstName.split(' ')[0]+' ' + second.middleName.split(' ')[0]+' '+second.lastName.split(' ')[0] in fileText:
                                    removeJudges.append(first)
                                    
                                #if only one of the two judges actually belongs to the same circuit as the case, get rid of the other
                                elif first.circuit==fileCirc and second.circuit!=fileCirc:
                                    
                                    removeJudges.append(second)
                                elif second.circuit==fileCirc and first.circuit!=fileCirc:
                                    
                                    removeJudges.append(first)

                                #if the two judges we are considering are from different courts, try to leverage that info

                                #see if some of the judges we are considering are from district courts and if so if the name of their court appears
                                #in the files text
                                elif first.circuit!=second.circuit and 'District Court' in first.circuit and first.circuit.split(' ')[-1] in ogFileText:
                                    
                                    removeJudges.append(second)
                                    
                                elif first.circuit!=second.circuit and 'District Court' in second.circuit and second.circuit.split(' ')[-1] in ogFileText:
                                    
                                    
                                    removeJudges.append(first)


                                #see if any of the judges are from a circuit court and the name of that court appears in the text
                                elif first.circuit!=second.circuit and 'Court of Appeals' in first.circuit and (first.circuit.split(' ')[-2]+' Circuit') in ogFileText:
                                    removeJudges.append(second)
                                    
                                elif first.circuit!=second.circuit and 'Court of Appeals' in second.circuit and (second.circuit.split(' ')[-2]+' Circuit') in ogFileText:
                                    removeJudges.append(first)
                                    
                                #check if we think a judge we are considering is from supreme court and the headmatter also mentions
                                #the supreme court
                                elif first.circuit!=second.circuit and 'Supreme Court' in first.circuit and 'Supreme Court' in ogFileText:
                                    removeJudges.append(second)
                                elif first.circuit!=second.circuit and 'Supreme Court' in second.circuit and 'Supreme Court' in ogFileText:
                                    removeJudges.append(first)

                                #see if one of the two judges has senior status or is not a judge this year at all (we add 1 year to the end of their
                                #service for when the case just came out a bit later).  If so, take the other one
                                elif fileYear>first.end:
                                    removeJudges.append(first)

                                elif fileYear>second.end:
                                    removeJudges.append(second)

                                elif fileYear>first.seniorStart:
                                    removeJudges.append(first)

                                elif fileYear>second.seniorStart:
                                    removeJudges.append(second)

                                #otherwise just take whatever judge started earlier, since they aren't bothering to specify
                                #which of them it is, its usually because the later judge wasn't around yet
                                elif first.start<second.start:
                                    
                                    removeJudges.append(second)

                                else:
                                    
                                    removeJudges.append(first)

                    for rj in removeJudges:
                        if rj in foundJudges:
                            foundJudges.remove(rj)
                    ##We will eventually use the window which produced the highest number of judge names
                    ##if this is more judges that we had associated with the file, use the current window
                    if len(foundJudges)>len(fileJudges):
                        
                        fileJudges=foundJudges
                                                        
                        
    #if we didn't find at least 3 judges and we have a list of judges who may be sitting by designation, we try the process again
    #now considering the candidate judges from other courts

    if len(fileJudges)<3 and secondaryJudgeLists!=None:
        #Sometimes there is no indication that a judge is sitting by designation
        #so we have an indicator if there is evidence to suggest they are.
        #we search for judges by designation either way, but change our behavior in sorting out judges with the same name in instances
        #where we don't have reason to suspect a judge by designation
        suspectDesignation = False
        if ('*' in ogFileText or 'District Judge' in ogFileText or 'Supreme Court' in ogFileText or
                            'sitting by designation' in fileText or 'Judge of' in ogFileText):
            suspectDesignation = True

        return findJudges(ogFileText, secondaryPotFileJudges, fileYear,fileCirc,debugOut=debugOut,suspectDesignation=suspectDesignation)

    
    
    return fileJudges



