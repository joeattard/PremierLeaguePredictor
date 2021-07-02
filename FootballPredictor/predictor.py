import numpy as np
import random
from collections import Counter


def find_interval(x, partition):
    """ find_interval -> i
        partition is a sequence of numerical values
        x is a numerical value

        partition[i] < x < partition[i+1], if such an index exists.
        -1 otherwise
    """

    for i in range(0, len(partition)):
        if x < partition[i]:
            return i - 1
    return -1


def weighted_choice(sequence, weights, secure=True):
    """
    weighted_choice selects a random element of
    the sequence according to the list of weights
    """

    if secure:
        crypto = random.SystemRandom()
        x = crypto.random()
    else:
        x = np.random.random()
    cum_weights = [0] + list(np.cumsum(weights))
    index = find_interval(x, cum_weights)
    return sequence[index]


'''Above code for the weighted probabilities found in the following link
--------->>>>> https://www.python-kurs.eu/bk_random.py <<<<<--------'''


def predicted_result(home_strength, away_strength):
    # cauchy distrib for draws
    a = 0.43
    x = (float(home_strength) - float(away_strength)) / 100
    c_1 = 0.5
    c_2 = 0.33 / 2
    c_3 = 2.5
    coeff_1 = np.pi * a
    coeff_2 = (4 * x) / c_1
    k = 0.9

    cauchy_dist = k / (coeff_1 * (1 + (coeff_2 ** 2)))

    # win distrib
    win_dist = c_3 * x + c_2

    if x < 0:
        x = (float(away_strength) - float(home_strength)) / 100
        win_dist = 1 - cauchy_dist - (c_3 * x + c_2)

    Pwin = win_dist
    Pdrw = cauchy_dist
    Plos = 1 - win_dist - cauchy_dist

    W = str("Win")
    L = str("Loss")
    D = str("Draw")
    results = [W, L, D]
    weights = [Pwin, Plos, Pdrw]
    outcomes = []
    n = 1
    for _ in range(n):
        outcomes.append(weighted_choice(results, weights))
    c = Counter(outcomes)
    for key in c:
        c[key] = c[key] / n
    return outcomes[0]


def points_gained(df, outcome, home_form, away_form, home_idx, away_idx):
    # set a max and min for the exponent of e so the form doesn't make a team too strong or too weak
    max_form = 0.1655
    form_gain = 0.04
    min_form = -0.1

    # define rules for gaining points and save cumulatively
    if outcome == "Win":
        if home_form < max_form:
            df.loc[home_idx, 'PredictedForm'] += form_gain
        if away_form > min_form:
            df.loc[away_idx, 'PredictedForm'] += form_gain
        df.loc[home_idx, 'PredictedPoints'] += 3
    elif outcome == "Draw":
        df.loc[home_idx, 'PredictedPoints'] += 1
        df.loc[away_idx, 'PredictedPoints'] += 1
    else:
        if away_form < max_form:
            df.loc[away_idx, 'PredictedForm'] += form_gain
        if home_form > min_form:
            df.loc[home_idx, 'PredictedForm'] += form_gain
        df.loc[away_idx, 'PredictedPoints'] += 3

    return df


def run_fixtures(fixtures, df, continue_seasons):

    for i in range(len(fixtures)):
        home_team = fixtures["Home"][i]
        away_team = fixtures["Away"][i]

        home_stat = df.loc[df['Names'] == home_team]
        away_stat = df.loc[df['Names'] == away_team]

        home_idx = df.loc[df['Names'] == home_team, 'PredictedPoints'].index[0]
        away_idx = df.loc[df['Names'] == away_team, 'PredictedPoints'].index[0]

        home_form = df.loc[home_idx, 'PredictedForm']
        away_form = df.loc[away_idx, 'PredictedForm']

        home_strength = home_stat.iloc[0]['TeamStrength'] * np.exp(home_form)
        away_strength = away_stat.iloc[0]['TeamStrength'] * np.exp(away_form)

        # get the home and away strength and predict the result
        outcome = predicted_result(home_strength, away_strength)

        # if continue seasons then finish the current seasons fixtures
        if continue_seasons:
            if (int(df.loc[home_idx, 'Played']) < int(fixtures["GameWeek"][i]) or int(df.loc[away_idx, 'Played']) < int(
                    fixtures["GameWeek"][i])):
                points_gained(df, outcome, home_form, away_form, home_idx, away_idx)
            if int(fixtures["GameWeek"][i]) == 38:
                df.loc[home_idx, 'PredictedPoints'] += (int(df.loc[home_idx, 'Points']))
                df.loc[away_idx, 'PredictedPoints'] += (int(df.loc[away_idx, 'Points']))

        # else start season from fresh
        else:
            points_gained(df, outcome, home_form, away_form, home_idx, away_idx)

    return df