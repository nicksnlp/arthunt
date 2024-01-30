# This the main file for NLP app project. Spring, 2024. Helsinki University.
from sklearn.feature_extraction.text import CountVectorizer
import nick, zongchan, xinyuan # Import functions from all members' works

# read from 100 wiki articles
with open('enwiki-20181001-corpus.100-articles.txt', 'r', encoding='UTF-8') as f:
    file_chunk = f.read().replace('\n', ' ')    # replace all newline characters with single space
    documents = file_chunk.split('</article>')  # split the file(str) into list
    del documents[-1]   # remove the last element, which is empty (which was caused by an </article> in the END of the document)
