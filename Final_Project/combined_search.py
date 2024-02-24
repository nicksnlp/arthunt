from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from flask import Flask, render_template, request
app = Flask(__name__)

def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as f:
        file_chunk = f.read().replace('\n', ' ')    # replace all newline characters with single space
        documents = file_chunk.split('Title:')  # split the file(str) into list
    return documents 


documents = read_file('exhibitions_data.txt')    # type = a list of strings

tv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix_r = tv.fit_transform(documents).T.tocsr()
cv = CountVectorizer(lowercase=True, binary=True)   
sparse_matrix_b = cv.fit_transform(documents).T.tocsr() 
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
        if t not in terms:
            invalids.append(t)
    return ", ".join(invalids)

     
def wildcard_search(query):
    query = query.lower()  # Convert query to lowercase for case-insensitive matching
    terms = query.split()  
    print("Query Parts:", terms)
    matches = []

    terms = query.split()  
    for term in terms:
        if term == '*':  
            matches.extend(range(len(documents)))
        else:
            if '*' in term:
                prefix, suffix = term.split('*')
 
                for doc in documents:
                    if prefix in doc and suffix in doc:
                        matches.append(doc)
            else:
                if term in t2i:
                    matches.extend([documents[idx] for idx in sparse_matrix_b[t2i[term]].nonzero()[1]])  

    num_matches = len(matches)
    matches = matches[:10]  # Retrieve only the top 10 matches
    if num_matches == 0:   
        return "no"

    return num_matches, matches


def boolean_search(query):    # print BOOLEAN search results (top 10 only)
    hits_matrix = eval(rewrite_query(query.lower()))
    hits_list = list(hits_matrix.nonzero()[1])
    num_matches = len(hits_list)    # the number of matching docs
    matches = []                    # the matching content 

    if num_matches:     # found at least 1 matching doc
        doc_count = 0   # count documents displayed
        for idx in hits_list: # get first 10 matching docs
            matches.append(documents[idx][:300])
            # stop printing when doc_count reaches 10
            doc_count += 1
            if doc_count == 10:
                break
    return num_matches, matches        
  

def relevance_search(query):     # print RELEVANCE search results (top 10 only)
    query_vec = tv.transform([query.lower()]).tocsc()       #convert query to vector
    hits = np.dot(query_vec, sparse_matrix_r)
    ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
    num_matches = len(ranked_scores_and_doc_ids)    # the number of matching docs
    matches = []                    # the matching content 

    if num_matches:      # found at least 1 matching doc       
        doc_count = 0
        for r in ranked_scores_and_doc_ids:
            matches.append(documents[r[1]][:300])
            doc_count += 1
            if doc_count == 10:
                break
    return num_matches, matches              

# ------------------------------------------

@app.route('/')
def welcoming_message():
   return "Hi! We are group IKEA Meatballs! Welcome to our search engine!"


@app.route('/search')
def search():
    query = str(request.args.get('query'))    #Get query from URL variable
    #invalid_words = invalid_term(query, terms)
    matches = []
    num_matches = 0
    search_mode = "Relevance Search"

    if query:
        num_matches, matches = wildcard_search(query)
        if "*" in query:
            search_mode = "Wildcard Search"
        elif boolean_detector(query):     # CASE 1: query fits boolean search
            search_mode = "Boolean Search"
            num_matches, matches = boolean_search(query)
    elif not query:
        print ('none')
    else:           
        num_matches, matches = relevance_search(query)
    
    return render_template('index_combined.html', matches=matches, num_matches=num_matches, search_mode=search_mode)

