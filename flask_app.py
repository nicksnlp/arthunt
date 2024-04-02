from flask import Flask, render_template, request
from gallery_search import GallerySearch
import os

app = Flask(__name__)
gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'})

@app.route('/')
def welcoming_message():
    return render_template('home_page.html')

@app.route('/search')
def search():

    query = request.args.get('query')
    search_data = gallery_search.search(query)
    return render_template('index_combined.html', **search_data)

### with help of CHATGPT and some thinking
@app.route('/scrape', methods=['POST'])
def scrape():

    data_file_path = 'scraped_data.json'
    if os.path.exists(data_file_path):
        os.remove(data_file_path)
        scrape_message = "Old JSON file removed. Scraping restarted."
        gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'})
        
    else:
        scrape_message = "Old JSON file not found. Scraping restarted."
        gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'})

    return render_template('index_combined.html', scrape_message=scrape_message)

    
    scrape_message = "JSON file removed and Flask restarted."
    return render_template('index_combined.html', scrape_message=scrape_message)
### CHATGPT ends, thinking never ends...
