import sys
import socket
import select
import multiprocessing as mp
import threading

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

class Selector:
    def __init__(self, server_socket):
        self.server_socket = server_socket
        self.connection_map = {}
        self.buffer_map = {}
        self.requests_map = {}
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

                        self.connection_map[connection.fileno()] = connection
                        self.buffer_map[connection.fileno()] = ""
                        self.requests_map[connection.fileno()] = []

                        select_poll.register(connection, select.POLLIN)
                    else:
                        connection = self.connection_map[fd]

                        message = connection.recv(self.buffer_size)

                        if message:
                            self.buffer_map[fd] += str(message, "utf8")
                        else:
                            select_poll.unregister(connection)
                            connection.close()

                            del self.connection_map[fd]
                            del self.buffer_map[fd]
                            del self.requests_map[fd]

                print(self.buffer_map)

        except Exception as error:
            sys.stderr.write("Error: Selector {}\n".format(error))

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
