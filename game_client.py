import pygame
import pygame.locals
import sys
import time
import yaml
import socket
import threading
import queue
import select

class GameBody:
    def __init__(self):
        pass

class SceneLobby:
    def __init__(self, client_socket):
        self.buffer = ""
        self.socket = client_socket
        self.rooms = [[] for _ in range(65)]
        self.lock_rooms = threading.Lock()

    def execute(self, command):
        if command["room"] == 0:
            if command.get("list") is not None:
                self.lock_rooms.acquire()

                for x in command["list"]:
                    self.rooms[0].append(x)

                self.lock_rooms.release()

            elif command.get("enter") is not None:
                self.lock_rooms.acquire()
                self.rooms[0].append(command["enter"])
                self.lock_rooms.release()

            elif command.get("exit") is not None:
                self.lock_rooms.acquire()
                self.rooms[0].remove(command["exit"])
                self.lock_rooms.release()

    def draw(self, screen):
        sysfont = pygame.font.SysFont(None, 80)
        screen.fill((255, 255, 255))
        string = ",".join([str(x) for x in self.rooms[0]])
        font = sysfont.render(string, True, (0, 0, 0))
        screen.blit(font, (30, 30))

class Lobby:
    def __init__(self):
        pass

class Room:
    pass

class Command:
    pass

def send(client_socket, data):
    string = yaml.dump(data)
    client_socket.sendall(bytes(string, "utf8") + b"\n")

def receive(client_socket, command_queue):
    while True:
        response = client_socket.recv(1024)
        string = str(response, "utf8")
        print("receive: " + string)
        index = string.find("\n\n")

        if index >= 0:
            data = yaml.load(string[: index + 2], Loader = yaml.FullLoader)
            command_queue.put(data)
            string = string[index + 2 :]

def loop(command_queue, scene_lobby):
   while True:
        data = command_queue.get()
        print("loop: " + str(data))
        scene_lobby.execute(data)

def main(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    command_queue = queue.Queue()

    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Game!")


    location = "lobby"

    scene_lobby = SceneLobby(client_socket)

    event = threading.Event()

    thread_receive = threading.Thread(target = receive, args = (client_socket, command_queue))
    thread_loop = threading.Thread(target = loop, args = (command_queue, scene_lobby))

    thread_receive.start()
    thread_loop.start()

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)

        scene_lobby.draw(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                client_socket.close()
                return

if __name__ == '__main__':
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    main(server_host, server_port)
