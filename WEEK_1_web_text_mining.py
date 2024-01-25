from bs4 import BeautifulSoup
import requests

url = "https://www.bbcgoodfood.com/recipes/collection/pie-recipes"

result = requests.get(url)

soup = BeautifulSoup(result.text, "html.parser")

result = soup.find("p").text

print(result)
