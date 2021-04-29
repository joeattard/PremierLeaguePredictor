from numpy import log as ln
from data_collection import *
from predictor import *

"""
Author: Joe Attard
Date: 29-04-2021

Currently only using EPL data and links. 
Could be updated/changed to utilise other league data,
would require updating league urls below, as well as the 
bbc league data (url variable)
"""

league_urls = ["https://www.footballcritic.com/arsenal-fc/squad/467",
               "https://www.footballcritic.com/aston-villa-fc/squad/461",
               "https://www.footballcritic.com/brighton-hove-albion-fc/squad/510",
               "https://www.footballcritic.com/burnley-fc/squad/492",
               "https://www.footballcritic.com/chelsea-fc/squad/471",
               "https://www.footballcritic.com/crystal-palace-fc/squad/508",
               "https://www.footballcritic.com/everton-fc/squad/473",
               "https://www.footballcritic.com/fulham-fc/squad/460",
               "https://www.footballcritic.com/leeds-united-fc/squad/497",
               "https://www.footballcritic.com/leicester-city-fc/squad/489",
               "https://www.footballcritic.com/liverpool-fc/squad/462",
               "https://www.footballcritic.com/manchester-city-fc/squad/464",
               "https://www.footballcritic.com/manchester-united-fc/squad/475",
               "https://www.footballcritic.com/newcastle-united-fc/squad/466",
               "https://www.footballcritic.com/sheffield-united-fc/squad/480",
               "https://www.footballcritic.com/southampton-fc/squad/506",
               "https://www.footballcritic.com/tottenham-hotspur-fc/squad/472",
               "https://www.footballcritic.com/west-bromwich-albion-fc/squad/474",
               "https://www.footballcritic.com/west-ham-united-fc/squad/496",
               "https://www.footballcritic.com/wolverhampton-wanderers-fc/squad/459"]


#get data from league table site
url = "https://www.bbc.co.uk/sport/football/premier-league/table"
df = league_data(url, league_urls)

#load fixture list
fixtures = pd.read_csv('Data/league_fixtures.csv')

'''To be set by user...'''
continue_seasons = True #----------->False = start season from fresh, True = finish current season
seasons = 100  #-------------------->Number of iterations of a season sim (average taken)

for season in range (0, seasons):
    print(season)
    def_strength_array = []
    for i in range(len(df)):
        """
        Experimented with a default form factor as the football critic site
        updates the team strength/form as games are played. This means it may not
        be entirely accurate if starting a fresh league. The default_form variable 
        is intended to compensate, although it's not perfect....
        """

        current_form = df["Form"][i]
        total_f = len(current_form)
        wins = current_form.count("W") / total_f
        losses = current_form.count("L") / total_f
        draws = current_form.count("D") / total_f
        if losses != 0:
            current_form_val = ((wins + draws) / losses)
        else:
            current_form_val = 5 * (wins + (draws / 2))

        form_val = 0.04 * current_form_val + 0.9
        default_strength = df["TeamStrength"][i] / form_val
        def_strength_array.append(default_strength)
        default_form = ln(form_val)

        #uncomment to test the "form factor" else all start with default 0 form
        #df.loc[i, "PredictedForm"] = default_form
        df.loc[i, "PredictedForm"] = 0

    df["DefaultStrength"] = def_strength_array
    run_fixtures(fixtures, df, continue_seasons)

# divide cumulative points by total seasons + 1 (starts from zero)
for i in range(len(df)):
    df.loc[i, "PredictedPoints"] = round(df.loc[i, "PredictedPoints"] / seasons + 1)

df = df.sort_values("PredictedPoints", ascending=False)

#display final standings --> Position column represents current real life position
print(df[["Names", "PredictedPoints", "Position"]])

#save final standings to CSV
df.to_csv('Data/FinalPredictedStandings')