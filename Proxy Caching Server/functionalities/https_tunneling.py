import threading
from socket import *
from .send_errors import send_error
from .logger import log_connect_tunnel_closed, log_connect_browser_established

def handle_tunnel(client_socket, host, port):
    server_socket = None

    try:
        # Tries to open a raw TCP connection to the target (host and port)
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.settimeout(10)
        server_socket.connect((host, port))

        # We tell the browser that the tunnel is ready. This is the last thing that our proxy does, the rest is 
        # between the server and the browser simultanously
        client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        log_connect_browser_established(host, port)

        # We remove the timeout for the server socket and the client socket so the tunnel stays open as long as needed
        server_socket.settimeout(None)
        client_socket.settimeout(None)

        _run_relay(client_socket, server_socket)
    
    except (ConnectionRefusedError, OSError) as e:
        send_error(client_socket, 502, "Bad Gateway")
    
    except socket.timeout:
        send_error(client_socket, 504, "Gateway Timeout")
    
    finally:
        # Closing both sockets when the tunnel ends
        for sock in [server_socket, client_socket]:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

        log_connect_tunnel_closed(host, port)


# Copies bytes from the passed source socket to the passed destination socket until connection closes.
# When done, it signals to the destination that no more data is coming
def _relay_one_direction(src_socket, dst_socket):
    try:
        while True:
            data = src_socket.recv(4096)
            if not data:
                # src closed the connection, so we end it
                break
            
            # Sends the data to the destination
            dst_socket.sendall(data)
    
    except (OSError, ConnectionResetError, BrokenPipeError):
        # This means probably that one side closed abruptly, not an error - just end of session
        pass

    finally:
        # At the end, we signal to the destination that writing is over from the source.
        # SHUT_WR sends FIN to dst without closing the socket entirely, giving the other relay thread
        # time to drain remaining data. 
        try:
            dst_socket.shutdown(SHUT_WR)
        except Exception: 
            pass

# Spawns two threads one per direction, and waits for both to finish.
# This is full duplex: both directions carry data simultaneously.
def _run_relay(client_socket, server_socket):
    t1 = threading.Thread(
        target=_relay_one_direction,
        args=(client_socket, server_socket), # from thr browser to the server
        daemon=True # a deamon thread = runs in the background and will automatically terminate when the main program exits.
    )

    t2 = threading.Thread(
        target=_relay_one_direction,
        args=(server_socket, client_socket), #server => browser thread connection
        daemon=True
    )

    t1.start()
    t2.start()
    t1.join() # waits for both direction threads to close/terminate before returning
    t2.join() # handle_tunnel's finally block then cleans up sockets