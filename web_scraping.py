# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import requests

data_file_path = "data/scraped_data.json"

'''
FUNCTION INPUT:
The function below works for the Tate gallery website (debugged & tested)
To extract gallery info from Tate, you can define the following variable (type = dictionary) first:

gallery_2_url = {'Tate':'https://www.tate.org.uk/whats-on'} 

and use it as the input when calling function 'extract_gallery_info(gallery_2_url)':
'''

'''
FUNCTION OUTPUTS:
the function outputs 6 lists, including:
all exhibitions'...
1. titles
2. dates
3. locations
4. brief intro 
5. articles
6. url for EACH exhibition's page

NOTE: any missing info will be stored as None type in the lists; 
      thus,in all 5 lists, the same index number should point to the SAME exhibition!
'''
def load_data_from_file(data_file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None

def save_data_to_file(data, data_file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def extract_gallery_info(gallery_2_url):
    # Check if data exists in the file
    saved_data = load_data_from_file(data_file_path)
    if saved_data:
        return saved_data
    
    # Data not found in file, proceed with scraping
    # initialize 6 types of info from each exhibition
    exhib_titles = []         # 1. titles
    exhib_dates = []          # 2. dates
    exhib_locations = []      # 3. locations
    exhib_intro = []          # 4. brief intro
    exhib_articles = []       # 5. article 
    exhib_urls = []           # 6. url for EACH exhibition's page

    # loop through all exhibition overview pages (max 20 per page) -- OUTER LOOP 
    # and loop through all exhibitions on each of these pages -- INNER LOOP 

    # initialize current_url as the first page's url
    current_url = gallery_2_url.get('Tate')

    # this is used to cancatenate with href --> get valid new url as a whole
    home_url = current_url[:23]

    # OUTER LOOP  
    while current_url:     # continue looping before reaching the end page
        
        # reset current overview page
        page = requests.get(current_url)        
        soup = BeautifulSoup(page.text, 'html.parser')

        # get all exhibition info on current overview page
        mixed_info = soup.find_all('div', class_ = 'card')
        
        # reset current page hrefs(to each exhibition's own page) 
        current_page_hrefs = []  

        # 4. brief intros for each exhibition
        for i in mixed_info:
            info_chunck = i.find_all('div', class_ = "card__description")
            if not info_chunck:   # exhibition without intro info
                exhib_intro.append(None)
            else:
                for intro in info_chunck:
                    intro = intro.text.strip().replace(u'\xa0', u' ')
                    exhib_intro.append(intro)
            
        # 6. collect url for each exhibition's own page
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
                date = date.get_text(strip = True,separator = "; ") 
            else:
                date = soup2.find('div',class_="content__info-dates")   # for some pages, date is displayed in different format
                if date:  # content not empty
                    date = date.get_text(strip = True,separator = "; ")                    
            exhib_dates.append(date)
            
            # 3. location 
            location = soup2.find('span', class_ = "splash-header__venue")
            if location:  # content not empty
                location = location.text.strip()
            else:
                location = soup2.find('div',class_="content__info-location")   # for some pages, location is displayed in different format
                if location:  # content not empty
                    if location.find('p'):
                        location = location.find('p').get_text(strip = True,separator = " - ")
                        location = location.split(" - ")[0]
            exhib_locations.append(location)
            
            # 5. article
            article = soup2.find('div', class_ = "block-rich_text")
            if article:  # content not empty
                article = article.text.strip()
            exhib_articles.append(article)        
        
        # get url for exhibitions on the next page
        next_page = soup.find_all('li', class_ = 'pager__item pager__item--next')  
        
        # check if reaches the end of all pages & update current page url accordingly
        if next_page:  
            current_url = home_url + next_page[0].find('a').attrs['href']
        else:
            current_url = ''

    # After scraping, save the data to the file
    data = {
        'titles': exhib_titles,
        'dates': exhib_dates,
        'locations': exhib_locations,
        'intro': exhib_intro,
        'articles': exhib_articles,
        'urls': exhib_urls
    }
    save_data_to_file(data, data_file_path)

    
    return exhib_titles, exhib_dates, exhib_locations, exhib_intro, exhib_articles, exhib_urls
