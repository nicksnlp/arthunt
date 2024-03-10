from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

'''documents = ["there is a greenhouse",
             "where are the houses?",
             "where is your house?",
             "there is a housing problem",
             "houses are expensive",
             "look, a lighthouse!",
             "house house house",
             "the house is over there"]'''

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
    matched_docs = set()  
    terms = query.split()  
    for term in terms:
        if term == '*':  
            matched_docs.update(range(len(documents)))
        else:
            if '*' in term:
                prefix, suffix = term.split('*')
                for doc_idx, doc in enumerate(documents):
                    if prefix in doc and suffix in doc:
                        matched_docs.add(doc_idx)
            else:
                if term in t2i:
                    matched_docs.update(list(sparse_matrix[t2i[term]].nonzero()[1]))    
    if matched_docs:
        print("Query terms found in the following documents:")
        count = 0
        for doc_idx in sorted(matched_docs):
            print(f"Document {count}: {documents[doc_idx][:300]}...\n")   
            count += 1
            if count == 11:
                break         
    else:
        print("Sorry, no matched result was found.")

def input_loop():
    print("Welcome!")
    while True:
        query = input("Please enter a new search term, or press 'q' to quit: ")
        if query == "q":
            break
        search_documents(query)

input_loop()





