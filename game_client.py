# import pygame
# import pygame.locals
import sys
import time
import yaml
import socket
import threading
import queue
import select

import tkinter as tk

import gui


class SceneLobby(tk.Canvas):
    def __init__(self, hub):
        super().__init__(hub.window.master, width = 1280, height = 720, bg = "#218721")
        self.width = 1280
        self.height = 720
        self.page = 0
        self.chunk = 2
        self.pack()
        self.socket = hub.socket
        self.rooms = [[] for _ in range(65)]

    def execute(self, command):
        if command["room"] == 0:
            if command.get("list") is not None:

                for item in command["list"]:
                    self.rooms[item["room_id"]].append(item["fd"])

                self.render()

            elif command.get("enter") is not None:
                room_id = command["enter"]["room_id"]
                fd = command["enter"]["room_id"]
                self.rooms[room_id].append(fd)

            elif command.get("exit") is not None:
                room_id = comand["exit"]["room_id"]
                fd = command["enter"]["room_id"]
                self.rooms[room_id].remove(fd)


    def render(self):
        h = self.height
        margin = h / 12
        first_room_id = self.page * (self.chunk ** 2) + 1

        for i in range(self.chunk):
            for j in range(self.chunk):
                first_room_id + i * self.chunk + j
                size = (7 * h) / (8 * self.chunk) - h / 24
                top = margin + i * (size + h / 24)
                left = margin + j * (size + h / 24)
                self.create_rectangle(left, top, left + size, top + size, fill = "yellow")

        self.create_rectangle(self.height, 0, self.width, self.height, fill = "white")

    def draw(self, screen):
        sysfont = pygame.font.SysFont(None, 80)
        screen.fill((255, 255, 255))
        string = ",".join([str(x) for x in self.rooms[0]])
        font = sysfont.render(string, True, (0, 0, 0))
        screen.blit(font, (30, 30))



class SceneSwitch:
    def __init__(self):
        pass

    def set_scene(self, scene):
        self.scene = scene

    def send(self, command):
        self.scene.execute(command)


def send(client_socket, data):
    string = yaml.dump(data)
    client_socket.sendall(bytes(string, "utf8") + b"\n")


def receive_loop(client_socket, command_receiver):
    try:
        while True:
            response = client_socket.recv(1024)
            string = str(response, "utf8")
            print("[receive]: " + string)
            index = string.find("\n\n")

            if index >= 0:
                data = yaml.load(string[: index + 2], Loader = yaml.FullLoader)
                if data.get("system") == "close":
                    command_receiver.put({ "system": "end" })
                    return
                command_receiver.put(data)
                string = string[index + 2 :]
    except:
        command_receiver.put({ "system": "end" })
        print("thread 'receive' end")

def command_loop(command_receiver, scene_switch):
    while True:
        data = command_receiver.get()
        print("[loop]: " + str(data))

        if data.get("system") == "end":
            return print("thread 'loop' end")

        scene_switch.send(data)


class Hub:
    def __init__(self, client_socket, window):
        self.socket = client_socket
        self.window = window


def main(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    command_receiver = queue.Queue()

    scene_switch = SceneSwitch()

    thread_receive_loop = threading.Thread(target = receive_loop, args = (client_socket, command_receiver))
    thread_command_loop = threading.Thread(target = command_loop, args = (command_receiver, scene_switch))

    def before_quit_action():
        send(client_socket, { "system": "close" })
        thread_receive_loop.join()
        client_socket.close()

    config = {
        "before_quit_action": before_quit_action
    }

    window = gui.create_window(config)

    hub = Hub(client_socket = client_socket, window = window)
    scene_switch.set_scene(SceneLobby(hub))


    thread_receive_loop.start()
    thread_command_loop.start()



    gui.start(window)


if __name__ == '__main__':
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    main(server_host, server_port)
