from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

#Initialize Flask instance
app = Flask(__name__, static_folder='static')

def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as f:
        file_chunk = f.read().replace('\n', ' ')    # replace all newline characters with single space
        documents = file_chunk.split('</article>')  # split the file(str) into list
        del documents[-1]                           # remove the last element, which is empty (which was caused by an </article> in the END of the document)
    return documents
documents = read_file('enwiki-20181001-corpus.100-articles.txt')    # read docs: 100 wiki articles

cv = CountVectorizer(lowercase=True)
dense_matrix = cv.fit_transform(documents).T.todense()
terms = cv.get_feature_names_out()                  
t2i = cv.vocabulary_   
tfv5 = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix = tfv5.fit_transform(documents).T.tocsr()

def search_documents(query):
    matched_docs = [] 
    terms = query.split()  
    for term in terms:
        if term == '*':  
            matched_docs.extend(range(len(documents)))
        else:
            if '*' in term:
                prefix, suffix = term.split('*')
                for doc in documents:
                    if prefix in doc and suffix in doc:
                        matched_docs.append(doc)
            else:
                if term in t2i:
                    matched_docs.extend([documents[idx] for idx in sparse_matrix[t2i[term]].nonzero()[1]])  # Add matched documents to list
    return matched_docs


@app.route('/')
def greeting():
   return "Welcome, this is a simple search engine"

@app.route('/search')
def search():

    #Get query from URL variable
    query = request.args.get('query')
    matches = []

    if query:
        matches = search_documents(query)

    total_matches = len(matches)
    max_display = 15
    displayed_matches = matches[:max_display]
    return render_template('index.html', matches=displayed_matches, total_matches=total_matches, max_display=max_display)






