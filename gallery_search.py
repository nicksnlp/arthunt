from flask import Flask, render_template, request
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import itertools, re
from web_scraping import extract_gallery_info
from data_visualization import bar_generator
"""
Make sure this is done:
# pip install -U spacy -- MAKE SURE THIS IS DONE
# python -m spacy download en_core_web_sm  -- MAKE SURE THIS IS DONE (may be python3 needed)

or uncomment the following(but it may not work):

try:
    import spacy
except ImportError:
    !pip install -U spacy
    import spacy
    !python -m spacy download en_core_web_sm
"""
import spacy

class GallerySearch:
    def __init__(self, gallery_url):
        self.gallery_url = gallery_url
        self.nlp = spacy.load('en_core_web_sm')
        self.boolean_operators = {"and": "&", "or": "|", "not": "1 -", "(": "(", ")": ")"} # formerly known as "d"
        
        self.exhib_titles, self.exhib_dates, self.exhib_locations, self.exhib_intro, self.exhib_articles, self.exhib_urls = extract_gallery_info(self.gallery_url)
        
#        self.exhib_titles_lemm, _ = self.lemmatize_text_with_ner(self.exhib_titles) # the second output left blank
#        self.exhib_dates_lemm, _ = self.lemmatize_text_with_ner(self.exhib_dates) # the second output left blank
#        self.exhib_locations_lemm, _ = self.lemmatize_text_with_ner(self.exhib_locations) # the second output left blank
#        self.exhib_intro_lemm, _ = self.lemmatize_text_with_ner(self.exhib_intro) # the second output left blank
        
        self.exhib_articles_lemm, self.people_mentioned_by_articles = self.lemmatize_text_with_ner(self.exhib_articles)
        
        self.tv, self.sparse_matrix_r, self.cv, self.sparse_matrix_b, self.terms, self.t2i = self.vectorize_articles(self.exhib_articles) # for NO lemmatization
        self.tv_lemm, self.sparse_matrix_r_lemm, self.cv_lemm, self.sparse_matrix_b_lemm, self.terms_lemm, self.t2i_lemm = self.vectorize_articles(self.exhib_articles_lemm) # for lemmatization:


    #Lemmatize all the following data: titles, locations, intro, articles (ONLY ARTICLES ARE USED IN THE SEARCH HOWEVER...):
    def lemmatize_text_with_ner(self, text_list):
        lemmatized_list = []
        people_mentioned_by_articles = []
        for item in text_list:
            if item is not None:
                doc = self.nlp(item)
                lemmatized_tokens = [token.lemma_ for token in doc]
                lemmatized_item = ' '.join(lemmatized_tokens)
                lemmatized_list.append(lemmatized_item)
                peoples_list = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
                people_mentioned_by_articles.append(list(set(peoples_list))) if peoples_list else people_mentioned_by_articles.append(["None"])
        return lemmatized_list, people_mentioned_by_articles

    # Lemmatize query (beware - input should not be empty)
    def lemmatize_query(self, query):
        doc = self.nlp(query)
        lemmatized_tokens = [token.lemma_ for token in doc] 
        query_lemm = ' '.join(lemmatized_tokens)

        return query_lemm
    
    def vectorize_articles(self, articles_list):    # sparse_matrix_r: 'r' for 'relevance', sparse_matrix_b：'b' for 'boolean'
        tv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
        sparse_matrix_r = tv.fit_transform(articles_list).T.tocsr()
        
        cv = CountVectorizer(lowercase=True, binary=True)
        sparse_matrix_b = cv.fit_transform(articles_list).T.tocsr()
        
        terms = cv.get_feature_names_out()
        t2i = cv.vocabulary_
        
        return tv, sparse_matrix_r, cv, sparse_matrix_b, terms, t2i

    def boolean_detector(self, query):    # decides whether to run boolean / relevance search
        
        q_split = query.lower().split()

        # logic operators that should not appear at the start/end of the query (except for not)
        non_starting_words = ['and', 'or', ')']
        non_ending_words = ['and', 'or', '(', 'not']

        # do not perform boolean search if:
        # 1) logic operator illegaly appears at the srart/end of query
        # 2) the query contains only one word
        if q_split[0] in non_starting_words or q_split[-1] in non_ending_words or len(q_split) == 1:
            return False
        else:
            return any(q in self.boolean_operators.keys() for q in q_split)

    def rewrite_query(self, query):  # rewrite query & convert retrieved rows to dense; rewrite every token in the query
        return " ".join(self.boolean_operators.get(t, f'self.sparse_matrix_b[self.t2i["{t}"]].todense()') for t in query.split())

    def rewrite_query_lemm(self, query):  # rewrite query & convert retrieved rows to dense; rewrite every token in the query
        return " ".join(self.boolean_operators.get(t, f'self.sparse_matrix_b[self.t2i_lemm["{t}"]].todense()') for t in query.split())

    def invalid_term(self, query, terms):
        return ", ".join(t for t in query.lower().split() if t not in terms)

    '''
    modifying the original wildcard search func: new name -> wildcard_parser
    now this func will only output list of queries with "*" replaced by all possible words in the vocab 
    and let the other search funcs do the search for it
    '''
    # replace words with '*' by possible words in the vocab,
    # store new queries in a list
    def wildcard_parser(self, query, terms):
        splited_query = query.lower().split()
        new_query_list = []
        
        # replace words with '*' by possible words in the vocab,
        # store new queries in a list
        
        # find the word with '*' 
        for idx, word in enumerate(splited_query):
            if "*" in word:
                #Nick's update 
                # replace each word with '*' by a list of all possible replacement words from vocab
                splited_query[idx] = list(t for t in terms if re.fullmatch(word.replace('*', '.*'), t))
                    
            # if no '*' in the current word, just turn word it into a list
            else:
                splited_query[idx] = [word]
            
        # generate new queries bease on the updated splited_query:
        splited_query = list(itertools.product(*splited_query))
        
        # store all possible new queries to new_query_list
        for l in splited_query:
            new_query_list.append(" ".join(l))

        return new_query_list

    def boolean_search(self, query):
        hits_matrix = eval(self.rewrite_query(query.lower()))
        idx_matches = list(hits_matrix.nonzero()[1]) # indices of matching contents                

        return idx_matches  

    def boolean_search_lemm(self, query):
        hits_matrix = eval(self.rewrite_query_lemm(query.lower()))
        idx_matches = list(hits_matrix.nonzero()[1]) # indices of matching contents                

        return idx_matches  

    def relevance_search(self, query, is_wildcard):  
        # use non-lemmatized matrix for wildcard search
        if is_wildcard:
            query_vec = self.tv.transform([query.lower()]).tocsc()       #convert query to vector
            hits = np.dot(query_vec, self.sparse_matrix_r)

        # use lemmatized matrix otherwise
        else:
            query_vec = self.tv_lemm.transform([query.lower()]).tocsc()       #convert query to vector
            hits = np.dot(query_vec, self.sparse_matrix_r_lemm)

        # rank doc by relevance (high -> low)
        ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
        num_matches = len(ranked_scores_and_doc_ids)            # the number of matching docs
        idx_matches = []                                        # indices of matching contents 

        if num_matches:      # there's at least 1 matching doc      
            for r in ranked_scores_and_doc_ids:
                idx_matches.append(r[1])

        return idx_matches

