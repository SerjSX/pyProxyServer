def format_forbidden(body):
    msg = (b"HTTP/1.0 403 Forbidden\r\n"
              b"Content-Type: text/plain; charset=utf-8\r\n"
            + f"Content-Length: {len(body)}\r\n".encode()
            + b"Connection: close\r\n"
            + b"\r\n"
            + body)
    
    return msg