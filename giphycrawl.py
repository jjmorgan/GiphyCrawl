''' Giphy Crawl -- Obtain GIFs from the Categories page

Author:
Justin Morgan
jjmorgan@ucla.edu

Repository:
github.com/jjmorgan/GiphyCrawl

Obtains gifs from the most popular tags in the Giphy database
- Crawling is used to obtain the categories and tags
- Giphy API is used to get the images
- Does not guarantee that images across categories are unique

'''
import urllib2
import os.path
import json
import threading
import time

from sys import stdout
from sys import exit

MAX_DL_PER_TAG = 10
MAX_THREADS = 6

PUBLIC_BETA_KEY = "dc6zaTOxFJmzC"

USER_AGENT = "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0"

''' Thread-safe print to console '''
def thread_print(str, print_lock):
  print_lock.acquire()
  try:
    print str
  finally:
    print_lock.release()

''' Get images from tags in a category '''
def crawl_category(tid, cid, category, tag_list_array, print_lock):
  tid_str = "[" + str(tid) + "]"
  
  dir = "crawl\\" + str(cid)
  if not os.path.exists(dir):
    os.mkdir(dir)

  thread_print(tid_str + " Begin retrieving images for " + category +  " (" + str(cid) + ")", print_lock)
  
  tags = get_tags(category)
  for t in tags:
    thread_print(tid_str + " Searching by tag: " + t, print_lock)
    urls = get_urls_by_tag(t)
    
    for n, u, p in urls:
      download_image(n, u, dir)
      tag_list_array.append(get_tags_for_image(n, p))
      #thread_print(tid_str + " Downloaded: " + name, print_lock)

''' Save an image to the crawl directory '''
def download_image(name, url, todir):
  path = os.path.join(todir, name)
  if not os.path.exists(path):
    with open(path, 'wb+') as fout:
      response = urllib2.urlopen(url).read()
      fout.write(response)
  
''' Retrieve URLs to the original image and containing page '''
def get_urls_by_tag(tag):
  urls = []
  
  t = tag.replace(' ', '+')
  limit = str(MAX_DL_PER_TAG)
  try:
    # api.giphy.com checks the User-Agent of the request object to ensure it's a valid browser
    request = urllib2.Request("http://api.giphy.com/v1/gifs/search?q=" + t + "&limit=" + limit + "&api_key=" + PUBLIC_BETA_KEY)
    request.add_header("User-Agent", USER_AGENT)
    response = urllib2.urlopen(request).read()
  except urllib2.HTTPError, e:
    with open("httperror.html", "w+") as f:
      f.write(e.fp.read())
    print "*** API call failed!"
    return [], []
  result = json.loads(response)
  
  images = result["data"]
  for g in images:
    # (name, originalurl, pageurl)
    urls.append( (g["id"] + ".gif", g["images"]["original"]["url"], g["url"]) )
  
  return urls
  
''' Get the most popular tags associated with a category '''
def get_tags(category):
  tags = []
  
  response = urllib2.urlopen("http://giphy.com/categories/" + category).read()
  
  # Tags are defined by the element:
  # <a href="/search/<TAG>/">#<TAG></a>
  
  i = 0
  while True:
    start = response.find("/\">#", i)
    if start == -1:
      break
    end = response.find("<", start)
    tag = response[start+4:end]
    tags.append(tag)
    i = start + 1
    
  return tags
  
''' Get category names from the categories page '''
def get_categories():
  categories = []
  
  response = urllib2.urlopen("http://giphy.com/categories").read()
  
  # Categories are defined by the element:
  # <a href="/categories/<CATEGORY>" class="tag">
  
  i = 0
  while True:
    end = response.find("class=\"tag\"", i)
    if end == -1:
      break
    start = response.rfind("/", i, end)
    category = response[start+1:end-2]
    categories.append(category)
    i = end + 1
  
  return categories
  
''' Get the user tags / keywords associated with a single image '''
def get_tags_for_image(name, url):
  # Tags associated with an image are not given in the JSON response
  # Only way to get them is to visit the image's page itself
  
  response = urllib2.urlopen(url).read()
  
  # Tags for an image are defined by the element:
  # <meta name="keywords" content="tag, tag, tag, tag, ..., tag, GIF, Animated GIF">
  # The last two tags are always "GIF, Animated GIF", so we leave these out
  end = response.find(", GIF, Animated GIF\">")
  start = response.rfind("\"", 0, end)
  tags = response[start+1:end]
  print (name, tags)
  return (name, tags)
  
''' Main routine -- Launches threads to crawl Giphy categories '''
def main():
  if not os.path.exists("crawl"):
    os.mkdir("crawl")
    
  categories = get_categories()
  print "Starting crawl for", len(categories), "categories..."
    
  # assign each thread a single category to crawl
  print_lock = threading.Lock()
  threads = []
  tag_list_array = []
  c_index = 0
  for i in range(min(MAX_THREADS, len(categories))):
    t = threading.Thread(target=crawl_category, args=(i, c_index, categories[c_index], tag_list_array, print_lock))
    threads.append((t, i))
    t.start()
    c_index += 1
    
  # wait for threads to finish, and create new threads for remaining categories
  while len(threads) > 0:
    finished_threads = []
    for t, tid in threads:
      if not t.isAlive():
        finished_threads.append((t, tid))
        
    for f, tid in finished_threads:
      f.join()
      threads.remove((f, tid))
      
      if c_index < len(categories):
        t = threading.Thread(target=crawl_category, args=(tid, c_index, categories[c_index], tag_list_array, print_lock))
        threads.append((t, tid))
        t.start()
        c_index += 1
    
  with open("crawl\\taglist.txt", "w+") as tagf:
    for n, t in tag_list_array:
      tagf.write(n + '\t' + t + '\n')
    
  print "Done."
  
''' Main entry point '''
if __name__ == '__main__':
  main()
