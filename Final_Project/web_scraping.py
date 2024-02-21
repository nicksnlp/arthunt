# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests


'''
FUNCTION INPUT:
The function below works for the Tate gallery website (debugged & tested)
To extract gallery info from Tate, you can define the following variable (type = dictionary) first:

gallery_2_url = {'Tate':'https://www.tate.org.uk/whats-on'} 

and use it as the input when calling function 'extract_gallery_info(gallery_2_url)':
'''

'''
FUNCTION OUTPUTS:
the function outputs 5 lists, including:
all exhibitions'...
1. titles
2. dates
3. locations
4. intro articles
5. url for EACH exhibition's page

NOTE: any missing info will be stored as None type in the lists; 
      thus,in all 5 lists, the same index number should point to the SAME exhibition!
'''


def extract_gallery_info(gallery_2_url):

    # initialize 5 types of info from each exhibition
    exhib_titles = []         # 1. titles
    exhib_dates = []          # 2. dates
    exhib_locations = []      # 3. locations
    exhib_intro = []          # 4. intro articles
    exhib_urls = []           # 5. url for EACH exhibition's page

    # loop through all exhibition pages (max 20 per page) -- OUTER LOOP 
    # and loop through all exhibitions on each of these pages -- INNER LOOP 

    # initialize current_url as the first page's url
    current_url = gallery_2_url.get('Tate')

    # this is used to cancatenate with href --> get valid new url as a whole
    home_url = current_url[:23]

    # OUTER LOOP  
    while current_url:     # continue looping before reaching the end page
        
        # reset current page
        page = requests.get(current_url)        
        soup = BeautifulSoup(page.text, 'html.parser')

        # get all exhibition info on the current webpage
        mixed_info = soup.find_all('div', class_ = 'card')
        
        # reset current page hrefs(to each exhibition's own page) 
        current_page_hrefs = []  
        
        # get urls for each exhibition's own page
        for i in mixed_info:
            info_chunck = i.find_all('a')
            for j in info_chunck:
                new_url = home_url+j.attrs['href']
                
                # prevent url repetitions
                if new_url not in current_page_hrefs:
                    current_page_hrefs.append(new_url)     # update current page hirefs
                    exhib_urls.append(new_url)             # accumulate all urls 
        
        # INNER LOOP     
        # extract from each exhibition on their seperate web page
        for href in current_page_hrefs:
            
            page2 = requests.get(href)
            soup2 = BeautifulSoup(page2.text, 'html.parser')
       
            # 1. title
            title = soup2.find('h1', class_ = "splash-header__fulltitle")
            if title:  # content not empty
                title =  title.text.strip()
            exhib_titles.append(title)

            # 2. date
            date = soup2.find('span',class_ = "splash-header__dates")
            if date:  # content not empty
                date = date.text.strip()
            else:
                date = soup2.find('div',class_="content__info-dates")   # for some pages, date is displayed in different format
                if date:  # content not empty
                    date = date.text.strip()                    
            exhib_dates.append(date)
            
            # 3. location 
            location = soup2.find('span', class_ = "splash-header__venue")
            if location:  # content not empty
                location = location.text.strip()
            else:
                location = soup2.find('div',class_="content__info-location")   # for some pages, location is displayed in different format
                if location:  # content not empty
                    if location.find('p'):
                        location = location.find('p').get_text(strip = True,separator=" - ")            
            exhib_locations.append(location)
            
            # 4. intro article
            intro = soup2.find('div', class_ = "block-rich_text")
            if intro:  # content not empty
                intro = intro.text.strip()
            exhib_intro.append(intro)        
        
        # get url for exhibitions on the other page
        next_page = soup.find_all('li', class_ = 'pager__item pager__item--next')  
        
        # check if reaches the end of all pages & update current page url accordingly
        if next_page:  
            current_url = home_url + next_page[0].find('a').attrs['href']
        else:
            current_url = ''

    return exhib_titles, exhib_dates, exhib_locations, exhib_intro, exhib_urls