### REWRITE THE FOLLOWING FUNCTION
    def remove_unknown_terms(self, query):
        words = query.lower().split()
        words_good = []
        last_one_was_bad = 0
        
        #Check that the word appears at least in lemmatised or non lemmatised vocabulary, remove it otherwise, with possible and/or/not preceding it and following it
        for i, word in enumerate(words):
            
            if (word in self.terms_lemm) or (word in self.terms):

                #do not append and/or if follows the unknown word
                if last_one_was_bad == 1 and (words[i] == 'and' or words[i] == 'or'):
                    #do not append anything and proceed further
                    last_one_was_bad = 0

                else:
                    words_good.append(word)
                    last_one_was_bad = 0

            #check that the unknown word is not preceded by or/and/not, remove operator otherwise
            if (word not in self.terms_lemm) and (word not in self.terms):

                last_one_was_bad = 1
                #remove preceding and/or/nor
                if i >= 1 and (words[i-1] == 'and' or words[i-1] == 'or' or words[i-1] == 'not'):
                    if len(words_good) != 0: 
                        words_good.pop()        
                                
        return " ".join(w for w in words_good)
    
    
    def search(self, query):
        num_matches = 0
        idx_matches = []
        search_mode = "None. Try different query."    # default search mode
        naming_query = ''   # for the naming of generated bar chart
        query_lemm = ''

        
        # query not empty or == None -> get all matching idx then
        if query and not str(query).isspace():
            query = str(query).strip()      # remove starting & ending whitespaces
            query_known = self.remove_unknown_terms(query) ## REWRITE QUERY TO REMOVE UNKNOWN TERMS
            query_lemm = self.lemmatize_query(query_known)
            query_list = [query_lemm] #USING LEMMATISED QUERY
            invalid_words = self.invalid_term(query, self.terms)
            invalid_words_lemm = self.invalid_term(query_lemm, self.terms_lemm)

            try:
                #WILDCARD SEARCH: BOOLEAN or RELEVANCE 
                if "*" in query:
                    is_wildcard = True
                    # update query list:
                    query_list = self.wildcard_parser(query, self.terms)

                    # then do the search
                    for q in query_list:

                        # 1: boolean search
                        if self.boolean_detector(q):    
                            search_mode = "Boolean + Wildcard Search"
                            idx_matches_per_loop = self.boolean_search(q)
                            
                            for idx in idx_matches_per_loop: # prevent repetitions
                                if idx not in idx_matches:
                                    idx_matches.append(idx)

                        # 2: relevance search 
                        else:
                            search_mode = "Relevance + Wildcard Search"
                                                  
                            idx_matches_per_loop = self.relevance_search(q, is_wildcard)

                            for idx in idx_matches_per_loop: # prevent repetitions
                                if idx not in idx_matches:
                                    idx_matches.append(idx)                

                # BOOLEAN SEARCH, unknown terms removed
                #"am and cats" -- query, "be and cat" -- search
                elif self.boolean_detector(query):

                    search_mode = "Boolean Search + Lemmatization"

                    idx_matches_per_loop = self.boolean_search_lemm(query_lemm)

                    for idx in idx_matches_per_loop: # prevent repetitions
                        if idx not in idx_matches:
                            idx_matches.append(idx)

                # RELEVANCE SEARCH, unknown terms removed 
                else:
                    # mark that the query doesn't need wildcard search
                    is_wildcard = False

                    search_mode = "Relevance Search + Lemmatization"
                                          
                    idx_matches_per_loop = self.relevance_search(query_lemm, is_wildcard)

                    for idx in idx_matches_per_loop: # prevent repetitions
                        if idx not in idx_matches:
                            idx_matches.append(idx)
                                
            except:
                
                idx_matches = []
                

            # at least 1match found, then generate bar chart
            if idx_matches:
                # count total number of matches
                num_matches = len(idx_matches)
                
                # cannot have "*" in file name, do some replacements
                naming_query = query_list[0]
                if "*" in query:
                    naming_query += '_etc'
                    
                match_locations = [self.exhib_locations[idx] for idx in idx_matches]
                bar_generator(self.exhib_locations, match_locations, naming_query)

        # query contains multiple whitespaces
        elif str(query).isspace():
            query = None
        if query != None:
            return {
                    'query': str(query + " REWRITTEN QUERY: " + query_known  + ", matching : " + ", ".join(query_list)),
                    'naming_query': naming_query,
                    'idx_matches': idx_matches,
                    'num_matches': num_matches,
                    'search_mode': search_mode,
                    'exhib_titles': self.exhib_titles, 
                    'exhib_dates': self.exhib_dates, 
                    'exhib_locations': self.exhib_locations, 
                    'exhib_intro': self.exhib_intro, 
                    'exhib_articles': self.exhib_articles,
                    'exhib_urls': self.exhib_urls,
                    'people_mentioned_by_articles': self.people_mentioned_by_articles                     
            }
        else:
            return {
                    'query': query,
                    'naming_query': naming_query,
                    'idx_matches': idx_matches,
                    'num_matches': num_matches,
                    'search_mode': search_mode,
                    'exhib_titles': self.exhib_titles, 
                    'exhib_dates': self.exhib_dates, 
                    'exhib_locations': self.exhib_locations, 
                    'exhib_intro': self.exhib_intro, 
                    'exhib_articles': self.exhib_articles,
                    'exhib_urls': self.exhib_urls,
                    'people_mentioned_by_articles': self.people_mentioned_by_articles                     
            }
        
