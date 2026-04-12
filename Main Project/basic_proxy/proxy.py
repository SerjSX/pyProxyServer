from socket import *

from http_parser import parse_http_request, parse_response_status_line
from logger import (log_request, log_response, log_request_received,
                    log_rejected_method, log_total_time, log_request_forwarded,
                    log_response_received, log_response_sent_back)
import threading
from proxy_cache import ProxyCache
import time

#standard buffer size 4KB, good enough for packets+memory (could be more or less)
BUFFER_SIZE = 4096
PROXY_PORT = 10000

cache = ProxyCache()

def handle_client(client_socket, client_address):
    #this will be used to calculate total time taken from request to response
    start_time = time.time()

    try:
        #.recv()=read bytes from TCP stream
        #.decode()=convert HTTP to string
        request = client_socket.recv(BUFFER_SIZE).decode()

        #handle empty requests (example: if client disconnects)
        if not request:
            return

        #call http_parser method
        parsed = parse_http_request(request)

        #standard HTTP requires proper response form to prevent crashing
        if not parsed:
            client_socket.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        log_request_received()

        #assign each of the returned parsed values to a variable
        method, host, port, path, headers = parsed

        #Checking if the method is not GET first, then sending a proper error response
        if method != "GET":
            log_rejected_method(method)
            client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            return

        # Forms the url to check if it exists in cache already, and to use it later to add to cache.
        cache_key = host + path

        # call logger request method
        log_request(client_address, method, path, host, headers)

        # Getting the cache based on the key variable; if none exists then it returns None
        cache_result = cache.get(cache_key)
        if cache_result:
            # If it's found stored in cache, then it sends back the cached response to the client
            print(f"HIT: {cache_key}")
            client_socket.sendall(cache_result)
            status_code, status = parse_response_status_line(cache_result)
            log_response(status_code, status, len(cache_result))
            log_total_time(start_time)
            return

        else:
            print(f"MISS: {cache_key}. Fetching from server...")

        #connect to target server as proxy (proxy becomes client here)
        server_socket = socket(AF_INET, SOCK_STREAM)
        #use request's external host name and port
        server_socket.connect((host, port))

        #rebuild the parsed HTTP request
        #this is done in order to change full URLs into simple resource requests (like index.html)
        #since we're already connecting to external URL
        forward_request = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

        log_request_forwarded(host)

        #send request to external URL
        server_socket.sendall(forward_request.encode())

        # This variable is used to store the entire message for caching later.
        cache_response = b""
        total_size = 0

        #receive response from external URL and forward back to client
        while True:
            #receive next packet from external URL
            #we keep receiving in case response larger than buffer size
            data = server_socket.recv(BUFFER_SIZE)
            #keep listening until no more data is received (ex: server closed connection)
            if len(data) == 0:
                break

            log_response_received()

            total_size += len(data)

            try:
                #send current packet back to client
                client_socket.sendall(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                print("Client disconnected while sending response")
                break
            #prepare cache variable to store in cache dictionary
            cache_response += data

        log_response_sent_back()

        # Adds the response received to cache
        if cache_response:
            cache.set(cache_key, cache_response)

        status_code, status = parse_response_status_line(cache_response)

        #call logger response method
        log_response(status_code, status, total_size)

        #close current connection after response has been fully received
        server_socket.close()

    #catch connection or parsing errors to prevent crashes
    except Exception as e:
        print("Error:", e)
        try:
            client_socket.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
        except:
            pass  # socket already closed, ignore

    finally:
        client_socket.close()

    log_total_time(start_time)


def start_proxy():
    # AF_INET=ipv4 and SOCK_STREAM=TCP (TCP required for HTTP)
    server_socket = socket(AF_INET, SOCK_STREAM)
    # ''=listen to localhost
    server_socket.bind(('', PROXY_PORT))
    # 5 means max queued connections are 5, can be more or less
    server_socket.listen(5)

    print(f"Proxy running on port {PROXY_PORT}...")

    # constant listening to accept clients
    while True:
        #client_socket=proxy's communication link to client
        #client_address=IP + Port
        client_socket, client_address = server_socket.accept()

        # Opens a new thread to handle the client's request 
        t = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )
        t.start()
        #handle_client(client_socket, client_address)


if __name__ == "__main__":
    start_proxy()
