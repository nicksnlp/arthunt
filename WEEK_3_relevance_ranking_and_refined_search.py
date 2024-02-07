from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as f:
        file_chunk = f.read().replace('\n', ' ')    # replace all newline characters with single space
        documents = file_chunk.split('</article>')  # split the file(str) into list
        del documents[-1]                           # remove the last element, which is empty (which was caused by an </article> in the END of the document)
    return documents    # type: list of strings


documents = read_file('enwiki-20181001-corpus.100-articles.txt')    # read docs: 100 wiki articles

cv = CountVectorizer(lowercase=True, binary=True)   
sparse_matrix_b = cv.fit_transform(documents).T.tocsr() 
terms = cv.get_feature_names_out()                  
t2i = cv.vocabulary_                                

tv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix_r = tv.fit_transform(documents).T.tocsr()

d = {"and": "&", "or": "|", "not": "1 -", "(": "(", ")": ")"}       # boolean operators


def boolean_detector(query):    # decide whether to run boolean / relevance search
    for q in query.split():
        if q in d.keys():
            return True
    return False


# --------------------------boolean parser
def rewrite_token(t):       # rewrite query & convert retrieved rows to dense
    return d.get(t, 'sparse_matrix_b[t2i["{:s}"]].todense()'.format(t))    

def rewrite_query(query):   # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())
# --------------------------


def invalid_term(query, terms): # output words in the query that are not in the vocab
    invalids = []
    for t in query.split():
        if t not in terms:
            invalids.append(t)
    return ", ".join(invalids)


def print_boolean_search(query):    # print BOOLEAN search results (top 10 only)
    hits_matrix = eval(rewrite_query(query))
    hits_list = list(hits_matrix.nonzero()[1])
    num_matches = len(hits_list) # the number of matching docs

    if num_matches:     # CASE 1: there exists at least 1 matching doc
        print(f"{num_matches} matching document(s) found (max. 10 of these documents will be displayed below):\n")         
        doc_count = 0   # count documents displayed
        for i, doc_idx in enumerate(hits_list): #ptint matching docs (first 10 of them)
            print(f"Matching doc #{i+1:d}: \n {documents[doc_idx][:300]}...\n")     # print the first 500 characters in the article (to save space)
            # stop printing when doc_count reaches 10
            doc_count += 1
            if doc_count == 10:
                break
    else:               # CASE 2: no matching docs found
        print("Sorry, no matching documents found :(\n")     


def print_relevance_search(query):     # print RELEVANCE search results (top 10 only)
    query_vec = tv.transform([query]).tocsc()       #convert query to vector
    hits = np.dot(query_vec, sparse_matrix_r)
    ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
    num_matches = len(ranked_scores_and_doc_ids)    # the number of matching docs
    
    if num_matches:     # CASE 1: there exists at least 1 matching doc       
        print(f"{num_matches} relevant document(s) found (max. 10 of these documents will be displayed below):\n") 
        doc_count = 0
        for score, i in ranked_scores_and_doc_ids:
            print(f"Relevant doc #{doc_count+1:d} (score = {score:.4f}): \n{documents[i][:300]}...\n")
            doc_count += 1
            if doc_count == 10:
                break
    else:               # CASE 2: no matching docs found
        print("Sorry, no matching documents found :(\n")         


# +
# put repetitive printing messages into a function; it returns the new query from the user
def new_search():
    print("Now, you may chose to:")
    print("-- Re-enter your query: type your new query and press enter")
    print("-- QUIT: enter 2 white spaces and press enter\n")
    print("---------------------------------------------------------------------")        
    return input("Your new input here: ").lower()

#--------------------------------------------------------------------- input loop
# opening message, shows up only once from the beginning 
print("Welcome! You can search for articles by entering a query using the keyboard!\n")
print("-- To search for articles, please type your query, then press enter")
print("-- To QUIT searching, please enter 2 white spaces, then press enter\n")
print("---------------------------------------------------------------------")        
query = input("Your input here: ").lower()      # # user's first input

# keep asking for an input query until the user quits
while query != "  ":
    invalid_words = invalid_term(query, terms)
    
    # when input only contain white spaces (not including 2 spaces, which is the QUIT move)
    if not query.split():
        print("\nOops, your input is empty!")
        print("(Psst! If you were actually trying to QUIT, check if you've accidentaly entered less or more than 2 white spaces!)\n")
        query = new_search()

    # do not search for any thing if there is any invalid word in the query
    elif len(invalid_words):    # length not equal to 0 -> invalid word exists
        print("\nINVALID TERM(S) DETECTED.\n")
        print(f"Sorry, our vacabulary doesn't contain '{invalid_words}', please input other words instead.\n")
        query = new_search()

    else: # proceed searching if there is no invalid word in the query
        print("\nTHIS QUERY IS VALID.\n")
        if boolean_detector(query):     # CASE 1: query fits boolean search
            print("-- MODE: Boolean Search --\n")
            print_boolean_search(query)   
        else:                           # CASE 2: query fits relevance search
            print("-- MODE: Relevance-ranked Search --\n")
            print_relevance_search(query)    

        print("The search has completed.")
        query = new_search()

# user choose QUIT, ending the while loop
print("\nYou have chosen QUIT. \nSee you next time then!")
