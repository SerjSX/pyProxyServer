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
