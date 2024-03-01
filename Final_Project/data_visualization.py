# functions that generates graphs
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib
matplotlib.use('agg')


# +
''' - read from a list, generate a horizontal bar chart 
    - chart content: frequencies (x axis) - list of gallery locations (y axis)
'''
def bar_generator(exhib_locations, match_locations, query):
    
    # count list of item & their frequencies
    loc2freq = {}
    for loc in exhib_locations:
        loc2freq[loc] = 0

    loc2freq_new = Counter(match_locations)
    loc2freq.update(loc2freq_new)

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
            x + 0.02,      # x axis of lable's position
            y - 0.1,      # y axis of lable's position
            str(x), 
            color = (0.2, 0.4, 0.2, 0.6), 
            fontsize = 15
        )
        
    #  x axis title
    ax.set_xlabel("number of exhibitions", fontsize = 15)
    
#     plt.show()
    plt.savefig(f'static/query_{query}_plot.png',bbox_inches='tight')    

# +
# # ------------ uncomment this block only for for debugging / testing -----------------

# from web_scraping import extract_gallery_info   

# gallery_2_url = {'Tate':'https://www.tate.org.uk/whats-on'} 
# exhib_titles, exhib_dates, exhib_locations, exhib_intro, exhib_articles, exhib_urls = extract_gallery_info(gallery_2_url)

# +
# bar_generator(exhib_locations,exhib_locations[:4],"Current Exhibitions and Locations")
# -------------------------------------------------------------------------------------
