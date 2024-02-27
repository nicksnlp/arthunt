# +
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from flask import Flask, render_template, request

from web_scraping import extract_gallery_info
from data_visualization import bar_generator
# -


# gallery to be scraped (gallery name: homepage url)
# stroed in a dictionary to make adding new galleries convenient
gallery_2_url = {'Tate':'https://www.tate.org.uk/whats-on'} 

exhib_titles, exhib_dates, exhib_locations, exhib_intro, exhib_articles, exhib_urls = extract_gallery_info(gallery_2_url)

tv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix_r = tv.fit_transform(exhib_articles).T.tocsr()
cv = CountVectorizer(lowercase=True, binary=True)   
sparse_matrix_b = cv.fit_transform(exhib_articles).T.tocsr() 
terms = cv.get_feature_names_out()                  
t2i = cv.vocabulary_ 

d = {"and": "&", "or": "|", "not": "1 -", "(": "(", ")": ")"}       # boolean operators


def boolean_detector(query):    # decide whether to run boolean / relevance search
    for q in query.split():
        if q in d.keys():
            return True
    return False


def rewrite_token(t):       # rewrite query & convert retrieved rows to dense
    return d.get(t, 'sparse_matrix_b[t2i["{:s}"]].todense()'.format(t))    


def rewrite_query(query):   # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())


def invalid_term(query, terms): # output words in the query that are not in the vocab
    invalids = []
    for t in query.lower().split():
        if '*' not in t and t not in terms:
            invalids.append(t)
    return ", ".join(invalids)


def wildcard_search(query, docs):
    query = query.lower()  # Convert query to lowercase for case-insensitive matching
    terms = query.split()  
    matches = []

    # terms = query.split()  
    for term in terms:
        if term == '*':  
            matches.extend(range(len(docs)))
        else:
            if '*' in term:
                prefix, suffix = term.split('*')
 
                for doc in docs:
                    if prefix in doc and suffix in doc:
                        matches.append(doc)
            else:
                if term in t2i:
                    matches.extend([docs[idx] for idx in sparse_matrix_b[t2i[term]].nonzero()[1]])  

    num_matches = len(matches)
    # matches = matches[:10]  # Retrieve only the top 10 matches
    # if num_matches == 0:   
    #     return "no"

    return num_matches, matches


def boolean_search(query, docs):   
    hits_matrix = eval(rewrite_query(query.lower()))
    hits_list = list(hits_matrix.nonzero()[1])
    num_matches = len(hits_list)    # the number of matched docs
    matches = []                    # contents of matched docs

    if num_matches:     # there's at least 1 matching doc
        for idx in hits_list: # get matching docs
            matches.append(docs[idx][:300])
    return num_matches, matches        


def relevance_search(query, docs):     
    query_vec = tv.transform([query.lower()]).tocsc()       #convert query to vector
    hits = np.dot(query_vec, sparse_matrix_r)
    # rank doc by relevance (high -> low)
    ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
    num_matches = len(ranked_scores_and_doc_ids)    # the number of matching docs
    matches = []                                    # the matching content 

    if num_matches:      # there's at least 1 matching doc      
        for r in ranked_scores_and_doc_ids:
            matches.append(docs[r[1]][:300])
    return num_matches, matches              


# ------------------------------------------

app = Flask(__name__)

@app.route('/')
def welcoming_message():
    return "Hi! We are group IKEA Meatballs! Welcome to our search engine!"


@app.route('/search')
def search():
    query = str(request.args.get('query'))      # Get query from URL variable
    invalid_words = invalid_term(query, terms)
    matches = []
    num_matches = 0
    search_mode = "Relevance Search"            # default search mode

    # if query:
    #     num_matches, matches = wildcard_search(query)
    #     if "*" in query:
    #         search_mode = "Wildcard Search"
    #     elif boolean_detector(query):     # CASE 1: query fits boolean search
    #         search_mode = "Boolean Search"
    #         num_matches, matches = boolean_search(query)
    # elif not query:
    #     print ('none')
    # else:           
    #     num_matches, matches = relevance_search(query)

    if query:
        # do the searching if there's no invalid term in the query (those with "*" do not count as invalid)
        if not invalid_words:  

             # 1: boolean search  
            if boolean_detector(query):     
                search_mode = "Boolean Search"
                num_matches, matches = boolean_search(query, exhib_articles)   

            # 1: wildcard search
            elif "*" in query:
                search_mode = "Wildcard Search"  
                num_matches, matches = wildcard_search(query, exhib_articles) 

            # 3: relevance search    
            else:                           
                num_matches, matches = relevance_search(query, exhib_articles)
    
    return render_template('index_combined.html', 
                           query = query, 
                           matches=matches, 
                           num_matches=num_matches, 
                           search_mode=search_mode
                           )
