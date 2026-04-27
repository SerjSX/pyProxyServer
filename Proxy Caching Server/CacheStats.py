from functionalities.logger import write_log
from colorama import init, Fore, Style # type: ignore

"""
Class used to store statistics about the HTTP requests:
    - The total misses and hits are counted and stored.
    - The total hit and miss time are summed and stored.
    - The average hit and miss time can be calculated through the provided methods: avg_hit_time() and avg_miss_time()
    - The hit over miss time speed factor can be calculated and returned through the provided method: hit_over_miss_time()
    - The entire information mentioned above can be logged through the method: log_summary()
    
"""

class CacheStats:
    def __init__(self):
        # Initializing variables to store the hits, misses, and times for each.
        self.TOTAL_HITS = 0
        self.TOTAL_MISSES = 0
        self.HIT_TIME = 0.0
        self.MISS_TIME = 0.0

    # Recording a hit and its duration
    def record_hit(self, duration):
        self.TOTAL_HITS += 1
        self.HIT_TIME += duration

    # Recording a miss and its duration
    def record_miss(self, duration):
        self.TOTAL_MISSES += 1
        self.MISS_TIME += duration

    # Calculating and returning the average hit time 
    def avg_hit_time(self):
        return self.HIT_TIME / self.TOTAL_HITS if self.TOTAL_HITS else 0.0

    # Calculating and returning the average miss time
    def avg_miss_time(self):
        return self.MISS_TIME / self.TOTAL_MISSES if self.TOTAL_MISSES else 0.0

    # Calculating and returning the hit over miss speed factor
    def hit_over_miss_time(self):
        hit_avg = self.avg_hit_time()
        miss_avg = self.avg_miss_time()
        return f"{miss_avg / hit_avg}x" if hit_avg else "No hits recorded"

    # Logs an entire summary for the above metrics claculated: total requests, hits, misses, average miss/hit time, and speed factor.
    def log_summary(self):
        write_log(f"{Fore.CYAN + Style.BRIGHT}---- Performance Summary ----")
        write_log(f"{Fore.MAGENTA}Total Requests: {self.TOTAL_HITS + self.TOTAL_MISSES}")
        write_log(f"{Fore.GREEN}Total Hits: {self.TOTAL_HITS}")
        write_log(f"{Fore.RED}Total Misses: {self.TOTAL_MISSES}\n")
        write_log(f"{Fore.RED + Style.BRIGHT}Average Miss Time: {self.avg_miss_time():.4f} ms")
        write_log(f"{Fore.GREEN + Style.BRIGHT}Average Hit Time: {self.avg_hit_time():.4f} ms\n")
        write_log(f"{Fore.MAGENTA + Style.BRIGHT}Speedup Factor: ~{self.hit_over_miss_time()}")
        write_log(f"{Fore.CYAN + Style.BRIGHT}-----------------------------\n")

