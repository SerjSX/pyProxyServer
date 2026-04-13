from socket import *

from http_parser import parse_http_request, parse_response_status_line
from logger import (log_request, log_response, log_request_received,
                    log_rejected_method, log_total_time, log_request_forwarded,
                    log_response_received, log_response_sent_back,
                    log_blocked_host, log_blocked_address)
from filtering import (is_host_blocked, is_address_blocked)
from response_text_util import (format_forbidden)
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

        #assign each of the returned parsed values to a variable
        method, host, port, path, headers = parsed

        log_request_received(client_address, host)

        # checking if the host that the client is trying to access to is blacklisted or not.
        # If it is, we return a 403 HTTP message and log the attempt to request the host.
        if is_host_blocked(host):
            client_socket.sendall(format_forbidden(b"Access denied by proxy. You cannot request this host as its blacklisted.\r\n"))
            log_blocked_host()
            return


        #Checking if the method is not GET first, then sending a proper error response
        if method != "GET":
            log_rejected_method(method)
            client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            return

        # Forms the url to check if it exists in cache already, and to use it later to add to cache.
        cache_key = host + path

        # call logger request method
        log_request(method, path, host, headers)

        # Getting the cache based on the key variable; if none exists then it returns None
        cache_result = cache.get(cache_key)
        if cache_result:
            # If it's found stored in cache, then it sends back the cached response to the client
            client_socket.sendall(cache_result)
            status_code, status = parse_response_status_line(cache_result)
            log_response(status_code, status, len(cache_result), "hit")
            log_total_time(start_time)
            return

        #connect to target server as proxy (proxy becomes client here) since it didn't get a cache hit
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

            total_size += len(data)

            # Logging the received response batch
            log_response_received(total_size)

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
        log_response(status_code, status, total_size, "miss")

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

    # Resets the TIME_WAIT after stopping the server so it immediately starts again.
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

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

        # Checking if the client's IP address is blacklisted or no, if it is then it does not proceed with the request.
        # Sends a 403 HTTP respone back and closes the connection
        if is_address_blocked(client_address[0]):
            client_socket.sendall(format_forbidden(b"Access denied by proxy. Your address is blacklisted, contact the developers if needed.\r\n"))
            log_blocked_address(client_address[0])
            client_socket.close()
            continue

        # Opens a new thread to handle the client's request 
        t = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )
        t.start()


if __name__ == "__main__":
    start_proxy()
