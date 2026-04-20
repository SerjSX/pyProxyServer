import datetime
import time

def log_request(method, path, host, headers):
    print("---- REQUEST ----")
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


def log_response(status_code, status, size, type):
    print(f"\n---- RESPONSE ----")
    print(f"Status: {status_code} {status}")
    print(f"Size: {size} bytes")
    #show response timestamp
    print(f"Time: {datetime.datetime.now()}")
    print(f"Response Type: {type.upper()}")
    print("------------------\n")

def log_request_received(client_address, host):
    # Log that the request was successfully received with a timestamp
    print(f"\n[{datetime.datetime.now()}] Request received from client {client_address[0]}:{client_address[1]} to host: {host}\n")

def log_rejected_method(method):
    # If method is different from GET
    print(f"Rejected method: {method}")

def log_total_time(start_time):
    # Log the total time it took from receiving the request till the connection is closed
    print(f"Total time taken: {time.time() - start_time}\n\n")

def log_request_forwarded(host):
    # Log that we are now sending request to external URL with timestamp
    print(f"[{datetime.datetime.now()}] Request forwarded to {host}")

def log_response_received(current_size):
    # Log that response successfully received from external URL with timestamp
    print(f"[{datetime.datetime.now()}] Response received from server; current size = {current_size}B")

def log_response_sent_back():
    # Log that we successfully sent response back to client with timestamp
    print(f"[{datetime.datetime.now()}] Response sent to client")

def log_blocked_host():
    print(f"[{datetime.datetime.now()}] Blocked the request attempt since it's blacklisted.")

def log_blocked_address(client_ip):
    print(f"[{datetime.datetime.now()}] Blocked the client from requesting anything since their address is blacklisted: {client_ip}")

def format_forbidden(body):
    return (b"HTTP/1.0 403 Forbidden\r\n"
              b"Content-Type: text/plain; charset=utf-8\r\n"
            + f"Content-Length: {len(body)}\r\n".encode()
            + b"Connection: close\r\n"
            + b"\r\n"
            + body)