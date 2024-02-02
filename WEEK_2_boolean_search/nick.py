# Nikolay Vorontsov, functions. NLP Apps 2024.
## IT SHOULD WORK I THINK, BUT NEEDS TESTING
from sklearn.feature_extraction.text import CountVectorizer
import nick, zongchan, main # Import functions from all members' worksnick, zongchan, xinyuan # Import functions from all members' works


#print contents of the retrived documents. Input: query -- string
def print_contents(query):

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







