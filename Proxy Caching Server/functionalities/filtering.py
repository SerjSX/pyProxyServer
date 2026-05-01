from pathlib import Path
import threading

"""
This module is responsible for loading blacklists of hosts, addresses, and ports. Also provides helper methods to know if
a host/address/port is blacklisted or no.

It also is responsible for loading the blacklisted text files if they are modified as the server is running; so no need to restart
the server.
"""

# Initializing the base directory to have a proper file path for storing the blacklist text files.
BASE_DIR = Path(__file__).resolve().parent
BLACKLIST_DIR = BASE_DIR / "blacklists"

HOSTS_FILE = BLACKLIST_DIR / "hosts.txt"
ADDRESSES_FILE = BLACKLIST_DIR / "addresses.txt"
PORTS_FILE = BLACKLIST_DIR / "ports.txt"

# Thread lock used to avoid unsafe file checks
LOCK = threading.Lock()

# Caches + last modified times to track if a blacklist text file has been updated or not compared to the
# last modified date added when trying to check if a host/port/clientIP is blacklisted or no.
HOSTS_CACHE = set()
HOSTS_LAST_MODIFIED = 0

ADDRESSES_CACHE = set()
ADDRESSES_LAST_MODIFIED = 0

PORTS_CACHE = set()
PORTS_LAST_MODIFIED = 0


# Reading a blacklist file while ignoring comments and empty lines
def read_lines(file_path):
    lines = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                # strip() removes leading and trailing whitespaces
                line = raw_line.strip()
                # Ignore line if empty or a comment
                if not line or line.startswith("#"):
                    continue
                # Add lines to list of lines
                lines.append(line)
    except FileNotFoundError:
        pass  # do nothing if file doesn't exist / empty blacklist

    return lines


# Loads the hosts blacklist from the file
def load_hosts():
    # Adds each line from the file into the set (sets don't include duplicates)
    # Also normalize by removing www. prefix for consistent matching
    return {line.lower().replace("www.", "", 1) for line in read_lines(HOSTS_FILE)}

# gets the hosts blacklisted and updates if the file has been modified after the last modified stored timestamp
def get_hosts_blacklist():
    global HOSTS_CACHE, HOSTS_LAST_MODIFIED

    try:
        # built-in stat library can calculate a file's last modified time
        last_modified = HOSTS_FILE.stat().st_mtime
    except FileNotFoundError:
        last_modified = 0 # in case file is not found

    # Check if the host's last modified time matches the updated time and update it accordingly
    if last_modified != HOSTS_LAST_MODIFIED:
        with LOCK:
            try:
                new_last_modified = HOSTS_FILE.stat().st_mtime
            except FileNotFoundError:
                new_last_modified = 0

            # If a new modification occurred, load the new contents of the file and update file's last modified
            if new_last_modified != HOSTS_LAST_MODIFIED:
                HOSTS_CACHE = load_hosts()
                HOSTS_LAST_MODIFIED = new_last_modified

    return HOSTS_CACHE


# Addresses section (same logic as hosts section)
def load_addresses():
    return set(read_lines(ADDRESSES_FILE))


def get_addresses_blacklist():
    global ADDRESSES_CACHE, ADDRESSES_LAST_MODIFIED

    try:
        last_modified = ADDRESSES_FILE.stat().st_mtime
    except FileNotFoundError:
        last_modified = 0

    if last_modified != ADDRESSES_LAST_MODIFIED:
        with LOCK:
            try:
                new_last_modified = ADDRESSES_FILE.stat().st_mtime
            except FileNotFoundError:
                new_last_modified = 0

            if new_last_modified != ADDRESSES_LAST_MODIFIED:
                ADDRESSES_CACHE = load_addresses()
                ADDRESSES_LAST_MODIFIED = new_last_modified

    return ADDRESSES_CACHE


# Ports Section
def load_ports():
    ports = set()

    for line in read_lines(PORTS_FILE):
        try:
            port = int(line)
            if 1 <= port <= 65535:
                ports.add(port)
        except ValueError:
            pass  # ignore invalid entries

    return ports

# same logic as hosts section
def get_ports_blacklist():
    global PORTS_CACHE, PORTS_LAST_MODIFIED

    try:
        last_modified = PORTS_FILE.stat().st_mtime
    except FileNotFoundError:
        last_modified = 0

    if last_modified != PORTS_LAST_MODIFIED:
        with LOCK:
            try:
                new_last_modified = PORTS_FILE.stat().st_mtime
            except FileNotFoundError:
                new_last_modified = 0

            if new_last_modified != PORTS_LAST_MODIFIED:
                PORTS_CACHE = load_ports()
                PORTS_LAST_MODIFIED = new_last_modified

    return PORTS_CACHE


# The below three methods are used by proxy.py to check if a host/address/port is blacklisted or no.
# Anything above is used by these below methods as helpers.
def is_host_blocked(host):
    if not host:
        return False
    # To ensure all cases are blocked.
    normalized_host = host.lower().replace("www.", "", 1)
    return normalized_host in get_hosts_blacklist()


def is_address_blocked(address):
    return address in get_addresses_blacklist()


def is_port_blocked(port):
    return port in get_ports_blacklist()