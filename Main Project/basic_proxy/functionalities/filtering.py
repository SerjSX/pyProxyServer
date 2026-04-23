from pathlib import Path
import threading

BASE_DIR = Path(__file__).resolve().parent
BLACKLIST_DIR = BASE_DIR / "blacklists"

HOSTS_FILE = BLACKLIST_DIR / "hosts.txt"
ADDRESSES_FILE = BLACKLIST_DIR / "addresses.txt"
PORTS_FILE = BLACKLIST_DIR / "ports.txt"

# Thread lock used to avoid unsafe file checks
LOCK = threading.Lock()

# Caches + last modified times
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


# Hosts section
def load_hosts():
    # Adds each line from the file into the set (sets don't include duplicates)
    return {line.lower() for line in read_lines(HOSTS_FILE)}


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


def is_host_blocked(host):
    if not host:
        return False
    return host.lower() in get_hosts_blacklist()


def is_address_blocked(address):
    return address in get_addresses_blacklist()


def is_port_blocked(port):
    return port in get_ports_blacklist()