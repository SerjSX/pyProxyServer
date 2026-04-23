import threading 
import time
from collections import OrderedDict
from functionalities.logger import log_cache_miss, log_cache_hit, log_cache_lru, log_cache_expired

"""
Class used to store the cached values in a dictionary.
    def get(self, url): 
        Gets the response data from the cached dict, if it's stored, else returns None
    def set(self, url, response): 
        Sets a new response data to the cache dict with the key being the url and the value being an inner dict containing the response data and the timestamp
"""

# 60 seconds to remove cached objects
CACHE_TIMEOUT = 60

class ProxyCache:
    def __init__(self):
        # Stores cache as: url => {"data": bytes, "timestamp": float}
        # Using OrderedDict in order to implement LRU algorithm (acts as a queue)
        self.store = OrderedDict()

        # Shared lock is needed in case 2 threads try to write to the cache dict at the same time
        self.cache_lock = threading.Lock()

        # This limits the number of entries we can add to the cache
        self.max_size = 10

    def get(self, url):
        # Acquiring lock so someone else doesn't touch the dict at the same time
        with self.cache_lock:
            # Checks if the url is in the dict, if not then it returns None
            if url not in self.store:
                log_cache_miss(url)
                return None # miss occurs, not in the cache dict

            # Else it returns the data and timestamp stored in cache
            entry = self.store[url]
            data = entry["data"]
            timestamp = entry["timestamp"]
            
            # Check expiration, if entry has been in cache for more than allowed, it gets deleted
            if (time.time() - timestamp) > CACHE_TIMEOUT:
                log_cache_expired(url)
                # If the entry is expired, simply delete it from cache
                del self.store[url]
                # Treat its expiration as a cache miss instead and return None
                return None

            log_cache_hit(url)

            # Move to end of cache, make as most recently used
            self.store.move_to_end(url)

            return data

    def set(self, url, response):
        # Acquires lock as well, and it sets a new key in the dictionary

        with self.cache_lock:
            # First, if it already exists we remove it to insert at the end
            if url in self.store:
                del self.store[url]

            # Then we check if cache is not full
            elif len(self.store) >= self.max_size:
                # If full, pop/delete the oldest entry (first in dict, oldest) from cache and keep track of old url
                old_url, _ = self.store.popitem(last=False)
                log_cache_miss(old_url)

            # Insert new entry as most recently used (last in dict)
            # key=URL(host+path) => {"data": response, "timestamp": added time in float}
            self.store[url] = {
                "data": response,
                "timestamp": time.time()
            }
