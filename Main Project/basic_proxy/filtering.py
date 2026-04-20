# Hosts blocked.
HOSTS_BLACKLIST = {
    # "example.com"
}

# IP addresses blocked.
ADDRESS_BLACKLIST = {
    #"127.0.0.1"
}

def is_host_blocked(host):
    return host in HOSTS_BLACKLIST

def is_address_blocked(address):
    return address in ADDRESS_BLACKLIST
