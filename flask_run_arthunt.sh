#! /bin/zsh

# script: flask_run_arthunt.sh
# author: Nikolay Vorontsov (April 2024)
# script to run final project in Building NLP apps course 2024 

# path_to_your_environment
. demoenv/bin/activate
# path to the project repository
cd nicksnlp/arthunt/ 
 
export FLASK_APP=flask_app.py  
export FLASK_DEBUG=True  
export FLASK_RUN_PORT=8000

flask run
