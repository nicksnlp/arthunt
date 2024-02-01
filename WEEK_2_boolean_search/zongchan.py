from sklearn.feature_extraction.text import CountVectorizer

def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as f:
        file_chunk = f.read().replace('\n', ' ')
        documents = file_chunk.split('</article>')
        del documents[-1]
    return documents

def term_matrix(documents):
    cv = CountVectorizer()
    sparse_matrix = cv.fit_transform(documents)
    dense_matrix = sparse_matrix.todense()
    td_matrix = dense_matrix.T
    terms = cv.get_feature_names()
    t2i = cv.vocabulary_
    return td_matrix, terms, t2i


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
