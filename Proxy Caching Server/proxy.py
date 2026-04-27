import threading
import time
from socket import *

from CacheStats import CacheStats
from ProxyCache import ProxyCache
from functionalities.filtering import (is_host_blocked, is_address_blocked, is_port_blocked)
from functionalities.http_parser import parse_request, parse_response_status_line
from functionalities.logger import (log_response, log_rejected_method, log_request_forwarded,
                                    log_response_received, log_response_sent_back,
                                    log_blocked_host, log_blocked_address, init_logger,
                                    log_blocked_port, log_request, write_log)
from functionalities.send_errors import send_error, send_forbidden
from functionalities.https_tunneling import handle_tunnel

#standard buffer size 4KB, good enough for packets+memory (could be more or less)
BUFFER_SIZE = 4096
PROXY_PORT = 10000

# Initializes the logging file, a ProxyCache object for storing the cached responses, and a CacheStats object for 
# tracking statistics on the hits/misses since runtime.
init_logger()
cache = ProxyCache()
stats = CacheStats()

# This method is used only if a cache miss occurs; it fetches from the target server.
def fetch_from_server(client_socket, client_address, method, host, port, path, cache_key):
    #connect to target server as proxy (proxy becomes client here) since it didn't get a cache hit
    server_socket = socket(AF_INET, SOCK_STREAM)

    #use request's external host name and port
    server_socket.connect((host, port))

    #rebuild the parsed HTTP request
    #this is done in order to change full URLs into simple resource requests (like index.html)
    #since we're already connecting to external URL
    forward_request = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

    #send request to external URL
    server_socket.sendall(forward_request.encode())

    # Logs the request that it sent to the target server
    log_request_forwarded(host)

    # This variable is used to store the entire message for caching later.
    cache_response = b""
    total_size = 0 # used for logging purposes

    #receive response from external URL and forward back to client
    while True:
        #receive next packet from external URL
        #we keep receiving in case response larger than buffer size
        data = server_socket.recv(BUFFER_SIZE)
        #keep listening until no more data is received (ex: server closed connection)
        if len(data) == 0:
            break

        # tracking the total size of the response to log
        total_size += len(data) 

        # Logging the received response batch
        log_response_received(host, total_size)

        try:
            #send current packet back to client
            client_socket.sendall(data)
        
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            write_log("Client disconnected while sending response")
            break

        # Concatenates the chunks of data received from the target server to store it later in cache
        cache_response += data

    # Logging that the response from the target server reached the client
    log_response_sent_back(host, port, client_address)

    # Adds the response received to cache
    if cache_response:
        cache.set(cache_key, cache_response)

    # Parses the response's status line
    status_code, status = parse_response_status_line(cache_response)

    #call logger response method to log a brief response information
    log_response(status_code, status, total_size)

    #close current connection after response has been fully received
    server_socket.close()


# This method is run whenever an incoming request came from the client to the server.
def handle_client(client_socket, client_address):
    #This will be used to calculate total time taken from request to response
    start_time = time.time()

    try:
        #.recv()=read bytes from TCP stream
        #.decode()=convert HTTP to string
        request = client_socket.recv(BUFFER_SIZE).decode()

        #handle empty requests (example: if client disconnects) 
        if not request:
            return

        #call http_parser method to parse the request of the user and get the method, host, port, path and remaining headers
        parsed = parse_request(request)

        #standard HTTP requires proper response form to prevent crashing, if the returned value is None from
        # parse_request then there's an issue with the formatting; it sends a 400 Bad Request response.
        if not parsed:
            send_error(client_socket, 400, "Bad Request")
            return

        #assign each of the returned parsed values to a variable for easy access
        method, host, port, path, headers = parsed

        # checking if the host/port that the client is trying to access to is blacklisted or not.
        # If it is, we return a 403 HTTP message and log the attempt to request the host/port.
        if is_host_blocked(host):
            send_forbidden(client_socket, b"Access denied by proxy. You cannot request this host as it is blacklisted.\r\n")
            log_blocked_host(host)
            return

        if is_port_blocked(port):
            send_forbidden(client_socket, b"Access denied by proxy. You cannot request to this port number.\r\n")
            log_blocked_port(port)
            return

        # If the method is CONNECT then it's an HTTPS request - does NOT cache as proxy does not see what's being transfered 
        # between the server and the browser through the TCP tunnel opened by the proxy.
        if method == "CONNECT":
            log_request(client_address, method, host, port, headers, path if method == "GET" else None)

            # target is "hostname:port", it's not the full URL. Calls handle_tunnel which is from functionalities => https_tunneling.py
            handle_tunnel(client_socket, host, port)
            
            # Returns because there is no statistics for this as it's not cached.
            return
        
        # If the method is GET, then it's an HTTP request.
        # Adjusts cache key to store in cache, sends to target server if not found in cache or gets response from the cache server.
        elif method == "GET":

            # Forms the url to check if it exists in cache already, and to use it later to add to cache.
            cache_key = f"{host}:{port}{path}"

            # call logger request method to log the client's request
            log_request(client_address, method, host, port, headers, path if method == "GET" else None)

            # Getting the cache based on the key variable; if none exists then it returns None
            cache_result = cache.get(cache_key)
            if cache_result:
                # If it's found stored in cache, then it sends back the cached response to the client
                client_socket.sendall(cache_result)

                # It parses the status line of the response retrieved
                status_code, status = parse_response_status_line(cache_result)

                # Tracks the record hit time to the CacheStats class
                stats.record_hit(time.time() - start_time)

                # Logs the response that the client retrieved
                log_response(status_code, status, len(cache_result))
            else:
                # If it's not found in cache, then it fetches from the server using the fetch_from_server method
                fetch_from_server(client_socket, client_address, method, host, port, path, cache_key)

                # Tracks the miss time to the CacheStats class
                stats.record_miss(time.time() - start_time)

    
            # Logs the statistical summary since server runtime for HTTP requests only.
            stats.log_summary()

        # Any other method that's not GET or CONNECT is forbidden, so it sends a 405 response
        else: 
            log_rejected_method(method)
            send_error(client_socket, 405, "Method Not Allowed")
            return
        

    #catch connection or parsing errors to prevent crashes
    except Exception as e:
        write_log("Error:" + e)
        try:
            send_error(client_socket, 500, "Internal Server Error")
        except:
            pass  # socket already closed, ignore

    finally:
        client_socket.close()


def start_proxy():
    # AF_INET=ipv4 and SOCK_STREAM=TCP (TCP required for HTTP)
    server_socket = socket(AF_INET, SOCK_STREAM)

    # Resets the TIME_WAIT after stopping the server so it immediately starts again.
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # ''=listen to localhost
    server_socket.bind(('', PROXY_PORT))

    # 5 means max queued connections are 5, can be more or less
    server_socket.listen(5)


    write_log(f"Proxy running on port {PROXY_PORT}...") #logs where the proxy is running

    # constant listening to accept clients
    while True:
        #client_socket=proxy's communication link to client
        #client_address=IP + Port
        client_socket, client_address = server_socket.accept()

        # Checking if the client's IP address is blacklisted or no, if it is then it does not proceed with the request.
        # Sends a 403 HTTP response back and closes the connection
        if is_address_blocked(client_address[0]):
            send_forbidden(client_socket, b"Access denied by proxy. Your address is blacklisted, contact the developers if needed.\r\n")
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
