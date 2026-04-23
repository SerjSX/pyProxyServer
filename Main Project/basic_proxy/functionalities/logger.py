import datetime
import time
import os
import threading

LOG_FILE = None
log_lock = threading.Lock()

# External file logging method
def init_logger():
    global LOG_FILE

    # Creates a logs directory in our project directory if non-existent
    if not os.path.exists("logs"):
        os.makedirs("logs")

    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # Uniquely adding timestamp to file name to later easily identify it
    LOG_FILE = f"logs/proxy_{timestamp}.txt"

# This method unifies console and external file printing
def write_log(message):
    global LOG_FILE
    message = str(message)

    # This lock prevents logging from multiple threads at once
    # This is to prevent messy logs
    with log_lock:
        print(message, flush=True) #prints in the console

        if LOG_FILE:
            try:
                # This writes to the external text file
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(message+ "\n")
            except Exception as e:
                print("Logging failed:", e)

def log_request(method, path, host, headers):
    write_log("---- REQUEST ----")
    #show HTTP request line
    write_log(f"{method} {path} HTTP/1.1")
    #host name
    write_log(f"Host: {host}")

    #mainly shows browser used
    if "User-Agent" in headers:
        write_log(f"User-Agent: {headers['User-Agent']}")

    #show request timestamp using datetime library
    write_log(f"Time: {datetime.datetime.now()}")
    write_log("-----------------\n")


def log_response(status_code, status, size):
    write_log(f"\n---- RESPONSE ----")
    write_log(f"Status: {status_code} {status}")
    write_log(f"Size: {size} bytes")
    #show response timestamp
    write_log(f"Time: {datetime.datetime.now()}")
    write_log("------------------\n")

# Logs that a CONNECT request was received.
def log_connect_request(client_address, host, port):
    write_log(f"\n[{datetime.datetime.now()}] CONNECT HTTPS request received from client {client_address[0]}:{client_address[1]} to: {host}:{port}")

def log_request_received(client_address, host):
    # Log that the request was successfully received with a timestamp
    write_log(f"\n[{datetime.datetime.now()}] Request received from client {client_address[0]}:{client_address[1]} to host: {host}\n")

def log_rejected_method(method):
    # If method is different from GET
    write_log(f"Rejected method: {method}")

def log_request_forwarded(host):
    # Log that we are now sending request to external URL with timestamp
    write_log(f"[{datetime.datetime.now()}] Request forwarded to {host}")

def log_response_received(current_size):
    # Log that response successfully received from external URL with timestamp
    write_log(f"[{datetime.datetime.now()}] Response received from server; current size = {current_size}B")

def log_response_sent_back():
    # Log that we successfully sent response back to client with timestamp
    write_log(f"[{datetime.datetime.now()}] Response sent to client")

def log_connect_browser_established(host, port):
    write_log(f"[{datetime.datetime.now()}] Connection established with {host}:{port}; tunnel is ready.")

def log_connect_tunnel_closed(host, port):
    write_log(f"\n[{datetime.datetime.now()}] Tunnel closed for: {host}:{port}")

def log_blocked_host():
    write_log(f"[{datetime.datetime.now()}] Blocked the request attempt since it's blacklisted.")

def log_blocked_address(client_ip):
    write_log(f"[{datetime.datetime.now()}] Blocked the client from requesting anything since their address is blacklisted: {client_ip}")

def log_blocked_port(port):
    write_log(f"[{datetime.datetime.now()}] Blocked the request attempt to port {port} since it's blacklisted.")

def log_cache_hit(url):
    write_log(f"[{datetime.datetime.now()}] Cache HIT: {url}")

def log_cache_miss(url):
    write_log(f"[{datetime.datetime.now()}] Cache MISS: {url}")

def log_cache_lru(url):
    write_log(f"[{datetime.datetime.now()}] Cache full, least used entry removed from cache: {url}")

def log_cache_expired(url):
    write_log(f"[{datetime.datetime.now()}] Entry expired, removing: {url}")