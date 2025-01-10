import socket  # noqa: F401
import threading


def parse_request(request_data):
    decoded_data = request_data.decode("utf-8")
    lines = decoded_data.split("\r\n")
    method, path, version = lines[0].split()

    host = ""
    user_agent = ""

    for line in lines:
        if "Host:" in line:
            host = line.split()[1]
        if "User-Agent:" in line:
            user_agent = line.split()[1]

    return method, path, version, host, user_agent


def handler(client_sock):
    with client_sock:
        data = client_sock.recv(1024)  # HOW TO: https://realpython.com/python-sockets/

        method, path, version, host, user_agent = parse_request(data)

        if path == "/":
            client_sock.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        elif path == "/user-agent":
            client_sock.sendall(
                f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode(
                    "utf-8"
                )
            )
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


def main():
    server_socket = socket.create_server(
        ("localhost", 4221), reuse_port=True
    )  # HOW TO: https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only

    try:
        while True:
            client_sock, client_addr = server_socket.accept()
            threading.Thread(
                target=handler, args=(client_sock,), daemon=True
            ).start()  # Use this to test https://github.com/hatoo/oha
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
