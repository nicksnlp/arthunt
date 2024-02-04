# Nikolay Vorontsov, functions. NLP Apps 2024.
import zongchan # Import functions from other members' works

from sklearn.feature_extraction.text import CountVectorizer
#generate term matrix
td_matrix, terms, t2i = zongchan.term_matrix(documents)

d = {"and": "&", "AND": "&",
     "or": "|", "OR": "|",
     "not": "1 -", "NOT": "1 -",
     "(": "(", ")": ")"}          # operator replacements

def rewrite_token(t):
    return d.get(t, 'td_matrix[t2i["{:s}"]]'.format(t)) 

def rewrite_query(query): # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

#print contents of the retrived documents. Input: query -- string
def print_contents(query, documents):

    hits_matrix = eval(rewrite_query(query))
    
    hits_list = list(hits_matrix.nonzero()[1])
    print(hits_list)

    for i, doc_idx in enumerate(hits_list):
        # print m amount of characters for a document
        for char in documents[doc_idx]:
            print("Matching doc:", documents[doc_idx])
            if char >= 300:
                print("------------")
                break







