import urllib3
import os
import requests
import re
from bs4 import BeautifulSoup
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

url="https://www.imdb.com/chart/top?ref_=nv_mv_250"
# os.environ['NO_PROXY'] = 'imdb.com'
req = requests.get(url)
page = req.text

soup = BeautifulSoup(page, 'html.parser')

links=[]
for a in soup.find_all('a'): #, href=True):
    links.append(a.get('href'))
links=['https://www.imdb.com'+a.strip() for a in links if a is not None and a.startswith('/title/tt') ]

#---------------------------Remove duplicates in links
top_250_links=[]
for c in links:
    if c not in top_250_links:
        top_250_links.append(c)
#top_250_links=top_250_links[2:]

# print(len(top_250_links))
top_250_links[0:5]

# column_list=['Rank','Movie_name' ,'URL' ,'Release_Year' ,'IMDB_Rating' ,
# 'Reviewer_count' ,'Censor_Board_Rating' ,'Movie_Length' ,'Genre_1' ,
# 'Genre_2' ,'Genre_3' ,'Genre_4' ,'Release_Date' ,'Story_Summary' ,
# 'Director' ,'Writer_1' ,'Writer_2' ,'Writer_3' ,'Star_1' ,
# 'Star_2' ,'Star_3' ,'Star_4' ,'Star_5' ,'Plot_Keywords' ,'Budget' ,
# 'Gross_USA' ,'Cum_Worldwide_Gross' ,'Production_Company' 
# ]
# df = pd.DataFrame(columns=column_list)#,index=t) 

countryset = set()
# genredict = {}
# directordict = {}
# actordict = {}


