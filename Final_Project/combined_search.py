# -*- coding: utf-8 -*-
# +
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from flask import Flask, render_template, request
import itertools

from web_scraping import extract_gallery_info
from data_visualization import bar_generator

# pip install -U spacy -- MAKE SURE THIS IS DONE
# python -m spacy download en_core_web_sm  -- MAKE SURE THIS IS DONE (may be python3 needed)
import spacy

# Load the spaCy English model
nlp = spacy.load('en_core_web_sm')

# -

# gallery to be scraped (key = gallery name, value = gallery url)
# stroed in a dictionary to make adding new galleries convenient
gallery_2_url = {'Tate':'https://www.tate.org.uk/whats-on'} 

exhib_titles, exhib_dates, exhib_locations, exhib_intro, exhib_articles, exhib_urls = extract_gallery_info(gallery_2_url)

# ------

#Lemmatise all the following data: titles, locations, intro, articles: ONLY ARTICLES ARE USED IN THE SEARCH HOWEVER...
exhib_titles_lemm = []
for item in exhib_titles:
    doc = nlp(item)
    lemmatized_tokens = [token.lemma_ for token in doc]
    lemmatized_item = ' '.join(lemmatized_tokens)

    exhib_titles_lemm.append(lemmatized_item)

exhib_locations_lemm = []
for item in exhib_locations:
    doc = nlp(item)
    lemmatized_tokens = [token.lemma_ for token in doc]
    lemmatized_item = ' '.join(lemmatized_tokens)

    exhib_locations_lemm.append(lemmatized_item)

exhib_intro_lemm = []
for item in exhib_intro:
    if item is not None:
        doc = nlp(item)
        lemmatized_tokens = [token.lemma_ for token in doc]
        lemmatized_item = ' '.join(lemmatized_tokens)

        exhib_intro_lemm.append(lemmatized_item)

exhib_articles_lemm = []
for item in exhib_articles:
    doc = nlp(item)
    lemmatized_tokens = [token.lemma_ for token in doc]
    lemmatized_item = ' '.join(lemmatized_tokens)

    exhib_articles_lemm.append(lemmatized_item)

# Lemmatise query (beware - input should not be empty)
def lemmatise_query(query):
    doc = nlp(query)
    lemmatized_tokens = [token.lemma_ for token in doc] 
    query_lemm = ' '.join(lemmatized_tokens)

    return query_lemm

# -------

tv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix_r = tv.fit_transform(exhib_articles_lemm).T.tocsr()        # sparse_matrix_r: 'r' for 'relevance'

cv = CountVectorizer(lowercase=True, binary=True)   
sparse_matrix_b = cv.fit_transform(exhib_articles_lemm).T.tocsr()        # sparse_matrix_b：'b' for 'boolean'

terms = cv.get_feature_names_out()
t2i = cv.vocabulary_ 

d = {"and": "&", "or": "|", "not": "1 -", "(": "(", ")": ")"}       # boolean operators


def boolean_detector(query):    # decide whether to run boolean / relevance search

    q_split = query.lower().split()

    # logic operators that should not appear at the start/end of the query (except for not)
    non_starting_words = ['and','or',')']
    non_ending_words = ['and','or','(', 'not']

    # do not perform boolean search if:
    # 1) logic operator illegaly appears at the srart/end of query
    # 2) the query contains only one word
    if q_split[0] in non_starting_words or q_split[-1] in non_ending_words or len(q_split) == 1:
        return False
    else:
        for q in q_split:
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
        if '*' not in t and t not in terms:     # exceptions: wildcard
            invalids.append(t)
    return ", ".join(invalids)


