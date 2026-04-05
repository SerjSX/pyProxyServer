from socket import *;
from urllib.parse import urlparse
from datetime import datetime

# The server will run on port 8888
PORT = 8888

# Creating the server's socket and binding the port to it, plus accepting queuing up to 10
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', PORT))
server_socket.listen(10)

# Printing an output for the admin 
print(f"Server running on port {PORT}")

# This method is responsible to forward the request to the origin server, plus getting and returning the response back to the user 
def forwardRequest(method, host, port, path):
    # Creating a basic forward request without persistant connection based on the host and path that the client is trying to connect to
    # Encoding it before sending to the origin server
    forward_request = (
        f"GET {path} HTTP/1.0\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode()

    # Creating a socket for the target server.
    target_socket = socket(AF_INET, SOCK_STREAM)
    target_socket.settimeout(10) # to not wait forever
    target_socket.connect((host, port)) #connecting to the host at its port 
    target_socket.sendall(forward_request) #sending the request, retrying automatically if it fails

    # receiving full response; which is in batches/chunks
    response = b''
    while True:
        # Getting the first 4096B chunk 
        chunk = target_socket.recv(4096)
        if not chunk: #if empty then we received everything, so the while True loop is broken
            break;
        else:
            # If not empty, we add the response to the response variable
            response += chunk

    # Saving the response time
    response_time = datetime.now()

    target_socket.close() # closing target connection

    # returning the response and the response_time
    return (response, response_time);

# This method is responsible for parsing the request of the user's browser, plus checking for errors
def parseRequest(client_socket):
    # First line is needed to extract the method, target host, port, and requested resource
    # requested resource is actually on the first line too with the main URL.
    raw = client_socket.recv(4096).decode()

    # if the request is empty, then return. The browser does it sometimes possibly when using cached version
    if not raw:
        print("Ignored empty request, possibly from browser loading from cache.")
        return

    # Output for the admin
    print("Parsing the request...")

    # Splitting the request so each line of the request would be a separate value in the list
    splitted_request = raw.split("\r\n")
    request_line = splitted_request[0] # Extracting only the first line and putting it in a separate variable; this is the request line
    
    # Splitting the parts of the requests line
    request_line_parts = request_line.split(' ')
    # ensuring all parts exist (3)
    if len(request_line_parts) < 3:
        # If there are missing ports, print an output to the admin and send a bad request HTTP response back to the user
        print("\tAll parts in the request must be in valid format. Ignoring this request.")
        client_socket.sendall(b"HTTP/1.0 400 Bad Request\r\n\r\n")

        # Leaves the method.
        return

    # Separates the parts of the request lines to three
    method, url, version = request_line_parts

    # Only accepting GET methods so far, so anything else is not considered
    if method != "GET":
        # Printing to the admin and sending a 501 response to the client
        print(f"\tOnly GET method is allowed so far, ignoring this request with the method {method}")
        client_socket.sendall(b"HTTP/1.0 501 Not Implemented\r\n\r\n")
        return

    # Parsing the url to get the host, port and path of the requested resource
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or 80
    path = parsed_url.path or "/"

    # If the host is empty then ignore it, may be localhost.
    if host is None:
        # Printing to the admin and sending a 501 response to the client
        print("\tIgnoring this request because the host is empty; possibly a localhost connection.")
        client_socket.sendall(b"HTTP/1.0 501 Not Implemented\r\n\r\n")
        return

    # After successfully parsing, printing output to the admin to show the progress
    print("\tThe requested URL from the client is: " + url)

    # Returning the values in a tuple 
    return (method, host, port, path)


while True:
    # The server accepts a client's connection
    client_socket, (client_ip, client_port) = server_socket.accept()
    request_time = datetime.now() # storing the request time as the current

    try:
        # Printing the request time for the admin
        print(f"{request_time} ==> Got a request from client with the following IP:PORT => {client_ip}:{client_port}")

        # Parsing the request received from the client 
        parsed_request = parseRequest(client_socket)

        # Only proceed if the value returned from the parseRequest is not empty, if it is then
        # something was wrong in the request and it was ignored.
        if (parsed_request):
            # Extracting the method, host, port and the path of the requested page from the parsed_request method's returned values
            method,host,port,path = parsed_request

            # Printing for the admin to show progress
            print(f"\tThe method of the request is {method};\n\tThe host is {host}, port is {port} and path is {path}. Now forwarding to the origin server...")
 
            # Using the forwardRequest method to send the request to the origin server and storing the response returned from it
            (client_response, response_time) = forwardRequest(method, host, port, path);
            
            # logging for the admin the time when we received the response
            print(f"{response_time} ==> Retrieved response, and sending it now to the user...")

            # Sending the response to the client
            client_socket.sendall(client_response)

            # Done
            print("Done!")

        # Separator to keep the terminal screen clean
        print("\n")
    
    # In case unexpected errors occurred 
    except Exception as e:
        print(f"Unhandled error: {e}")
    finally:
        # closes the client's socket once everything is done
        client_socket.close()