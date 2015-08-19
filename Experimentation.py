import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import linear_model
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split
##Our Data Set keept the matches in chronological order
#TODO - Add time to Data Scrapper and keep the time with FinalizeDataSets
#Then update this to SORT examples by time.

def runningAvg(features):
	return pd.rolling_mean(features, window=features.shape[0],min_periods=1)
	
def train(years = ['2008']):
	folder = "C:\\NBA Data Science\\Prepared\\"
	data = pd.read_csv(folder + years[0] + "_seasonDataSet.csv", header = False) #Loads our dataset
	
	teamA = data.ix[:,1:34]
	teamB = data.ix[:,35:68]
	result = data.ix[:,68]
	
	new_features = pd.DataFrame(teamA.values - teamB.values)
	new_features = runningAvg(new_features)
	
	#Hold out cross validation
	test_size = int(.70*new_features.shape[0])
	X_train = new_features[0:test_size]
	y_train = result[0:test_size]
	
	X_test = new_features[test_size:]
	y_test = result[test_size:]
	
	#X_train, X_test, y_train, y_test = train_test_split(new_features, result, test_size=0.3, random_state=0)
	
	classifier = linear_model.LogisticRegression()
	classifier.fit(X_train,y_train)
	print classifier.score(X_test, y_test)
	#print classifier.coef_
	
train()