# This the main file for NLP app project. Spring, 2024. Helsinki University.
from sklearn.feature_extraction.text import CountVectorizer

# read from 100 wiki articles
def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as f:
        file_chunk = f.read().replace('\n', ' ')
        documents = file_chunk.split('</article>')
        del documents[-1]
    return documents

#generate term matrix
def term_matrix(documents):
    cv = CountVectorizer()
    sparse_matrix = cv.fit_transform(documents)
    dense_matrix = sparse_matrix.todense()
    td_matrix = dense_matrix.T
    terms = cv.get_feature_names_out()
    t2i = cv.vocabulary_
    return td_matrix, terms, t2i

d = {"and": "&", "AND": "&",
     "or": "|", "OR": "|",
     "not": "1 -", "NOT": "1 -",
     "(": "(", ")": ")"}          # operator replacements

def rewrite_token(t):
    return d.get(t, 'td_matrix[t2i.get("{:s}", 0)]'.format(t))

def rewrite_query(query): # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

#print contents of the retrived documents. Input: query -- string, documents -- text file(pre-proccessed)
def print_contents(query, documents):

    hits_matrix = eval(rewrite_query(query))
    
    hits_list = list(hits_matrix.nonzero()[1])
    print(hits_list)
    
    for i, doc_idx in enumerate(hits_list):
        print("Matching doc #{:d}  ".format(i))
        print(documents[doc_idx][:300])
        print()

def invalid_term(query, td_matrix, terms, t2i):
    if query in terms: # query = user input
        index = t2i[query]
        column_sum = td_matrix[index].sum()
        print(f"The term '{query}' found in article {column_sum}.")
        return True
    else:
        print(f"Invalid term: '{query}'. Please enter a valid word.")
        return False

file_name = 'enwiki-20181001-corpus.100-articles.txt'
documents = read_file(file_name)
td_matrix, terms, t2i = term_matrix(documents)

def main():
    #--------------------------------------------------------------------------------------
    # opening message, shows up only once from the beginning 
    print("Welcome! You can search for articles by entering a query using the keyboard!")
    print("-- To search for articles, please type your query, then press enter;")
    print("-- To QUIT searching, please enter 2 white spaces, then press enter.\n")

    # user's first input
    query = input("Your input here: ").lower() #convert input to lower case
    #--------------------------------------------------------------------------------------
    # keep asking for an input query until the user quits
    while query != "  ":
        if_exist = invalid_term(query, td_matrix, terms, t2i)
        if if_exist == False: # query word does not exist
            print(f"Sorry, the query '{query}' contain word(s) that is not in our word list. You may chose to:")
            print("1. Start a new search -- type your query and press enter")
            print("2. QUIT -- enter 2 white spaces and press enter\n")
            query = input("Your new input here: ").lower()
        else:
            print("Query recieved. We've found you these articles:")
            # a query recieved! go fetch the articles!
            # [NICK'S FUNCTION HERE]
            print_contents(query, documents)
            
            print("The search has completed. You may choose to:")
            print("1. Start a new search -- type your query and press enter")
            print("2. QUIT -- enter 2 white spaces and press enter\n")
            query = input("Your new input here: ").lower()

    # user choose QUIT, ending the while loop
    print("Got it. See you next time!")


main()
