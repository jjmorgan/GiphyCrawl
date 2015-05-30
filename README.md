# GiphyCrawl

A simple "crawler" for downloading popular GIF files from Giphy.com. The crawler explores categories from Giphy and uses the public Giphy API to download GIFs from the most common tags associated with each category. The script also stores tags associated with each GIF in a text file.

--

Usage:

$ python giphycrawl.py

GIFs are downloaded to the ./crawl directory. Folders 0 - 23 represent each category retrieved. The final tag list is stored in ./crawl/taglist.txt.

--

Also included is a deprecated script (randomgiphy.py) that uses the random endpoint API call. The function is prone to returning duplicate images and is mostly unreliable at the moment.

GiphyCrawl was used to create a source database for evaluating an extension to the FIRE CBIR system that searches on animated images.
[github.com/jjmorgan/fire-cbir](http://github.com/jjmorgan/fire-cbir)
