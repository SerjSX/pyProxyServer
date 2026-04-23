from functionalities.logger import write_log

class CacheStats:
    def __init__(self):
        self.TOTAL_HITS = 0
        self.TOTAL_MISSES = 0
        self.HIT_TIME = 0.0
        self.MISS_TIME = 0.0

    def record_hit(self, duration):
        self.TOTAL_HITS += 1
        self.HIT_TIME += duration

    def record_miss(self, duration):
        self.TOTAL_MISSES += 1
        self.MISS_TIME += duration

    def avg_hit_time(self):
        return self.HIT_TIME / self.TOTAL_HITS if self.TOTAL_HITS else 0.0

    def avg_miss_time(self):
        return self.MISS_TIME / self.TOTAL_MISSES if self.TOTAL_MISSES else 0.0

    def hit_over_miss_time(self):
        hit_avg = self.avg_hit_time()
        miss_avg = self.avg_miss_time()
        return miss_avg / hit_avg if hit_avg else float('inf')

    def log_summary(self):
        write_log("---- Performance Summary ----")
        write_log(f"Total Requests: {self.TOTAL_HITS + self.TOTAL_MISSES}")
        write_log(f"Total Hits: {self.TOTAL_HITS}")
        write_log(f"Total Misses: {self.TOTAL_MISSES}\n")
        write_log(f"Average Miss Time: {self.avg_miss_time():.4f} ms")
        write_log(f"Average Hit Time: {self.avg_hit_time():.4f} ms\n")
        write_log(f"Speedup Factor: ~{self.hit_over_miss_time():.2f}x\n\n")