# NBA-Win-Loss-Prediction
#####Predicts which NBA team wins given a match up of two teams

#ScrapeWebsite - Scrapes http://www.basketball-reference.com for data on NBA matches
#FinalizeDataSets - Combines Scrapped data into seasonal data sets (Stores in Prepared Folder)
#DemoModel - Runs our Machine Learning Model

In the Prepared folder, there are data sets from years 2008 to 2015. Each line contains information for both teams in an individual match.

#TeamA Code,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,TS%,eFG%,3PAr,FTr,ORB%,DRB%,TRB%,AST%,#STL%,BLK%,TOV%,USG%,ORtg,DRtg
#... TeamB Code,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,TS%,eFG%,3PAr,FTr,ORB%,DRB%,TRB%,A#ST%,STL%,BLK%,TOV%,USG%,ORtg,DRtg
#... TeamAWin?
