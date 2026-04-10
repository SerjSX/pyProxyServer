import threading 
import time

"""
Class used to store the cached values in a dictionary.
    def get(self, url): 
        Gets the response data from the cached dict, if it's stored, else returns None
    def set(self, url, response): 
        Sets a new response data to the cache dict with the key being the url and the value being an inner dict containing the response data and the timestamp
"""
class ProxyCache:
    def __init__(self):
        # Stores cache as: url => {"data": bytes, "timestamp": float}
        self.store = {}

        # Shared lock is needed in case 2 threads try to write to the cache dict at the same time
        self.cache_lock = threading.Lock()

    def get(self, url):
        # Acquiring lock so someone else doesn't touch the dict at the same time
        with self.cache_lock:
            # Checks if the url is in the dict, if not then it returns None
            if url not in self.store:
                return None # miss occurs, not in the cache dict
            
            # Else it returns the data stored in cache
            entry = self.store[url]
            return entry["data"]

    def set(self, url, response):
        # Acquires lock as well, and it sets a new key in the dictionary with the values:
        # key=URL(host+path) => {"data": response, "timestamp": added time in float}
        with self.cache_lock:
            self.store[url] = {"data": response, "timestamp": time.time()}
