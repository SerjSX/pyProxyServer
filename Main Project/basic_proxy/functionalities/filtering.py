from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BLACKLIST_DIR = BASE_DIR / "blacklists"

HOSTS_FILE = BLACKLIST_DIR / "hosts.txt"
ADDRESSES_FILE = BLACKLIST_DIR / "addresses.txt"
PORTS_FILE = BLACKLIST_DIR / "ports.txt"

# Reading a blacklist file with ignoring comments and empty lines
def _read_non_comment_lines(file_path):
    lines = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                lines.append(line)
    except FileNotFoundError:
        pass #possible empty blacklist
    
    return lines

# Loading hosts lowercased and returning
def _load_hosts():
    return {line.lower() for line in _read_non_comment_lines(HOSTS_FILE)}

# Loading client IPs and returning
def _load_addresses():
    return set(_read_non_comment_lines(ADDRESSES_FILE))

# Loading the ports from the file
def _load_ports():
    ports = set()

    for line in _read_non_comment_lines(PORTS_FILE):
        try: 
            port = int(line)
            if 1 <= port <= 65535:
                ports.add(port)
        except ValueError:
            # ignore
            pass

    return ports

# Storing them in variables to be used in the coming check methods.
HOSTS_BLACKLIST = _load_hosts()
ADDRESS_BLACKLIST = _load_addresses()
PORT_BLACKLIST = _load_ports()

def is_host_blocked(host):
    if not host:
        return False
    
    return host.lower() in HOSTS_BLACKLIST

def is_address_blocked(address):
    return address in ADDRESS_BLACKLIST

def is_port_blocked(port):
    return port in PORT_BLACKLIST