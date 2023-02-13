#This is a simple class definition to hold information about each judge.  Is used by other files, and is not to be run directly.

class judge(object):
   
	def __init__(self,line):
		parts = line.strip().split(',')
		self.circuit = parts[1]
		self.start = int(parts[3])
		self.end = int(parts[4])
		self.party = parts[2]
		self.gender =''
		self.race=''
		self.birth=''
		self.ideology=''
		self.birth_year = ''
		self.court_type1 = ''
		self.court_type2 = ''
		self.court_type3 = ''
		self.court_type4 = ''
		self.court_type5 = ''
		self.court_type6 = ''
		self.commission_date1 = ''
		self.commission_date2 = ''
		self.commission_date3 = ''
		self.commission_date4 = ''
		self.commission_date5 = ''
		self.commission_date6 = ''

		self.court_name1=''
		self.court_name2 = ''
		self.court_name3 = ''
		self.court_name4 = ''
		self.court_name5 = ''
		self.court_name6 = ''

		self.chief11 = ''
		self.chief12 = ''
		self.chief21 = ''
		self.chief22 = ''
		self.chief31 = ''
		self.chief32 = ''
		self.chief41 = ''
		self.chief42 = ''
		self.chief51 = ''
		self.chief52 = ''
		self.chief61 = ''
		self.chief62 = ''

		self.chief11e = ''
		self.chief12e = ''
		self.chief21e = ''
		self.chief22e = ''
		self.chief31e = ''
		self.chief32e = ''
		self.chief41e = ''
		self.chief42e = ''
		self.chief51e = ''
		self.chief52e = ''
		self.chief61e = ''
		self.chief62e = ''

		self.senior1 = ''
		self.senior2 = ''
		self.senior3 = ''
		self.senior4 = ''
		self.senior5 = ''
		self.senior6 = ''


		self.judge_elite = ''
		self.fullName = parts[0]
		self.lastName = parts[0].split('<')[0].lower()
		self.firstName = parts[0].split('<')[1].lower().strip().split(' ')[0]
		self.middleName = parts[0].split('<')[0].lower().strip().split(' ')[0]

	def __init__(self,circuit,start,end,party,gender,race,birth,fullName,lastName,firstName,ideology,birth_year,judge_elite,
				 court_type1,court_type2,court_type3,court_type4,court_type5,court_type6,
				 commission_date1, commission_date2, commission_date3, commission_date4, commission_date5, commission_date6,
				 court_name1, court_name2, court_name3, court_name4, court_name5, court_name6,
				 chief11, chief12, chief21, chief22, chief31, chief32, chief41, chief42, chief51, chief52, chief61,chief62,
				 chief11e, chief12e, chief21e, chief22e, chief31e, chief32e, chief41e, chief42e, chief51e, chief52e,
				 chief61e, chief62e,
				 senior1, senior2, senior3, senior4, senior5, senior6,
				 seniorStart=9999,chiefStart=9999,chiefEnd=9999,middleName=''):
		self.circuit = circuit
		self.start = int(start)
		self.end = int(end)
		self.seniorStart = int(seniorStart)
		self.chiefStart = int(chiefStart)
		self.chiefEnd = int(chiefEnd)
		self.party = party
		self.gender = gender
		self.race = race
		self.birth = birth
		self.ideology = ideology
		self.birth_year = birth_year
		self.judge_elite = judge_elite
		self.court_type1 = court_type1
		self.court_type2 = court_type2
		self.court_type3 = court_type3
		self.court_type4 = court_type4
		self.court_type5 = court_type5
		self.court_type6 = court_type6
		self.commission_date1 = commission_date1
		self.commission_date2 = commission_date2
		self.commission_date3 = commission_date3
		self.commission_date4 = commission_date4
		self.commission_date5 = commission_date5
		self.commission_date6 = commission_date6
		self.court_name1 = court_name1
		self.court_name2 = court_name2
		self.court_name3 = court_name3
		self.court_name4 = court_name4
		self.court_name5 = court_name5
		self.court_name6 = court_name6

		self.chief11 = chief11
		self.chief12 = chief12
		self.chief21 = chief21
		self.chief22 = chief22
		self.chief31 = chief31
		self.chief32 = chief32
		self.chief41 = chief41
		self.chief42 = chief42
		self.chief51 = chief51
		self.chief52 = chief52
		self.chief61 = chief61
		self.chief62 = chief62

		self.chief11e = chief11e
		self.chief12e = chief12e
		self.chief21e = chief21e
		self.chief22e = chief22e
		self.chief31e = chief31e
		self.chief32e = chief32e
		self.chief41e = chief41e
		self.chief42e = chief42e
		self.chief51e = chief51e
		self.chief52e = chief52e
		self.chief61e = chief61e
		self.chief62e = chief62e

		self.senior1 = senior1
		self.senior2 = senior2
		self.senior3 = senior3
		self.senior4 = senior4
		self.senior5 = senior5
		self.senior6 = senior6

		self.partyCodes = {'Republican':'0','Democratic':'1'}
		self.partyCode = self.partyCodes[party]
		self.genderCodes = {'Male':'0','Female':'1'}
		self.genderCode = self.genderCodes[gender]
		self.raceCodes = {'White':'0','Other':'1'}
		if race in self.raceCodes:
			self.raceCode = self.raceCodes[race]
		else:
			self.raceCode = self.raceCodes['Other']
		#self.birthCodes = {'1':'0','2':'0','3':'0','4':'0','5':'0','6':'0','7':'1','8':'1','9':'1','10':'1','11':'1','12':'1'}
		self.birthCodes = {'0':'0','1':'1'}
		self.birthCode = self.birthCodes[birth]
		self.fullName = fullName
		self.lastName = lastName.lower()
		self.firstName = firstName.lower()
		self.middleName = middleName.lower()

	


	def __str__(self):
		return self.fullName + ' Circuit: ' + self.circuit + ' Party: ' + self.party + ' Gender: ' + self.gender +' Start: ' +str(self.start) + ' End: ' +str(self.end)
	def __repr__(self):
		return self.fullName + ' Circuit: ' + self.circuit + ' Party: ' + self.party + ' Gender: ' + self.gender +' Start: ' +str(self.start) + ' End: ' +str(self.end)