'''
modifying the original wildcard search func: new name -> wildcard_parser
now this func will only output list of queries with "*" replaced by all possible words in the vocab 
and let the other search funcs do the search for it
'''
def wildcard_parser(query, terms):
    splited_query = query.lower().split()
    new_query_list = []
    
    # replace words with '*' by possible words in the vocab,
    # store new queries in a list
    
    # find the word with '*' 
    for idx, word in enumerate(splited_query):
        if "*" in word:
            # ignors the middle part if there's more than 1 "*" in the word
            prefix = word.split('*')[0]
            suffix = word.split('*')[-1]

            #possible replacements for the current word in query
            replacement_words = []   
            
            # find all possible replacements
            for t in terms:
                if t.startswith(prefix) and t.endswith(suffix):
                    replacement_words.append(t)
                    
            # replace each word with '*' by a list of all possible replacement words from vocab
            splited_query[idx] = replacement_words
            
        # if no '*' in the current word, just trun it into a list
        else:
            splited_query[idx] = [word]
            
    # generate new queries bease on the updated splited_query:
    splited_query = list(itertools.product(*splited_query))
    
    # store new all possible queries to new_query_list
    for l in splited_query:
        new_query_list.append(" ".join(l))    

    return new_query_list


def boolean_search(query):   
    hits_matrix = eval(rewrite_query(query.lower()))
    idx_matches = list(hits_matrix.nonzero()[1])            # indices of matching contents                

    return idx_matches  


def relevance_search(query):     
    query_vec = tv.transform([query.lower()]).tocsc()       #convert query to vector
    hits = np.dot(query_vec, sparse_matrix_r)
    
    # rank doc by relevance (high -> low)
    ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
    num_matches = len(ranked_scores_and_doc_ids)            # the number of matching docs
    idx_matches = []                                        # indices of matching contents 

    if num_matches:      # there's at least 1 matching doc      
        for r in ranked_scores_and_doc_ids:
            idx_matches.append(r[1])
            
    return idx_matches              

# ------------------------------------------

app = Flask(__name__)

@app.route('/')
def welcoming_message():
    return render_template('home_page.html')


@app.route('/search')
def search():
    query = request.args.get('query')   # get query from URL variable
    
    num_matches = 0
    idx_matches = []  
    search_mode = "Relevance Search"            # default search mode
    naming_query = ''                           # for the naming of generated bar chart
    query_lemm = ''

    # query not empty or == None -> get all matching idx then
    if query:
        query = str(query).strip()      # remove starting & ending whitespaces
        query_lemm = lemmatise_query(query)
        query_list = [query_lemm]
        invalid_words = invalid_term(query_lemm, terms)

        # do the searching if there's no invalid term in the query (those with "*" do not count as invalid)
        if not invalid_words:  
            
            # change query_list if there's any '*' in the input query
            if "*" in query:
                search_mode = "Wildcard Search"  
                query_list = wildcard_parser(query_lemm, terms)
            
            # then do the search
            for q in query_list:
                
                # 1: boolean search  
                if boolean_detector(q):     
                    search_mode = "Boolean Search"
                    idx_matches_per_loop = boolean_search(q)

                    for idx in idx_matches_per_loop: # prevent repetitionss
                        if idx not in idx_matches:
                            idx_matches.append(idx)

                # 2: relevance search    
                else:                           
                    idx_matches_per_loop = relevance_search(q)

                    for idx in idx_matches_per_loop: # prevent repetitions
                        if idx not in idx_matches:
                            idx_matches.append(idx)

            # at least 1match found, then generate bar chart
            if idx_matches:
                 # count total number of matches
                num_matches = len(idx_matches)
                
                # cannot have "*" in file name, do some replacements
                naming_query = query_list[0]
                if "*" in query:
                    naming_query += '_etc'
                    
                match_locations = [exhib_locations[idx] for idx in idx_matches]
                bar_generator(exhib_locations, match_locations, naming_query)

    return render_template('index_combined.html', 
                           query = query,
                           query_lemm = query_lemm,
                           naming_query = naming_query,
                           idx_matches = idx_matches, 
                           num_matches = num_matches,
                           search_mode = search_mode,
                           exhib_titles = exhib_titles, 
                           exhib_dates = exhib_dates, 
                           exhib_locations = exhib_locations, 
                           exhib_intro = exhib_intro, 
                           exhib_articles = exhib_articles,
                           exhib_urls = exhib_urls,
                           )
