import threading 
import time

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
        self.store = {}

        # Shared lock is needed in case 2 threads try to write to the cache dict at the same time
        self.cache_lock = threading.Lock()

        # This limits the number of entries we can add to the cache
        self.max_size = 10

    def get(self, url):
        # Acquiring lock so someone else doesn't touch the dict at the same time
        with self.cache_lock:
            # Checks if the url is in the dict, if not then it returns None
            if url not in self.store:
                return None # miss occurs, not in the cache dict
            
            # Else it returns the data stored in cache
            entry = self.store[url]

            # Check expiration, if entry has been in cache for more than allowed, it gets deleted
            if ((time.time() - entry["timestamp"]) > CACHE_TIMEOUT):
                # If the entry is expired, simply delete it from cache
                del self.store[url]
                # Treat its expiration as a cache miss instead and return None
                return None

            return entry["data"]

    def set(self, url, response):
        # Acquires lock as well, and it sets a new key in the dictionary

        with self.cache_lock:
            # First we check if cache is not full
            if len(self.store) >= self.max_size:
                # If full, acquire the oldest entry and delete it from cache
                # lambda here acts as a nameless function called on the entries
                # item[1] is the entry value (response and timestamp)
                # the full function just gets the smallest timestamp (oldest entry)
                # This is technically the "least recently used" algorithm
                oldest = min(self.store.items(), key=lambda item: item[1]["timestamp"])
                # Delete this entry using its URL
                del self.store[oldest[0]]

            # key=URL(host+path) => {"data": response, "timestamp": added time in float}
            self.store[url] = {
                "data": response,
                "timestamp": time.time()
            }
