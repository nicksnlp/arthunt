import nltk, re, pprint
from nltk import word_tokenize
from urllib import request
from bs4 import BeautifulSoup

# retreat info from Sally's Baking Recipes (Pies, Crisps, & Tarts)
url = "https://sallysbakingaddiction.com/category/desserts/pies-crisps-tarts/"
html = request.urlopen(url).read().decode('utf8')

# pre-processed content
raw = raw = BeautifulSoup(html, 'html.parser').get_text()

# tokenize raw data
tokens = word_tokenize(raw)
text = nltk.Text(tokens)
