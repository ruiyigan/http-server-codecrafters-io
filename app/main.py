import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(
        ("localhost", 4221), reuse_port=True
    )  # HOW TO: https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only

    client_sock, client_addr = (
        server_socket.accept()
    )  # Wait for client returns client socket and address once client is connected

    with client_sock:
        while True:
            data = client_sock.recv(
                1024
            )  # HOW TO: https://realpython.com/python-sockets/
            if not data:
                break
            data = data.decode(
                "utf-8"
            )  # Specify endcoding to tell python how to read the bytes
            data_split = data.split()
            path = data_split[1]
            if path == "/":
                client_sock.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            else:
                if path[:6] == "/echo/":
                    echo_string = path[6:]
                    client_sock.sendall(
                        f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n\r\n{echo_string}".encode(
                            "utf-8"
                        )
                    )
                else:
                    client_sock.sendall(
                        b"HTTP/1.1 404 Not Found\r\n\r\n"
                    )  # Don’t see the \r\n\r\n when decoding b"HTTP/1.1 404 Not Found\r\n\r\n" is that \r\n (carriage return + line feed) is a special sequence used for formatting
    server_socket.close()


if __name__ == "__main__":
    main()
