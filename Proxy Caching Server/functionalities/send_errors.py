"""
This is a small module having two methods related to sending error responses to a client's socket:
    - send_forbidden(client_socket, body): sends a 403 message with a correct format o the client's socket, with a custom body passed from proxy.py
    - send_error(socket, status_code, status_text): used to send any error response with any status code and a given status text to a given client socket.
"""

def send_forbidden(client_socket, body):
    message = (
        b"HTTP/1.1 403 Forbidden\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        + f"Content-Length: {len(body)}\r\n".encode()
        + b"Connection: close\r\n"
        + b"Proxy-Connection: close\r\n"
        + b"\r\n"
        + body
    )

    client_socket.sendall(message)

def send_error(socket, status_code, status_text):
    message = f"HTTP/1.1 {status_code} {status_text}\r\nConnection: close\r\n\r\n"
    socket.sendall(message.encode())
