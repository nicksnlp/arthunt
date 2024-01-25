from bs4 import BeautifulSoup
import requests

# retreat pie info from BBC goodfood
url = "https://www.bbcgoodfood.com/recipes/collection/pie-recipes"
result = requests.get(url)
soup = BeautifulSoup(result.text, 'html')

# EXTRACT PAGE INTRO
intro = soup.find("p").text

#EXTRACT PIE NAMES (the first 10 of them)
all_pie_names = soup.find_all('h2', class_ = 'heading-4')
ten_pies = [pie.text for pie in all_pie_names[0:10]]

#EXTRACT CORRESPONDING PIE DESCRIPTIONS
pie_descriptions = soup.find_all('p', class_ = 'card__description d-block body-copy-small')
ten_descriptions = [des.text for des in pie_descriptions[0:10]]

#print everything:
print("# From a BBC good food webpage, we extracted a general introduction quote and information for 10 pies on that page :)\n")

print("Webpage Intro:")
print(intro+"\n")

for idx in range(10):
    name = ten_pies[idx]
    desc = ten_descriptions[idx]
    print("Pie #",idx+1,"- "+name)
    print(desc+".\n")
