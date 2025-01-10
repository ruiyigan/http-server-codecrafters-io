import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(
        ("localhost", 4221), reuse_port=True
    )  # HOW TO: https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only

    client_sock, client_addr = (
        server_socket.accept()
    )  # wait for client returns client socket and address once client is connected

    with client_sock:
        while True:
            data = client_sock.recv(
                1024
            )  # HOW TO: https://realpython.com/python-sockets/
            if not data:
                break
            data = data.decode("utf-8")
            data_split = data.split()
            path = data_split[1]
            if path == "/":
                client_sock.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            else:
                client_sock.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    server_socket.close()


if __name__ == "__main__":
    main()
