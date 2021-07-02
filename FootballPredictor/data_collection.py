import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from predictor import *


def league_data(url, league_urls):
    #get html from page to access the table
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    #get table and table rows
    table = soup.find_all('table')[0]
    rows = table.find_all('tr')
    #set up blank array to append data
    array = []

    #loop through each column in each row and clean up the form data
    for row in rows:
        row_array = []
        form_array = []
        columns = row.find_all('td')
        for column in columns:
            forms = column.find_all(class_="gs-u-vh")
            str = '$td-11'
            if str not in column['data-reactid'] and "team" not in column.text:
                #print(column.text)
                row_array.append(column.text)

            for form in forms:
                if form.text[0] in ['W', 'L', 'D']:
                    form_array.append(form.text[0])
        row_array.append(form_array)
        array.append(row_array)

    #remove redundant rows
    array.pop(0)
    array.pop(len(array)-1)

    #rename DataFrame columns and return
    df = pd.DataFrame(array, columns =['Position', 'Names', 'Played', 'Won', 'Drawn', 'Lost',
                                       'For', 'Against', 'GD', 'Points', 'Form'])

    #add more rows and columns for urls, points, form and strength
    df = df.sort_values('Names')
    df['TeamUrls'] = league_urls
    starting_points = []
    starting_form = []
    team_strength = []
    for url in league_urls:
        #squad_urls = get_player_urls(url)
        url = url.replace("squad", "team-ranking-history")
        #squad_avg = get_avg_rating(squad_urls)
        team_avg = get_avg_rating(url)
        #team_strength.append((squad_avg + team_avg)/2)
        team_strength.append(team_avg)
        starting_points.append(0)
        starting_form.append(0)
    df['PredictedPoints'] = starting_points
    df['TeamStrength'] = team_strength
    df['PredictedForm'] = starting_form
    df = df.sort_index(axis=0)

    return df


def get_player_urls(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    #get table and table rows
    table = soup.find_all('table')[2]
    rows = table.find_all('tr')
    players = []
    for row in rows:
        #row_array = []
        #form_array = []
        #columns = row.find_all('td')
        ratings_class = row.find_all(class_="ratings sel_A")
        for rating in ratings_class:
            for a in rating.find_all('a', href=True):
                link = a['href']
                #print(link)
                players.append(link)
    return players


def get_avg_rating(urls):
    team_rating = []
    if type(urls) == list:
        for url in urls:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = BeautifulSoup(webpage, 'html.parser')
            soup = str(soup)
            start = soup.find("Week 52, 2020")
            end = soup.find("//AVERAGE RATING")
            avg_data = soup[start:end]
            # get all the player ratings to create an overall
            team_rating.append(get_overall_data(avg_data, urls))

    else:
        url = urls
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        soup = str(soup)
        start = soup.find("Week 28, 2020")
        end = soup.find("//AVERAGE RATING")
        avg_data = soup[start:end]
        rating = get_overall_data(avg_data, urls)
        team_rating.append(rating)

    team_rating = np.nanmean(team_rating)
    return team_rating


def get_overall_data(avg_data, urls):
    ratings = []
    # get all the player ratings to create an overall
    for i in range(0, len(avg_data) - 1):
        if avg_data[i:i + 9] == '"value": ':
            rating = avg_data[i + 9: i + 11]
            ratings.append(int(rating))
    if len(ratings) > 0:
        return np.nanmean(ratings)
    else:
        return np.nan