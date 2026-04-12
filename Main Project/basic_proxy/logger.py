import datetime
import time

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
    print("-----------------\n")


def log_response(status_code, status, size):
    print("\n---- RESPONSE ----")
    print(f"Status: {status_code} {status}")
    print(f"Size: {size} bytes")
    #show response timestamp
    print(f"Time: {datetime.datetime.now()}")
    print("------------------\n")

def log_request_received():
    # Log that the request was successfully received with a timestamp
    print(f"[{datetime.datetime.now()}] Request received\n")

def log_rejected_method(method):
    # If method is different from GET
    print(f"Rejected method: {method}")

def log_total_time(start_time):
    # Log the total time it took from receiving the request till the connection is closed
    print(f"Total time taken: {time.time() - start_time}\n\n")

def log_request_forwarded(host):
    # Log that we are now sending request to external URL with timestamp
    print(f"[{datetime.datetime.now()}] Request forwarded to {host}")

def log_response_received():
    # Log that response successfully received from external URL with timestamp
    print(f"[{datetime.datetime.now()}] Response received from server")

def log_response_sent_back():
    # Log that we successfully sent response back to client with timestamp
    print(f"[{datetime.datetime.now()}] Response sent to client")