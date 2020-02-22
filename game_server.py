import sys
import socket
import select
import multiprocessing as mp
import threading
import yaml

class Player:
    def __init__(self):
        pass

class Room:
    def __init__(self):
        pass

class MessageQueue:
    def __init__(self):
        pass

def worker():
    pass

def send(connection, yaml_data):
    string = yaml.dump(yaml_data)
    connection.send(bytes(string, "utf8") + b"\n")

class Selector:
    def __init__(self, server_socket):
        self.server_socket = server_socket
        self.connection_map = {}
        self.buffer_map = {}
        self.requests_map = {}
        self.room_map = {}
        self.buffer_size = 1024

    def run(self):
        select_poll = select.poll()
        select_poll.register(self.server_socket, select.POLLIN)

        try:
            while True:
                ready = select_poll.poll()

                if not ready:
                    break

                for fd, event in ready:
                    if fd == self.server_socket.fileno():
                        connection, address = self.server_socket.accept()
                        new_fd = connection.fileno()

                        for other_fd in self.connection_map:
                            send(self.connection_map[other_fd], { "room": 0, "enter": new_fd })

                        self.connection_map[new_fd] = connection
                        self.buffer_map[new_fd] = ""
                        self.requests_map[new_fd] = []
                        self.room_map[new_fd] = 0

                        # send(connection, { "room": 0, "list": list(self.connection_map.keys()) })
                        self.send_list(connection)

                        select_poll.register(connection, select.POLLIN)
                    else:
                        connection = self.connection_map[fd]

                        message = connection.recv(self.buffer_size)

                        print(fd, message)

                        if message:
                            self.buffer_map[fd] += str(message, "utf8")
                            index = self.buffer_map[fd].find("\n\n")
                            if index >= 0:
                                data = yaml.load(self.buffer_map[fd][: index + 2], Loader = yaml.FullLoader)
                                self.buffer_map[fd] = self.buffer_map[fd][index + 2 :]
                                if data.get("system") == "close":
                                    send(connection, { "system": "close" })
                        else:
                            select_poll.unregister(connection)
                            connection.close()

                            del self.connection_map[fd]
                            del self.buffer_map[fd]
                            del self.requests_map[fd]
                            del self.room_map[fd]

                            for other_fd in self.connection_map:
                                send(self.connection_map[other_fd], { "room": 0, "exit": fd })

                print(self.buffer_map)

        except Exception as error:
            sys.stderr.write("Error: Selector {}\n".format(error))

    def send_list(self, connection):
        data = [{ "fd": fd, "room_id": room_id } for fd, room_id in self.room_map.items()]
        send(connection, { "room": 0, "list": data })

def main(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1024)

    server_socket.setblocking(False)

    selector = Selector(server_socket)

    selector_thread = threading.Thread(target = selector.run)

    selector_thread.start()

if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])

    main(host, port)
