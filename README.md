# About our project:

This is a continuation of a team-project IKEA Meatballs (https://github.com/zccwqdoorchid/IKEA-meatballs/tree/main/Final_Project) by XinyanMO, nicksnlp, and zccwqdoorchid.

The project runs on <strong>flask</strong> and requires the following libraries:  <strong>scikit-learn, spacy, beautifulsoup </strong>.

The following improvements have been made:

1.Wildcard search, bugs fixed.\
2.Boolean search, bugs fixed.\
3.The structure of the project: the functions are moved into a class GallerySearch within gallery_search.py, from where the call of the web_scraping.py and data_visualization.py are initiated.\
4.The main flask_app.py handles the html, and feeds the url-link and the query from user into the gallery_search.py.\
5.Scraping data is saved into an external scraped_data.json, as a dictionary. If it is not present there, the new scraping is initiated (may take around 5 minutes to complete).\
6."Scrape the WEB again" button on the loading page. Removes the data, initiates the new scraping process.

This way the project can be easier handled by web hosting environments, and/or incorporated into other applications.

FUTURE IMPROVEMNTS:
7. to deploy the project on pythonanywhere
8. include neural search

The project can be tested with the following commands:

Mac/Linux users:

Setting up the environment (python3 is already installed):

```
python3 -m venv demoenv
. demoenv/bin/activate
pip install Flask
pip install -U spacy
python -m spacy download en_core_web_sm
pip install beautifulsoup4
pip install -U scikit-learn
pip install -U matplotlib
```

clone the repository:
```
git clone git@github.com:nicksnlp/arthunt.git
cd arthunt
```

Run the flask:
```
export FLASK_APP=flask_app.py  
export FLASK_DEBUG=True  
export FLASK_RUN_PORT=8000
```

Then in your browser open: http://127.0.0.1:8000



Below is the description of the original project:
-------
Hi! We are team IKEA Meatballs (XinyanMO, nicksnlp, and zccwqdoorchid)!
Our project is a search engine for on-going and upcoming art exhibitions at different branches of Tate galleries.
You can search for exhibition info with a query!

Based on the search results found, a bar chart will be generated, showing the distribution (i.e., numbers) of relevant exhibition(s) at each of Tate's branch galleries; for each exhibition in the search results, the following information will be displayed:

1. the exhibition name
2. people names and other entities mentioned in the article
3. time period
4. location
5. a brief summary about the exhibition's content
6. a snapshot of an intro article
7. and by clicking to the "more info" button shown below each piece of search result, you can access Tate's website for that specific exhibition

The search engine has 4 different search modes. Search mode will be automatically selected based on the content of the query (and the activated search mode for an input query will be displayed). The search modes include the following:

1. Relevance Search with lemmatisation (the default mode)
2. Boolean Search WITHOUT lemmatisation (activated automatically if the query contains logic operator(s), including 'and', 'or', 'not', and brackets)\*
3. Wildcard + Relevance Search (activated automatically if the query contains "\*")
4. Wildcard + Boolean Search (activated automatically if the query contains "\*" + logic operator)

### NOTE: 
- To activate the Boolean Search mode, the logic operator in a query needs to be used in an acceptable way (e.g., a query such as "and cat" will be considered illegal, and the Boolean Search mode will not be activated. Instead, Relevance Search will take over in this case).
- On the other hand, if there is any word in the query that's not in the vocabulary, the Boolean Search mode will also not activate (e.g., a query like "sdfsd and cdcda").

## How to run the search engine:

Our search engine is not a public website; it can only run on a local device.
To run this search engine, one needs to set up and activate a virtual environment, and install <strong>Flask</strong>.
The following libraries are also need to be installed in the environment: <strong>scikit-learn, spacy, beautifulsoup</strong>.

### To set up

For Mac users:

```
python3 -m venv demoenv
. demoenv/bin/activate
pip install Flask
```

For Windows users:

```
py -3 -m venv demoenv
demoenv/Scripts/activate
pip install Flask
```

### Running the project

After everything has been set, let's start running the search engine!
Here is an example of how to run it:

The project directory is called "Final_Project", which is under the cloned repository "IKEA-meatballs-main":

```
git clone git@github.com:zccwqdoorchid/IKEA-meatballs.git
cd IKEA-meatballs-main\Final_Project
```

Then, set up the following environment variables and run Flask:

On Linux terminal

```
export FLASK_APP=combined_search.py
export FLASK_DEBUG=True
export FLASK_RUN_PORT=5000
flask run
```

On Windows command line:

```
set FLASK_APP=combined_search.py
set FLASK_DEMO=True
set FLASK_RUN_PORT=5000
flask run
```

On Windows PowerShell:

```
$env:FLASK_APP = "combined_search.py"
$env:FLASK_DEMO = "True"
$env:FLASK_RUN_PORT = "5000"
flask run
```

After that, open a browser and go to "http://127.0.0.1:5000". Now the search engine is at your disposal.

## Demo example:

If everything went well, the browser should display this home page:
![](demo/demo_home_page.png)

By clicking on the "start searching" button on the home page, it goes to the search page:
![](demo/demo_search.png)

And here is an example of search results displayed after inputting the query "Watercolour":

1. a bar chart that shows how many on-going/upcoming exhibitions related to "Watercolour" are at each of the branch galleries:
   ![](demo/demo_search_result_1-1.png)
2. and the information about each related exhibition:
   ![](demo/demo_search_result_1-2.png)
