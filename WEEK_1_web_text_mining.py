import nltk, re, pprint
from nltk import word_tokenize
from urllib import request

# retreat info from Sally's Baking Recipes (Pies, Crisps, & Tarts)
url = "https://sallysbakingaddiction.com/category/desserts/pies-crisps-tarts/"
response = request.urlopen(url)

# pre-processed content
raw = response.read().decode('utf8')

# tokenie raw data
tokens = word_tokenize(raw)
