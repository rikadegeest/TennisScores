#%%
#TODO: fix walkovers
import numpy as pd
url_done = pd.read_csv("url_done.csv") 

#%%
#cell to extract javascript based pages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_selenium_html_source(url):
    
    browser = webdriver.Chrome('/Users/rik/Downloads/chromedriver')
    browser.get(url)
    try:
        a = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "tabcontent"))
        )
        html = browser.page_source
        soup = BeautifulSoup(html)
    finally:
        browser.quit()
    return soup


#%%
#programm to download and visualise tennis results of the dutch competition

#setup
import requests
from bs4 import BeautifulSoup
import numpy as np 
import time


match_list = [["match_name", "home_team_player_1", "home_team_player_2", "away_team_player_1", "away_team_player_2", "team1_set_1", "team1_set_2", "team1_set_3", "team2_set_1","team2_set_2", "team2_set_3", "player1_won", "player2_won"]]
day_stats_list = [["classe", "date", "home_team", "away_team", "begin_time","score", "sets", "games"]]
session = requests.Session()

#return soup file from the starting url
def setup(url):
    #to accept the toernooi.nl cookies
    jar = requests.cookies.RequestsCookieJar()
    jar.set('st', 'l=1043&exp=44106.6793454745&c=1')
    session.cookies = jar

    #setup url
    res = session.get(url)
    res.raise_for_status()

    #get the temptempMatches in a soup
    soup = BeautifulSoup(res.text, 'html.parser')
    return(soup)

#makes soup of url
def soup_url(url):
    res = session.get(url)
    res.raise_for_status()

    #get the Matches in a soup
    soup = BeautifulSoup(res.text, 'html.parser')
    time.sleep(10)
    soup = BeautifulSoup(res.text, 'html.parser')
    return(soup)

#get whether match is single's or doubles
def single_or_double(match_name):
    if match_name[1:2] == 'E':
        return True
    else:
        return False

#checks if url is already scraped
def check_url_scraped(url):
    if url in url_done:
        return True
    else:
        return False

#return num sets played - 1
def check_sets_played(player_set_scores):
    if player_set_scores[2] == "":
        return 1
    else:
        return 2


#gets the stats of the day
def get_day_stats(soup):
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
    day_stats_list.append(dayStats)

#gets all Matches played on a day
def get_matches(soup):
    #temptempMatches
    match = soup.findAll('li', class_ = "match-group__item")

    for match in match:
        #grabs which match it is (he1, hd2, etc.)
        match_name = match.find('div', class_ = "match__header-title-main").find('span', class_ = 'nav-link__value').text
        print(match_name)
        
        if match.findAll('div', class_ = "match__row")[0].find('span',class_ = 'nav-link__value') is not None:
            player1_name = match.findAll('div', class_ = "match__row")[0].findAll('span',class_ = 'nav-link__value')[0].text
            player2_name = match.findAll('div', class_ = "match__row")[1].findAll('span',class_ = 'nav-link__value')[0].text

            if single_or_double(match_name):
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


            player1_set_scores = match.findAll('div', class_ = "match__row")[0]
            player2_set_scores = match.findAll('div', class_ = "match__row")[1]

            #check if walkover
            if player1_set_scores.find('li', class_='points__cell') is not None:
                player1_set_scores = player1_set_scores.findAll('li', class_='points__cell')
                player2_set_scores = player2_set_scores.findAll('li', class_='points__cell')

                for i in range(len(player1_set_scores)):
                    player1_set_scores[i-1] = player1_set_scores[i-1].text
                    player2_set_scores[i-1] = player2_set_scores[i-1].text

                if len(player1_set_scores) == 2:
                    empty_var = ""
                    player1_set_scores.append(empty_var)
                    player2_set_scores.append(empty_var)

                #checks winner
                if int(player1_set_scores[check_sets_played(player1_set_scores)]) > int(player2_set_scores[check_sets_played(player1_set_scores)]):
                    if single_or_double(match_name):
                        player1_won = player1_name
                        player2_won = ""
                    else:
                        player1_won = player1_name
                        player2_won = player12_name
                else:
                    if single_or_double(match_name):
                        player1_won = player2_name
                        player2_won = ""
                    else:
                        player1_won = player2_name
                        player2_won = player22_name
                
                matchStats = [match_name, home_team_player_1, home_team_player_2, away_team_player_1, away_team_player_2, player1_set_scores[0],player1_set_scores[1],player1_set_scores[2],player2_set_scores[0], player2_set_scores[1], player2_set_scores[2], player1_won, player2_won]
                match_list.append(matchStats)
            else:
                #walkover
                None
        else:
            #walkover
            None
                  
        

#get stats and matches every url in urlList
def get_one_team_stats_and_matches(url_list):
    for url in url_list:
        if check_url_scraped(url):
            None
        else:
            soup = soup_url(url)
            get_day_stats(soup)
            get_matches(soup)
            url_done.append(url)

#fils urlList with the url of every play day for a single team
def get_one_team_days_urls(soup):
    temp_url_list = []
    temp = soup.findAll('li', class_ ='match-group__item')
    for x in temp:
        #checks wheter day is played
        if x.find('div', class_='is-not-played') == None:
            url = 'https://mijnknltb.toernooi.nl' + x.find('a', class_ ='team-match__wrapper')['href']
            if (check_url_scraped):
                temp_url_list.append(url)
            else:
                None
        else:
            None
    return temp_url_list

#gets url of every team in competition
def get_one_competition_team_urls(soup):
    match_table = soup.find('table', class_='table--new')
    teams = match_table.findAll('tr')
    teams = teams[1:]
    temp_list = []
    for team in teams:
            url = 'https://mijnknltb.toernooi.nl' + team.find('a')['href']
            temp_list.append(url)
    return temp_list

#gets data from every team and every playdate in entire competition
def get_competition_data(soup):
    url_list = get_one_competition_team_urls(soup)
    for url in url_list:
        soup = soup_url(url)
        team_url_list = get_one_team_days_urls(soup)
        get_one_team_stats_and_matches(team_url_list)

#gets every team from a club
def get_club_team_urls(soup):
    match_groups = soup.findAll('div', class_='match-group')
    temp_url_list = []
    for match in match_groups:
        temp = match.find('ul', class_='list')
        teams = temp.findAll('li', class_='list__item', recursive=False)
        for team in teams:
            url = 'https://mijnknltb.toernooi.nl' + team.find('a')['href']
            temp_url_list.append(url)

    for temp_url in temp_url_list:
        soup = soup_url(temp_url)
        get_competition_data(soup)


startUrl = 'https://mijnknltb.toernooi.nl/league/02DF7F50-680B-493A-8804-0045BA39675E/club/1064/Index/teams'
soup = setup(startUrl)
soup = get_selenium_html_source(startUrl)
get_club_team_urls(soup)
#get_competition_data(soup)

#url_list = get_one_team_days_urls(soup)
#get_one_team_stats_and_matches(url_list)

#%%
import csv

with open("matches.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(match_list)

with open("url_done.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(url_done)





#%%
