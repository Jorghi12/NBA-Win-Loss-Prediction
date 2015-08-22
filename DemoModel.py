"""Model using the most basic features"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import cross_validation
from sklearn import linear_model


#Calculates the Rolling Average of a team's stats up to a specific date. Input needs to be sorted by time first
def teamRollingAvg(seasonCSV, teamId):
	teamSet = seasonCSV[seasonCSV['tm0_init'] == teamId]
	teamUpdatedSet = teamSet[teamSet.columns[1:]]
	teamUpdatedSet = teamUpdatedSet.shift(1) #No rolling average exists for the first game to use for predictions.
	teamUpdatedSet = pd.rolling_mean(teamUpdatedSet,window=teamSet.shape[0],min_periods=1)
	teamUpdatedSet = pd.concat([teamSet[teamSet.columns[0]],teamUpdatedSet],axis=1)
	return teamSet, teamUpdatedSet

#Loads and sorts the Seasonal Data Set by date
def loadAndSortData(year):
	folder = "C:\\NBA Data Science\\Prepared\\"
	data = pd.read_csv(folder + year + "_seasonDataSet.csv", header = False) #Loads our dataset

	#Convert date strings into type datetime
	data['date'] = pd.to_datetime(data['date'])
	
	#Sort our datarows by increasing date
	data = data.sort(['date'])
	
	return data

#Computes the rolling averages for all teams in the Sorted Data Set
def GenerateRollingAverages(sorted_data):
	teams = []
	team_rolls = []
	for i in range(0,34):
		team, team_rolling = teamRollingAvg(sorted_data,i)
		teams.append(team)
		team_rolls.append(team_rolling)
	return teams, team_rolls
	
"""Performs linear regression, indirectly predicting wins and losses by looking at the returned score differences"""
def trainScoreDifference(years = ['2008','2009','2010','2011','2012','2013','2014','2015']):
	year_errorSum = 0
	for year in years:
		#Loads the seasonal Data Set and sorts it by ascending date
		data = loadAndSortData(year)
	
		#Generate Team data and Rolling Averages data for each team in the data set
		teams, team_rolls = GenerateRollingAverages(data)
		
		featureDF = [] #The feature data frame (what our features are for the algorithm we'll use)
		targetDF = [] #The target data frame (what we're trying to predict correctly)
		
		for tm in range(0,len(teams)):
			team = teams[tm] #The Original Data set for team tm
			team_rolling = team_rolls[tm] #The Rolling Data set for team tm.
			
			"""Each Row N in team_rolling is the Predicted Rolling Average for game N using games N-1, thus Row 0 is NAN
			We'll use Row N (Predicted Feature based off of Rolling Average) to help predict the outcome of game N
			So the idea is that we'll use the rolling average based off previous games to help predict the outcome of each upcoming game"""
			columns = ['score_diff','team0_RollingWin','team1_RollingWin']
			dataD = np.array([np.arange(82)]*3,dtype="float").T
			predDF = pd.DataFrame(data = dataD,columns=columns)
			predDF = predDF.convert_objects(convert_numeric=True)
			vals = 0
			#Look at each match in our specified team's data set
			for match in range(1,team_rolling.shape[0]): #Note we start at index 1 to ignore the team's first match (No rolling averages)
				#Grabs the timestamp and opponent id from the match
				time_stamp = team_rolling.iloc[match]['date']
				opponent_id = team.iloc[match]['tm1_init']
				
				#Grab the Opponent's most recent rolling average at a date BEFORE/EQUAL to our match's date (time_stamp)
				opponent_rolling = team_rolls[opponent_id][team_rolls[opponent_id]['date'] <= time_stamp][-1:]
				
				#If Opponent has no rolling_data to base off... Remove the match from our predictions altogether
				if np.all(opponent_rolling.iloc[0][1:].isnull()):
					#team_rolling = team_rolling.drop(team_rolling.index[match:match])
					pass
				else:
					#Set the predicted (rolling) features for the opponent in the team_rolling DataFrame
					predDF.iloc[vals]['score_diff'] = team.iloc[[match]]['tm0_PTS'].values - team.iloc[[match]]['tm1_PTS'].values
					predDF.iloc[vals]['team0_RollingWin'] = team_rolling.iloc[[match]]['win'].values
					predDF.iloc[vals]['team1_RollingWin'] = opponent_rolling.iloc[[0]]['win'].values
					vals = vals + 1
					
			#Grab our selected target feature
			result = predDF['score_diff']
			
			#Subtract the rolling averages to give some type of comparison
			new_features = predDF.ix[:,1:]
			
			"""Remove NAN row (can't make any useful predictions for 1st game)"""
			if not new_features.empty: #Not all teams may be in our season. i.e. Seattle SuperSonics isn't in year 2008 and on. They were renamed to Oklahoma City Thunder (OKC)
				new_features = new_features.drop(new_features.index[[0]])
				result = result.drop(result.index[[0]])
			
			#Add to our training data
			featureDF.append(new_features)
			targetDF.append(result)
		
		X = pd.concat(featureDF) #Combine all individual team predictions into 1 large data frame
		y = pd.concat(targetDF) #Combine all individual team targets into 1 large data frame
		
		#Create a prediction model using Linear Regression w/ Cross Validation of (Minimum Least Squares error)
		loo = cross_validation.LeaveOneOut(len(X))
		regr = linear_model.LinearRegression()
		regr.fit(X, y)
		
		scores = cross_validation.cross_val_score(regr, X, y, scoring=scorerPTS, cv=loo)
		
		#print('Training error: %.4f' % (scorerPTSavg(regr,X,y)))
		year_errorSum += scores.mean()
		print('Year:' + year + ' Cross Validation Error: %.4f' % (scores.mean()))
	print('Average Error: %.4f' % (year_errorSum/len(years)))
		
