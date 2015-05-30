''' Random Giphy -- Obtain a random GIF from Giphy
This is incredibly prone to duplicate results, so it's not ideal
'''

from optparse import OptionParser
import json
import urllib2
import time
import threading
import os.path

parser = OptionParser()
parser.add_option("-c", "--count", dest="count", help="Number of random images to retrieve from Giphy (per thread)", type="int", default=10)
parser.add_option("-t", "--threads", dest="threads", help="Number of worker threads", type="int", default=1)
options, args = parser.parse_args()

def get_images(threadid, count, image_counts):
  i = 0
  while i < count:
    response = urllib2.urlopen('http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC').read()
    result = json.loads(response)
    
    url = result["data"]["image_url"]
    name = url.split('/')[5]
    
    path = "downloaded\\" + name + ".gif"
    if os.path.isfile(path):
      print '[' + str(threadid) + '] Duplicate:', name
      
    else:
      image = urllib2.urlopen(url).read()
      fout = open(path, 'wb+')
      fout.write(image)
      fout.close()
      
      image_counts[threadid] += 1
      i += 1
      
      print '[' + str(threadid) + '] Downloaded:', name

threads = []
image_counts = [0] * options.threads
for i in range(options.threads):
  t = threading.Thread(target=get_images, args=(i,options.count,image_counts))
  threads.append(t)
  t.start()

for t in threads:
 t.join()
  
print 'Finished downloading', sum(image_counts), 'gifs.'
