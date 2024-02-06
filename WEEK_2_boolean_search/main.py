from sklearn.feature_extraction.text import CountVectorizer

# get documetn contents -> list of strings
def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as f:
        file_chunk = f.read().replace('\n', ' ')    # replace all newline characters with single space
        documents = file_chunk.split('</article>')  # split the file(str) into list
        del documents[-1]                           # remove the last element, which is empty (which was caused by an </article> in the END of the document)
    return documents

# read from 100 wiki articles
documents = read_file('enwiki-20181001-corpus.100-articles.txt')


#generate term-document matrix
cv = CountVectorizer()                              # short for CountVectorizer()
sparse_matrix = cv.fit_transform(documents)         # sparse doc-term matrix
sparse_td_matrix = sparse_matrix.T.tocsr()          # convert matrix to CSR and transpose it
terms = cv.get_feature_names_out()                  # list of vocabs
t2i = cv.vocabulary_                                # t2i = term-to-index


# output words in the query that are not in the vocab
def invalid_term(query, terms):
    invalids = []
    for t in query.split():
        if t not in terms:
            invalids.append(t)
    return ",".join(invalids)


#---------------------------------------------------------------------
# boolean parser
d = {"and": "&", "or": "|", "not": "1 -", "(": "(", ")": ")"}   # operator replacements

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t))    # rewrite query & convert retrieved rows to dense

def rewrite_query(query):   # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())
#---------------------------------------------------------------------


# print relevant articles
def print_contents(query):
    hits_matrix = eval(rewrite_query(query))
    hits_list = list(hits_matrix.nonzero()[1])

    num_matches = len(hits_matrix.nonzero()[1]) # the number of matching docs

    if num_matches:     # CASE 1: there exists at least 1 matching doc
        # print the number of total matching docs found
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


# put repetitive printing messages into a function; it returns the new query from the user
def new_search():
    print("Now, you may chose to:")
    print("-- Re-enter your query: type your new query and press enter")
    print("-- QUIT: enter 2 white spaces and press enter\n")
    print("---------------------------------------------------------------------")        
    return input("Your new input here: ").lower()


#---------------------------------------------------------------------
# opening message, shows up only once from the beginning 
print("Welcome! You can search for articles by entering a query using the keyboard!\n")
print("-- To search for articles, please type your query, then press enter")
print("-- To QUIT searching, please enter 2 white spaces, then press enter\n")

# user's first input
print("---------------------------------------------------------------------")        
query = input("Your input here: ").lower()      # convert input to lower case


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
        print(f"\nSorry, our vacabulary doesn't contain '{invalid_words}', please input other words instead.\n")
        query = new_search()

    else: # proceed searching if there is no invalid word in the query
        print("\nTHIS QUERY IS VALID.\n")
        print_contents(query)   # a query recieved! go fetch & print the articles!
        print("The search has completed.")
        query = new_search()

# user choose QUIT, ending the while loop
print("\nYou have chosen QUIT. \nSee you next time then!")
