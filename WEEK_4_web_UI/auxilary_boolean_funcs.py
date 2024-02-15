# some functions related to the boolean search are moved here to make the main py file easer to read

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