from flask import Flask, render_template, request, jsonify
from gallery_search import GallerySearch

app = Flask(__name__)
gallery_search = GallerySearch({'Tate': 'https://www.tate.org.uk/whats-on'})

@app.route('/')
def welcoming_message():
    return render_template('home_page.html')

@app.route('/search')
def search():
    query = request.args.get('query') # get query from URL variable
    search_data = gallery_search.search(query)
    return render_template('index_combined.html', **search_data)
