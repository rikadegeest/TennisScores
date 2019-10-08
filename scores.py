#%%
urlDone = []

#%%
#programm to download and visualise tennis results of the dutch competition

#setup
import requests
from bs4 import BeautifulSoup
import numpy as np 


matchList = []
dayStatsList = []
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
    dayStats = {}
    match_day = soup.find('div', class_ = "team-match-header module module--dark module--card")

    classe = match_day.find('a').text
    date = match_day.find('div', class_='text--xsmall').time.text
    home_team = match_day.find('h2', class_ = 'is-team-1')['title']
    away_team = match_day.find('h2', class_ = 'is-team-2')['title']
    begin_time =  match_day.findAll('div', class_ = 'text--center')[1].text
    score = match_day.findAll('span', class_ = 'module__footer-item-value')[0].text
    sets = match_day.findAll('span', class_ = 'module__footer-item-value')[1].text
    games = match_day.findAll('span', class_ = 'module__footer-item-value')[2].text

    dayStats['league'] = classe
    dayStats['date'] = date
    dayStats['home_team'] = home_team
    dayStats['away_team'] = away_team
    dayStats['begin_time'] = begin_time
    dayStats['score'] = score
    dayStats['sets'] = sets
    dayStats['games'] = games

    dayStatsList.append(dayStats)

#gets all temptempMatches played on a day
def getMatches(soup):
    #temptempMatches
    match = soup.findAll('li', class_ = "match-group__item")

    for match in match:
        tempMatches = {}
        #grabs which match it is (he1, hd2, etc.)
        match_name = match.find('div', class_ = "match__header-title-main").find('span', class_ = 'nav-link__value').text

        tempMatches['match_name'] = match_name

        if singleOrDouble(match_name):
            player1_name = match.findAll('div', class_ = "match__row")[0].find('span',class_ = 'nav-link__value').text
            player2_name = match.findAll('div', class_ = "match__row")[1].find('span',class_ = 'nav-link__value').text

            tempMatches['home_team_player1'] = player1_name
            tempMatches['away_team_player1'] = player2_name
        else:
            player1_name = match.findAll('div', class_ = "match__row")[0].findAll('span',class_ = 'nav-link__value')[0].text
            player2_name = match.findAll('div', class_ = "match__row")[1].findAll('span',class_ = 'nav-link__value')[0].text

            player12_name = match.findAll('div', class_ = "match__row")[0].findAll('span',class_ = 'nav-link__value')[1].text
            player22_name = match.findAll('div', class_ = "match__row")[1].findAll('span',class_ = 'nav-link__value')[1].text

            tempMatches['home_team_player1'] = player1_name
            tempMatches['home_team_player2'] = player12_name
            tempMatches['away_team_player1'] = player2_name
            tempMatches['away_team_player2'] = player22_name

        player1_set_scores = []
        player2_set_scores = []

        player1_set_scores = match.findAll('div', class_ = "match__row")[0].findAll('li', class_='points__cell')
        player2_set_scores = match.findAll('div', class_ = "match__row")[1].findAll('li', class_='points__cell')

        for i in range(len(player1_set_scores)):
            #set i uitslag toevoegen aan list 
            player1_set_scores[i] = player1_set_scores[i].text
            player2_set_scores[i] = player2_set_scores[i].text

            temp1 = 'team1_set' + str(i)
            temp2 = 'team2_set' + str(i)
            tempMatches[temp1] = player1_set_scores[i]
            tempMatches[temp2] = player2_set_scores[i]

        #checks winner  
        if int(player1_set_scores[len(player1_set_scores) - 1]) > int(player2_set_scores[len(player1_set_scores) - 1]):
            if singleOrDouble(match_name):
                player_won = player1_name
                tempMatches['player1_won'] = player_won
            else:
                player1_won = player1_name
                player2_won = player12_name
                tempMatches['player1_won'] = player1_won
                tempMatches['player2_won'] = player2_won
        else:
            if singleOrDouble(match_name):
                player_won = player2_name
                tempMatches['player1_won'] = player_won
            else:
                player1_won = player2_name
                player2_won = player22_name
                tempMatches['player1_won'] = player1_won
                tempMatches['player2_won'] = player2_won
        matchList.append(tempMatches)

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
                break
        else:
            break

def checkUrlScraped(url):
    if url in urlDone:
        return True
    else:
        return False

#get stats and matches every url in urlList
def getOneTeamStatsAndMatches():
    for url in urlList:
        soup = soupUrl(url)
        urlList.remove(url)
        getDayStats(soup)
        getMatches(soup)
        urlDone.append(url)

soup = setup()
#getOneTeamDaysUrls(soup)
#getOneTeamStatsAndMatches()
#getOneTeamDaysUrls(soup)
#getDayStats(soup)
#getMatches(soup)



#%%