for x in np.arange(0, len(top_250_links)):

    
    #---------------------------Load html page for 1st movie in top 250 movies    
    url=top_250_links[x]
    # print(url)
    req = requests.get(url)
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')
    
    #---------------------------Retrieve Movie details from html page
    # Movie_name=(soup.find("div",{"class":"title_wrapper"}).get_text(strip=True).split('|')[0]).split('(')[0]
        
    # year_released=((soup.find("div",{"class":"title_wrapper"}).get_text(strip=True).split('|')[0]).split('(')[1]).split(')')[0]
        
    # imdb_rating=soup.find("span",{"itemprop":"ratingValue"}).text
    
    # reviewer_count=soup.find("span",{"itemprop":"ratingCount"}).text
    # box_office_details = []
    # box_office_dictionary = {'Country'}
    # for details in soup.find_all("div",{"class":"txt-block"}):
    #     detail = details.get_text(strip=True).split(':')
    #     # print(detail)
        
    #     if detail[0] == "Country":
    #         # box_office_details.append(detail)
    #         # print(detail[0])
    #         # print(detail[1])
            
    #         country = detail[1].split("|")
    #         # countrydict[x] = country
    #         for c in country:
    #             # print("("+str(x+1)+", \""+c+"\"),")
    #             countryset.add(c)
        # print(country)
    # print(countryset)
    # for detail in box_office_details:
    #     if detail[0] in box_office_dictionary:
    #         box_office_dictionary.update({detail[0] : detail[1]})
    
    # while len(country) < 4: 
    #     country.append(' ')
    # subtext= soup.find("div",{"class":"subtext"}).get_text(strip=True).split('|') #Censor_rating
    # if len(subtext)<4:
    #     censor_rating='Not Rated'
    #     movie_len=subtext[0]
    #     genre_list=subtext[1].split(',')
    #     # while len(genre_list)<4:         genre_list.append(" ")
    #     # genre_1,genre_2,genre_3,genre_4=genre_list
    #     release_date=subtext[2]
    # else:
    #     censor_rating=subtext[0]
    #     movie_len=subtext[1]
    #     genre_list=subtext[2].split(',')
    #     # while len(genre_list)<4:         genre_list.append(" ")
    #     # genre_1,genre_2,genre_3,genre_4=genre_list
        
    # #     release_date=subtext[3]
    # # genredict[x] = genre_list
    # for i in range(len(genre_list)):
    #     print('('+(str)(x+1)+', "'+genre_list[i]+'"),')
    # story_summary=soup.find("div",{"class":"summary_text"}).get_text(strip=True).strip()
    
    #---------------------------Director,Writer and Actor details
    # summary = soup.find("div", {"class":"summary_text"}).get_text( strip=True ).strip()
    # # Getting the credits for the director and writers
    # credit_summary = []
    # for summary_item in soup.find_all("div",{ "class" : "credit_summary_item" }):
    #     credit_summary.append(re.split( ',|:|\|' ,summary_item.get_text( strip=True )))
    
    # stars = credit_summary.pop()[1:4]
    # writers = credit_summary.pop()[1:3]
    # director = credit_summary.pop()[1:]

    # print("(" + str(x+1) + ",\"" + director[0] + "\", \'M\', "+"\"1970-1-1"+ "\"),")

    castlist = soup.find("table", {"class":"cast_list"})
    cast = castlist.find_all("tr", {"class":"odd"})[0:3]
    for c in cast:
        t = c.get_text().split('...')
        actor = t[0].strip()
        role = c.find("td", {"class":"character"}).find("a").get_text()
        # role = t[1].strip()
        print("(" + str(x+1) + ", \"" + actor +"\", "+ '\'F\'' + ", \"1977-4-1\", \"" + role + "\"),")





    #---------------------------Plot Keywords
    # b=[]
    # for a in soup.find_all("span",{"class":"itemprop"}):     b.append(a.get_text(strip=True))  
    
    # plot_keywords='|'.join(b)
    
    # #---------------------------Commercial details and Prod Company
    
    
    # b=[]                    #---------------------------Remove unwanted entries
    # d={'Budget':'', 'Opening Weekend USA':'','Gross USA':'','Cumulative Worldwide Gross':'','Production Co':''}
    # for a in soup.find_all("div",{"class":"txt-block"}):
    #     c=a.get_text(strip=True).split(':')
    #     if c[0] in d:
    #         b.append(c)
    
    # for i in b:             #---------------------------Update default values if entries are found
    #         if i[0] in d: 
    #             d.update({i[0]:i[1]})                
        #print(d)
    
    # production_company=d['Production Co'].split('See more')[0]
    # cum_world_gross=d['Cumulative Worldwide Gross'].split(' ')[0]
    # gross_usa=d['Gross USA'].split(' ')[0]
    # budget=d['Budget']
    
    # print(x,":",Movie_name)
    #---------------------------Dictionary to holds all details
    # movie_dict={
    #     'Rank':x+1,
    #     'Movie_name' : Movie_name,
    #     'URL' : url,
    #     'Release_Year' : year_released,
    #     'IMDB_Rating' : imdb_rating,
    #     'Reviewer_count' : reviewer_count,
    #     'Censor_Board_Rating' : censor_rating,
    #     'Movie_Length' : movie_len,
    #     'Genre_1' : genre_1,
    #     'Genre_2' : genre_2,
    #     'Genre_3' : genre_3,
    #     'Genre_4' : genre_4,
    #     'Release_Date' : release_date,
    #     'Story_Summary' : story_summary,
    #     'Director' : director,
    #     'Writer_1' : writer_1,
    #     'Writer_2' : writer_2,
    #     'Writer_3' : writer_3,
    #     'Star_1' : star_1,
    #     'Star_2' : star_2,
    #     'Star_3' : star_3,
    #     'Star_4' : star_4,
    #     'Star_5' : star_5,
    #     'Plot_Keywords' : plot_keywords,
    #     'Budget' : budget,
    #     'Gross_USA' : gross_usa,
    #     'Cum_Worldwide_Gross' : cum_world_gross,
    #     'Production_Company' : production_company
    #     }
    # #print(movie_dict['Rank'],":",movie_dict['Movie_name'])
    
    # #---------------------------Append rows to dataframes using dictionary
print(countryset)
    # df = df.append(pd.DataFrame.from_records([movie_dict],columns=movie_dict.keys() ) )