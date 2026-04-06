import datetime

def log_request(client_address, method, path, host, headers):
    print("---- REQUEST ----")
    #client IP and port
    print(f"Client: {client_address[0]}:{client_address[1]}")
    #show HTTP request line
    print(f"{method} {path} HTTP/1.1")
    #host name
    print(f"Host: {host}")

    #mainly shows browser used
    if "User-Agent" in headers:
        print(f"User-Agent: {headers['User-Agent']}")

    #show request timestamp using datetime library
    print(f"Time: {datetime.datetime.now()}")
    print("-----------------")


def log_response():
    print("---- RESPONSE ----")
    #show response timestamp
    print(f"Time: {datetime.datetime.now()}")
    print("------------------")
