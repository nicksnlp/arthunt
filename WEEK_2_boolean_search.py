documents = [""]

from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(lowercase=True, binary=True)
sparse_matrix = cv.fit_transform(documents)

dense_matrix = sparse_matrix.todense()
td_matrix = dense_matrix.T   # .T transposes the matrix
print(cv.get_feature_names_out())

terms = cv.get_feature_names_out()
print(cv.vocabulary_) # note the _ at the end