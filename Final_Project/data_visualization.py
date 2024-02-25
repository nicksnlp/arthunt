# functions that generates graphs
import matplotlib.pyplot as plt
import seaborn as sns 
from collections import Counter 

''' - read from a list, generate a horizontal bar chart 
    - chart content: frequencies (x axis) - list of gallery locations (y axis)
    - the input 'title' is a string, the name of the bar chart (e.g., 'Current Exhibitions and Locations')
'''
def bar_generator(item_list, title):
    
    # count list of item & their frequencies
    loc2freq = Counter(item_list)
    loc2freq = dict(sorted(loc2freq.items(), key=lambda x:x[1]))
    locs = list(loc2freq.keys())
    freqs = list(loc2freq.values())

    # draw the chart
    fig, ax = plt.subplots(figsize=(10, 8)) 
    
    ax.barh(
        locs,
        freqs,
        color = (0.2, 0.4, 0.2, 0.6),
    )
    plt.rc('font', size=15) 
    
    # lable freq numbers for each bar
    for y, x in enumerate(freqs):
        ax.text(
            x + 0.3,      # x axis of lable's position
            y - 0.1,      # y axis of lable's position
            str(x), 
            color = (0.2, 0.4, 0.2, 0.6), 
            fontsize = 15
        )
        
    # chart title
    ax.set_title(title, fontsize = 20)
    
    plt.show()    

# +
# ------------ uncomment this block only for for debugging / testing -----------------

# from web_scraping_Copy1 import extract_gallery_info   

# gallery_2_url = {'Tate':'https://www.tate.org.uk/whats-on'} 
# exhib_titles, exhib_dates, exhib_locations, exhib_intro, exhib_articles, exhib_urls = extract_gallery_info(gallery_2_url)

# +
# bar_generator(exhib_locations,"Current Exhibitions and Locations")

# -------------------------------------------------------------------------------------
