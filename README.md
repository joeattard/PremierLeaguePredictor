# PremierLeaguePredictor

This project gathers premier league data from 2 sources (BBC and FootballCritic) and attempts to simulate fixtures using said data. 

It works by calculating a value for "Team Strength" and then assigning probability values to a result (Win, Loss, Draw). 
These probabilities are then used in a function which uses these weighted values, to determine an outcome. 

Currently one other factor is used to decide the "team strength" for any given fixture and that is "form". 
"Form" is determined by taking into account previous results. eg. the more losses, the worse the form and 
therefore the worse the team strength to a limiting factorwhich is necessary so results don't exponentially decline or rise.

In the future I will add another factor, the home advantage factor!!!

Draw probability is calculated using a Cauchy distribution with specified coefficients determined through trial and error. 
Win/Loss probability is calculated using a linear function. 

A full season is simulated 100 times by default, and the average results determined. 

Currently I am only using EPL data, though this could easily be used for other leagues. It would require the following:

1. Updating the league URL from the BBC
2. Updating the team URLs from footballcrictic
3. Creating a fixture list in the same format as the one used


When running the code, you can specify the number of iterations required. Currently 100 seasons are run by default and the average taken. 

You can also update the boolean value for  "continue_seasons" to determine whether to continue the season from its current real-life staate, or start anew from Game Week1. 
