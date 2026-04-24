import datetime
import os
import re
import threading
from colorama import init, Fore, Style # type: ignore

# enabling ANSI codes on windows
init(autoreset=True) # autoreset-True means each color resets automatically after use

# Matches ANSI escape sequences so file logs stay plain text.
ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

reset_effects = Fore.RESET + Style.RESET_ALL

COLORS = {
    'time': Fore.WHITE + Style.DIM,
    'header': Fore.MAGENTA + Style.BRIGHT,
    'ip': reset_effects + Fore.CYAN,
    'GET': Fore.GREEN,
    'CONNECT': Fore.YELLOW,
    'HIT': reset_effects + Fore.GREEN + Style.BRIGHT,
    'MISS': reset_effects + Fore.RED,
    'SECONDARY_MISS': reset_effects + Fore.RED + Style.BRIGHT,
    'BLOCK': reset_effects + Fore.RED + Style.BRIGHT,
    'TUNNEL': reset_effects + Fore.YELLOW + Style.BRIGHT,
    'ERROR': reset_effects + Fore.RED + Style.BRIGHT,
    'BYTES': reset_effects + Fore.BLUE,
    'target_url': Fore.WHITE,
    'path': Fore.LIGHTBLACK_EX,
    'status': Fore.LIGHTCYAN_EX,
}

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

    # Clean the message from the characters that colorama adds when printing. 
    plain_message = ANSI_ESCAPE_RE.sub("", message)

    # This lock prevents logging from multiple threads at once
    # This is to prevent messy logs
    with log_lock:
        print(message, flush=True) #prints in the console

        if LOG_FILE:
            try:
                # This writes to the external text file
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(plain_message + "\n")
            except Exception as e:
                print("Logging failed:", e)


def log_request(client_address, method, host, port, headers, path=None):
    method_color = COLORS.get(method, Fore.WHITE)

    write_log(f"\n{COLORS['header']}------ REQUEST ------")
    write_log(f"{COLORS['time']}Time: {datetime.datetime.now()}")
    write_log(f"{COLORS['ip']}Client: {client_address[0]}:{client_address[1]}")
    write_log(f"{method_color}Method: {method}")
    write_log(f"{COLORS['target_url']}Target: {host}:{port}")

    if path:
        write_log(f"{COLORS['path']}Path: {path}")
    if "User-Agent" in headers:
        write_log(f"User-Agent: {headers['User-Agent']}")

    write_log(f"{COLORS['header']}---------------------\n")

def log_response(status_code, status, size):
    write_log(f"\n{COLORS['header']}---- RESPONSE ----")
    write_log(f"{COLORS['status']}Status: {status_code} {status}")
    write_log(f"{COLORS['BYTES']}Size: {size} bytes")
    #show response timestamp
    write_log(f"{COLORS['time']}Time: {datetime.datetime.now()}")
    write_log(f"{COLORS['header']}------------------\n")

def log_rejected_method(method):
    # If method is different from GET
    write_log(f"Rejected method: {method}")

def log_request_forwarded(host):
    # Log that we are now sending request to external URL with timestamp
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['SECONDARY_MISS']}Request forwarded to {host}")

def log_response_received(host, current_size):
    # Log that response successfully received from external URL with timestamp
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['SECONDARY_MISS']}Response received from server {host}; {COLORS['BYTES']}current size = {current_size}B")

def log_response_sent_back(host, port, client_address):
    # Log that we successfully sent response back to client with timestamp
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['SECONDARY_MISS']}Response from {host}:{port} sent to this client: {COLORS['ip']}{client_address[0]}:{client_address[1]}")

def log_connect_browser_established(host, port):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['TUNNEL']}Connection established with {host}:{port}; tunnel is ready.")

def log_connect_tunnel_closed(host, port):
    write_log(f"\n{COLORS['time']}[{datetime.datetime.now()}] {COLORS['TUNNEL']}Tunnel closed for: {host}:{port}")

def log_blocked_host(host):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['BLOCK']}Blocked the request attempt to {host} since it's blacklisted.")

def log_blocked_address(client_ip):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['BLOCK']}Blocked the client from requesting anything since their address is blacklisted: {COLORS['ip']}{client_ip}")

def log_blocked_port(port):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['BLOCK']}Blocked the request attempt to port {port} since it's blacklisted.")

def log_cache_hit(url):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['HIT']}Cache HIT: {url}")

def log_cache_miss(url):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] {COLORS['MISS']}Cache MISS: {url}")

def log_cache_lru(url):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] Cache full, least used entry removed from cache: {url}")

def log_cache_expired(url):
    write_log(f"{COLORS['time']}[{datetime.datetime.now()}] Entry expired, removing: {url}")