def scorerPTS(estimator, X, y):
	#Return's 1 (i.e. incorrect classification) when the ScoreDifference(y) has a different sign than the Predicted Score Difference
	#i.e. y=30 & predicted y = 10 -> outputs 0
	#i.e. y=10 & predicted y = -20 -> outputs 1 (incorrect classification)
	return int(y*estimator.predict(X) <= 0) 

"""Performs logistic regression, directly predicting wins and losses"""
def trainWinLoss(years = ['2008','2009','2010','2011','2012','2013','2014','2015']):
	#Loads the seasonal Data Set and sorts it by ascending date
	data = loadAndSortData(years[0])
	
	#Generate Team data and Rolling Averages data for each team in the data set
	teams, team_rolls = GenerateRollingAverages(data)
	
	featureDF = [] #The feature data frame (what our features are for the algorithm we'll use)
	targetDF = [] #The target data frame (what we're trying to predict correctly)
	
	for tm in range(0,len(teams)):
		team = teams[tm] #The Original Data set for team tm
		team_rolling = team_rolls[tm] #The Rolling Data set for team tm.
		
		"""Each Row N in team_rolling is the Predicted Rolling Average for game N using games N-1, thus Row 0 is NAN
		We'll use Row N (Predicted Feature based off of Rolling Average) to help predict the outcome of game N
		So the idea is that we'll use the rolling average based off previous games to help predict the outcome of each upcoming game"""
		columns = ['win','team0_RollingWin','team1_RollingWin']
		dataD = np.array([np.arange(82)]*3,dtype="float").T
		predDF = pd.DataFrame(data = dataD,columns=columns)
		predDF = predDF.convert_objects(convert_numeric=True)
		vals = 0
		#Look at each match in our specified team's data set
		for match in range(0,team_rolling.shape[0]):
			#Grabs the timestamp and opponent id from the match
			time_stamp = team_rolling.iloc[match]['date']
			opponent_id = team.iloc[match]['tm1_init']
			
			#Grab the Opponent's most recent rolling average at a date BEFORE/EQUAL to our match's date (time_stamp)
			opponent_rolling = team_rolls[opponent_id][team_rolls[opponent_id]['date'] <= time_stamp][-1:]
			
			#If Opponent has no rolling_data to base off... Remove the match from our predictions altogether
			if np.all(opponent_rolling.iloc[0][1:].isnull()):
				#team_rolling = team_rolling.drop(team_rolling.index[match:match])
				pass
			else:
				#Set the predicted (rolling) features for the opponent in the team_rolling DataFrame
				predDF.iloc[vals]['win'] = team.iloc[[match]]['win']
				predDF.iloc[vals]['team0_RollingWin'] = team_rolling.iloc[[match]]['win']
				predDF.iloc[vals]['team1_RollingWin'] = opponent_rolling.iloc[[0]]['win']
				vals = vals + 1
				
		#Grab our selected target feature
		result = predDF['win']
		result = result[0:vals]
		#Subtract the rolling averages to give some type of comparison
		new_features = predDF.ix[:,1:]
		new_features = new_features[0:vals]
		
		"""Remove NAN row (can't make any useful predictions for 1st game)"""
		if not new_features.empty: #Not all teams may be in our season. i.e. Seattle SuperSonics isn't in year 2008 and on. They were renamed to Oklahoma City Thunder (OKC)
			new_features = new_features.drop(new_features.index[[0]])
			result = result.drop(result.index[[0]])
		
		#Add to our training data
		featureDF.append(new_features)
		targetDF.append(result)
	
	X = pd.concat(featureDF) #Combine all individual team predictions into 1 large data frame
	y = pd.concat(targetDF) #Combine all individual team targets into 1 large data frame
	
	#Create a prediction model using Logistic Regression w/ Cross Validation
	regr = linear_model.LogisticRegressionCV()
	regr.fit(X, y)
	
	print('Training error: %.4f' % (1 - regr.score(X, y)))
	print('Cross Validation Error: %.4f' % (1-((np.mean(regr.scores_[1][0]) + np.mean(regr.scores_[1][1]) + np.mean(regr.scores_[1][2]))/3)))

trainScoreDifference(years = ['2008'])