import os
import sys
sys.path.append('C:\\NBA Data Science\\')
import ScrapeWebsite

###Team Codes are just the indicies
def createTeamCodes(years = ["2008","2009","2010","2011","2012","2013","2014","2015"]):
	initials = []
	for year in years:
		initials.extend(ScrapeWebsite.grab_team_initials(year))
	allTeams = list(set(initials))
	return allTeams
	
teamCodes = createTeamCodes()

def createCSVPerSeason(years = ["2008","2009","2010","2011","2012","2013","2014","2015"]):
	inPath = "C:\\NBA Data Science\\Scrapped\\"
	newpath = "C:\\NBA Data Science\\Prepared\\"
	if not os.path.exists(newpath): os.makedirs(newpath)
	
	for year in years:
		initials = ScrapeWebsite.grab_team_initials(year) #We'll be using functions inside our ScrapeWebsite
		outputCSV = open(newpath + year + "_seasonDataSet.csv","w+")
		
		for team in initials:
			basicCSV = open(inPath + year + "\\" + team + "_basic.csv", "r").read()
			advancedCSV = open(inPath + year + "\\" + team + "_advanced.csv","r").read()
			outcomeCSV = open(inPath + year + "\\" + team + "_outcome.csv","r").read()
			
			basicCSV = basicCSV.split('\n')
			advancedCSV = advancedCSV.split('\n')
			outcomeCSV = outcomeCSV.replace("G,Date,,,,,Opponent,,,Tm,Opp,W,L,Streak,Notes\n","") #Remove repeated headers from CSV
			outcomeCSV = outcomeCSV.split('\n')
			
			for i in range(0,len(basicCSV)):
				if basicCSV[i] != "" and advancedCSV[i] != "" and outcomeCSV[i] != "":
					#Create feature vectors
					outcomeFeatures = outcomeCSV[i].split(',')
					basicFeatures = basicCSV[i].split(',')
					advFeatures = advancedCSV[i].split(',')
					
					#Grab basic features for each team
					team0_basic = basicFeatures[0:19]
					team1_basic = basicFeatures[20:39]
					
					#Grab advanced features for each team (Ignore the duplicated MP feature that's already inside our basic dataset)
					team0_adv = advFeatures[1:15]
					team1_adv = advFeatures[16:]
					
					#Grab teamCode for opponent team by converting opponent's initial stored at the end of basicCSV
					print team + " " + year
					team1_initial = teamCodes.index(basicFeatures[40])
					
					#Grab teamCode for current team
					team0_initial = teamCodes.index(team)
					
					#Create team0 and team1 entry
					team0_entry = str(team0_initial) + "," + ','.join(team0_basic) + "," + ','.join(team0_adv)
					team1_entry = str(team1_initial) + "," + ','.join(team1_basic) + "," + ','.join(team1_adv)
					
					#Whether team0 won or lost
					team0_win = outcomeFeatures[7].replace("W","1").replace("L","0") #We'll get other values if our data is corrupted
					
					#Add new data point to line in our seasonal data set
					outputCSV.write(team0_entry + "," + team1_entry + "," + team0_win + "\n")
					
		#Close the file
		outputCSV.close()

if __name__ == "__main__":
	print "STARTING"
	createCSVPerSeason()
	print "FINISHED"
			
			
			