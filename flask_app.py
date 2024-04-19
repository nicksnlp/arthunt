from flask import Flask, render_template, request
from gallery_search import GallerySearch
import os, shutil

def clear_data():
    # remove old plots:
    for filename in os.listdir('./static/'):
        if filename.startswith('query_') and filename.endswith('_plot.png'):
            filepath = os.path.join('./static/', filename)
            os.remove(filepath)

#------

app = Flask(__name__)
data_file_path = './static/scraped_data.json'

if os.path.exists(data_file_path):
    pass
else:
    shutil.copy('./back_up_json/scraped_data.json', './static/scraped_data.json') # COPY DATA from a back up, USE SHUTIL both for linux/mac and win
        
gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'})

clear_data()

@app.route('/')
def welcoming_message():
    return render_template('home_page.html')

@app.route('/search')
def search():
        
    query = request.args.get('query')
    search_data = gallery_search.search(query)
    return render_template('index_combined.html', **search_data)

### with help of CHATGPT and some thinking and rewriting
@app.route('/scrape', methods=['POST'])
def scrape():

    if os.path.exists(data_file_path):
        try: #try scraping the file
            os.remove(data_file_path) #need to remove old data, in order to initiate the new scraping (in gallery_search.extract_gallery_info / web_scraping.extract_gallery_info)
            gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'})
            scrape_message = "Old JSON file removed. Scraping restarted. New file created."
        except: #if scraping failed (for eny reason, e.g. corrupted website), use back_up file
            shutil.copy('./back_up_json/scraped_data.json', './static/scraped_data.json') # USE SHUTIL both for linux/mac and win
            gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'}) # it uses data from a file, otherwise scrapes
            scrape_message = "Old JSON file removed. Scraping failed. Back-up data is used."

        
    else: #.json file is missing for any reason (for example the process was interrupted earlier)
        try: #try scraping the web        
            gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'})
            scrape_message = "Old JSON file not found. Scraping restarted. New file created."
        except: #if scraping failed (for eny reason, e.g. corrupted website), use back_up file
            shutil.copy('./back_up_json/scraped_data.json', './static/scraped_data.json') # USE SHUTIL both for linux/mac and win
            gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'}) # it uses data from a file, otherwise scrapes
            scrape_message = "Old JSON file not found. Scraping failed. Back-up data is used."

            
    clear_data()
    return render_template('index_combined.html', scrape_message=scrape_message)

### CHATGPT ends, writing ends, thinking never ends...
