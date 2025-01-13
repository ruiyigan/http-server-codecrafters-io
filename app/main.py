import argparse
import socket  # noqa: F401
import threading
from pathlib import Path


def parse_request(request_data):
    decoded_data = request_data.decode("utf-8")
    lines = decoded_data.split("\r\n")
    method, path, version = lines[0].split()

    host = ""
    user_agent = ""
    content_type = ""
    content_length = ""
    content = ""
    accept_encoding = ""

    for line in lines:
        if "Host:" in line:
            host = line.split()[1]
        if "User-Agent:" in line:
            user_agent = line.split()[1]
        if "Content-Type" in line:
            content_type = line.split()[1]
        if "Content-Length" in line:
            content_length = line.split()[1]
        if "Accept-Encoding" in line:
            accept_encoding = line.split()[1]

    if content_length:
        content = lines[-1]

    return (
        method,
        path,
        version,
        host,
        user_agent,
        content_type,
        content_length,
        content,
        accept_encoding,
    )


def parse_response(
    *,
    status: int,
    content_type: str = None,
    content: str = None,
    accept_encoding: str = None
) -> bytes:
    header = "HTTP/1.1 "
    if status == 404:
        header += "404 Not Found\r\n"
    elif status == 201:
        header += "201 Created\r\n"
    else:  # assume 200
        header += "200 OK\r\n"
        if accept_encoding == "gzip":
            header += "Content-Encoding: gzip" + "\r\n"
        if content_type:
            header += "Content-Type: " + content_type + "\r\n"
        if content:
            header += "Content-Length: " + str(len(content)) + "\r\n"

    response_string = header + "\r\n"
    if content:
        response_string += content

    return response_string.encode("utf-8")


def handler(client_sock, directory):
    with client_sock:
        data = client_sock.recv(1024)  # HOW TO: https://realpython.com/python-sockets/

        (
            method,
            path,
            version,
            host,
            user_agent,
            content_type,
            content_length,
            content,
            accept_encoding,
        ) = parse_request(data)

        if method == "POST":
            if path[:7] == "/files/":
                file_name = path[7:]
                file_path = directory + file_name
                with open(file_path, "w") as f:
                    f.write(content)
                client_sock.sendall(parse_response(status=201))

        if method == "GET":
            if path == "/":
                client_sock.sendall(parse_response(status=200))
            elif path == "/user-agent":
                client_sock.sendall(
                    parse_response(
                        status=200, content_type="text/plain", content=user_agent
                    )
                )
            elif path[:7] == "/files/":
                file_name = path[7:]
                file_path = directory + file_name
                if Path(file_path).is_file():
                    file = open(file_path, "r")
                    file_content = file.read()
                    client_sock.sendall(
                        parse_response(
                            status=200,
                            content_type="application/octet-stream",
                            content=file_content,
                        )
                    )
                else:
                    client_sock.sendall(parse_response(status=404))

            else:
                if path[:6] == "/echo/":
                    echo_string = path[6:]
                    client_sock.sendall(
                        parse_response(
                            status=200,
                            content_type="text/plain",
                            content=echo_string,
                            accept_encoding=accept_encoding,
                        )
                    )
                else:
                    client_sock.sendall(parse_response(status=404))


def main():
    parser = argparse.ArgumentParser(description="A simple HTTP server.")
    parser.add_argument(
        "--directory",
        type=str,
        required=False,
        help="Directory where the files are stored.",
    )
    args = parser.parse_args()
    directory = args.directory

    server_socket = socket.create_server(
        ("localhost", 4221), reuse_port=True
    )  # HOW TO: https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only

    try:
        while True:
            client_sock, client_addr = server_socket.accept()
            threading.Thread(
                target=handler, args=(client_sock, directory), daemon=True
            ).start()  # Use this to test https://github.com/hatoo/oha
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
