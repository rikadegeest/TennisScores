#%%
urlDone = []
urlList = []

#%%
#programm to download and visualise tennis results of the dutch competition

#setup
import requests
from bs4 import BeautifulSoup
import numpy as np 


matchList = [["match_name", "home_team_player_1", "home_team_player_2", "away_team_player_1", "away_team_player_2", "team1_set_1", "team1_set_2", "team1_set_3", "team2_set_1","team2_set_2", "team2_set_3", "player1_won", "player2_won"]]
dayStatsList = [["classe", "date", "home_team", "away_team", "begin_time","score", "sets", "games"]]
urlList = []
session = requests.Session()

#return soup file
def setup():
    #to accept the toernooi.nl cookies
    jar = requests.cookies.RequestsCookieJar()
    jar.set('st', 'l=1043&exp=44106.6793454745&c=1')
    session.cookies = jar

    #setup url
    startUrl = 'https://mijnknltb.toernooi.nl/league/02DF7F50-680B-493A-8804-0045BA39675E/team/418'
    res = session.get(startUrl)
    res.raise_for_status()

    #get the temptempMatches in a soup
    soup = BeautifulSoup(res.text, 'html.parser')
    return(soup)

#makes soup of url
def soupUrl(url):
    res = session.get(url)
    res.raise_for_status()

    #get the temptempMatches in a soup
    soup = BeautifulSoup(res.text, 'html.parser')
    return(soup)

#get whether match is single's or doubles
def singleOrDouble(match_name):
    if match_name[1:2] == 'E':
        return True
    else:
        return False

#gets the stats of the day
def getDayStats(soup):

    match_day = soup.find('div', class_ = "team-match-header module module--dark module--card")

    #gets information from html
    classe = match_day.find('a').text
    date = match_day.find('div', class_='text--xsmall').time.text
    home_team = match_day.find('h2', class_ = 'is-team-1')['title']
    away_team = match_day.find('h2', class_ = 'is-team-2')['title']
    begin_time =  match_day.findAll('div', class_ = 'text--center')[1].text
    score = match_day.findAll('span', class_ = 'module__footer-item-value')[0].text
    sets = match_day.findAll('span', class_ = 'module__footer-item-value')[1].text
    games = match_day.findAll('span', class_ = 'module__footer-item-value')[2].text

    dayStats = [classe, date, home_team, away_team, begin_time, score, sets, games]
    dayStatsList.append(dayStats)

#gets all temptempMatches played on a day
def getMatches(soup):
    #temptempMatches
    match = soup.findAll('li', class_ = "match-group__item")

    for match in match:
        #grabs which match it is (he1, hd2, etc.)
        match_name = match.find('div', class_ = "match__header-title-main").find('span', class_ = 'nav-link__value').text


        player1_name = match.findAll('div', class_ = "match__row")[0].findAll('span',class_ = 'nav-link__value')[0].text
        player2_name = match.findAll('div', class_ = "match__row")[1].findAll('span',class_ = 'nav-link__value')[0].text

        if singleOrDouble(match_name):
            home_team_player_1 = player1_name
            home_team_player_2 = ""
            away_team_player_1 = player2_name
            away_team_player_2 = ""

        else:
            player12_name = match.findAll('div', class_ = "match__row")[0].findAll('span',class_ = 'nav-link__value')[1].text
            player22_name = match.findAll('div', class_ = "match__row")[1].findAll('span',class_ = 'nav-link__value')[1].text

            home_team_player_1 = player1_name
            home_team_player_2 = player12_name
            away_team_player_1 = player2_name
            away_team_player_2 = player22_name

        player1_set_scores = match.findAll('div', class_ = "match__row")[0].findAll('li', class_='points__cell')
        player2_set_scores = match.findAll('div', class_ = "match__row")[1].findAll('li', class_='points__cell')

        for i in range(len(player1_set_scores)):
            player1_set_scores[i-1] = player1_set_scores[i-1].text
            player2_set_scores[i-1] = player2_set_scores[i-1].text

        if len(player1_set_scores) == 2:
            empty_var = ""
            player1_set_scores.append(empty_var)
            player2_set_scores.append(empty_var)

        #checks winner
        if int(player1_set_scores[check_sets_played(player1_set_scores)]) > int(player2_set_scores[check_sets_played(player1_set_scores)]):
            if singleOrDouble(match_name):
                player1_won = player1_name
                player2_won = ""
            else:
                player1_won = player1_name
                player2_won = player12_name
        else:
            if singleOrDouble(match_name):
                player1_won = player2_name
                player2_won = ""
            else:
                player1_won = player2_name
                player2_won = player22_name
        matchStats = [match_name, home_team_player_1, home_team_player_2, away_team_player_1, away_team_player_2, player1_set_scores[0],player1_set_scores[1],player1_set_scores[2],player2_set_scores[0], player2_set_scores[1], player2_set_scores[2], player1_won, player2_won]
        matchList.append(matchStats)

#return num sets played - 1
def check_sets_played(player_set_scores):
    if player_set_scores[2] == "":
        return 1
    else:
        return 2

#fils urlList with the url of every play day for a single team
def getOneTeamDaysUrls(soup):
    temp = soup.findAll('li', class_ ='match-group__item')
    for x in temp:
        #checks wheter day is played
        if x.find('div', class_='is-not-played') == None:
            url = 'https://mijnknltb.toernooi.nl' + x.find('a', class_ ='team-match__wrapper')['href']
            if (checkUrlScraped):
                urlList.append(url)
            else:
                None
        else:
            None

#checks if url is already scraped
def checkUrlScraped(url):
    if url in urlDone:
        return True
    else:
        return False

#get stats and matches every url in urlList
def getOneTeamStatsAndMatches():
    for url in urlList:
        if checkUrlScraped(url):
            None
        else:
            soup = soupUrl(url)
            getDayStats(soup)
            getMatches(soup)
            urlDone.append(url)


def test():
    for url in urlList:
        soup = soupUrl(url)
        getDayStats(soup)
        getMatches(soup)
    
soup = setup()
getOneTeamDaysUrls(soup)
getOneTeamStatsAndMatches()
#getOneTeamStatsAndMatches()

#%%
#this cell is to clean the code
from datetime import datetime as dt

def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(i)

def parse_date(date):
    return dt.strptime(date, '%Y-%m-%d')

def nog_naar_kijken():
    for match in matchList:
        match['team1_set1'] = parse_maybe_int(match['team1_set1'])
        match['team1_set2'] = parse_maybe_int(match['team1_set2'])
        match['team2_set1'] = parse_maybe_int(match['team1_set1'])
        match['team2_set2'] = parse_maybe_int(match['team2_set2'])
        if 'team1_set3' in match:
            match['team1_set3'] = parse_maybe_int(match['team1_set3'])
            match['team2_set3'] = parse_maybe_int(match['team2_set3'])    
        else:
            None


#%%
import csv

with open("matches.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(matchList)






#%%
