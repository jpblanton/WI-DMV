# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 08:57:08 2017

@author: James
"""

import re, sys, requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

"""
Talk with Bradley about JS scraping to get the missing centers
Mapping stuff is ready in R, just export this to csv, import it in R
and plot the amounts
"""

def time_from_series(s):
    #will need to check for special rules cases, can do that after extracting times
    open_df = s.str.extractall('(\d):?(\d{2})? a.m.')
    close_df = s.str.extractall('(\d):?(\d{2})? p.m.')
    #If there is a NaN, it's because someone wrote 9 a.m. instead of 9:00 a.m.
    #So we know it's a zero
    open_df = open_df.fillna(0)
    close_df = close_df.fillna(0)
    opens = pd.Series(index = open_df.index.levels[0])
    closes = pd.Series(index = close_df.index.levels[0])
    
    for day in open_df.index.levels[0]:
        h = float(open_df.loc[day].loc[:,0])
        m = float(open_df.loc[day].loc[:,1]) / 60
        opens[day] = h + m
        
    for day in close_df.index.levels[0]:
        h = float(close_df.loc[day].loc[:,0])
        m = float(close_df.loc[day].loc[:,1]) / 60
        closes[day] = h + m + 12

    return closes - opens
    
get_name_rgx = re.compile('=(.*)')

url = 'http://wisconsindot.gov/Pages/online-srvcs/find-dmv/default.aspx'
hdr = {'User-Agent': 'Mozilla/5.0'}

x = requests.get(url, hdr).content
x = BeautifulSoup(x, 'lxml')

#tables[0] is the list of cities
#tables[1] is the list of counties
tables = x.find_all('table', attrs = {'class' : 'ms-rteTable-default'})

cities = tables[0].find_all('a')
counties = tables[1].find_all('a')

links = []

for cell in cities:
    links.append(cell.attrs['href'])
    
for cell in counties:
    links.append(cell.attrs['href'])
    
names = []
for link in links:
    names.append(get_name_rgx.search(link).group(1))
    
openings = []
bad_links = []
wi_index = []

for link in links:
    data = requests.get(link, hdr).content

    data = BeautifulSoup(data, 'lxml')
    days = data.find('div', attrs = {'id' : 'hoursDiv'})
    if (days is None):
        print(link, ' is not formatted normally. Skipping.')
        bad_links.append(get_name_rgx.search(link).group(1))
        continue
    days = days.find_all('span')
    keys = []
    for day in days:
        keys.append(str(day.text).strip(' :'))
        
    df_dict = {}
    for i in range(len(keys)):
        df_dict[keys[i]] = str(days[i].next_sibling).strip()
    openings.append(df_dict)
    
    wi_index.append(str(data.find('div', attrs={'id' : 'stationNameDiv'}).text).strip())
        
hours = pd.DataFrame(openings, index = wi_index)
hours = hours.assign(loc = wi_index)
hours = hours.drop_duplicates()

