#FJ-240814

from bs4 import BeautifulSoup
import os
import os.path
import pathlib
import html
import re
import requests
import matplotlib.pyplot as plt


start_url = "https://www.svenskafans.com/fotboll/dif/arkiv/2024"
sf_url = "https://www.svenskafans.com"
filename = "dif.txt"
player_rating_pages = []
player_names = []
misspelled_names = ["Tokmac Nguyen", "Nguen Tokmac"]
players = []


class Player:
    def __init__(self, name, rating, avg_rating=0, match_count=1):
        self.name = name
        self.rating = rating
        self.avg_rating = avg_rating
        self.match_count = match_count
        
    def increment_rating(self, val):
        self.rating += val
        self.match_count += 1


def find_player_rating_pages():
    current_articles = requests.get(start_url)
    soup = BeautifulSoup(current_articles.content, "html.parser")
    html_list = soup.find_all("a", href=True)
    for tag in html_list:
            new_url = tag['href']
            if "/fotboll/dif/spelarbetyg" in new_url:
                player_rating_pages.append(tag['href'])
                
def find_ratings():
    for pageurl in player_rating_pages: 
        rating_url = sf_url + pageurl
        rating_article = requests.get(rating_url)
        soup = BeautifulSoup(rating_article.content, "html.parser")
        html_list = soup.find_all("strong")
        for tag in html_list:
            tag_string = tag.get_text().replace(u'\xa0', u' ')
            if "-" in tag_string:
                player_info = tag_string.split("-")
                player_name = player_info[0].strip()
                player_rating = player_info[1].strip()
                if(player_rating.isdigit()):
                    player_rating = int(player_info[1])
                else:
                    continue
                
                if("(" in player_name):
                    player_name = player_name.split("(")[0].strip()
            
                if(player_name.replace(" ", "").isalpha() and player_name not in misspelled_names):
                    if(player_name not in player_names):
                        player_names.append(player_name)
                        player = Player(player_name, player_rating)
                        players.append(player)
                    else:
                        for existing_player in players:
                            if(player_name == existing_player.name):
                                existing_player.increment_rating(player_rating)
                            
                if player_name not in player_names:
                    player_names.append(player_name)
                        
    for player in players:    
        avg_rating = player.rating / player.match_count
        player.avg_rating = round(avg_rating,2)
        
        
def visualize_data():
    fig, ax = plt.subplots(figsize=(16,16))
    sorted_players = sorted(players, key=lambda p:p.avg_rating, reverse=False)
        
    for player in sorted_players:
        if(player.match_count > 4):
            avg_rating = player.rating / player.match_count
            player.avg_rating = round(avg_rating,2)
            bars = plt.barh(y=player.name, width=player.avg_rating, color="blue")
            ax.text(player.avg_rating + 0.01,player.name,player.avg_rating,va='center',ha='left',color='black')
            
    plt.show()
        

find_player_rating_pages()
find_ratings()
visualize_data() 