This dir contains code and scripts for visualizing the histwords embeddings. 

# png images

the scripts/ dir has files for generating .png graphics. running `python
scripts/closest_over_time_with_anns.py awful` will generate a file in viz/output/

NOTE: if you are using Mac OS, try out 'pythonw' if python does not work for you

# web explorer

the web dir contains a self contained web server for interactive exploration of
the histwords embeddings. run with `python viz/web/main.py` and then open
http://localhost:5000 and enter a search term.

## multi word exploration

to search for multiple terms at once, separate them with a colon, like:
"awful:terrible". when multiple search terms are used, their results are color
coded based on which search terms the result has shown up for. make sure to
hover over a word to see which search term that word is relevant to.

if you put in a lot of words, prepare to wait a long time! generally, it takes
me 5+ seconds to do 2 or 3 words at once.
