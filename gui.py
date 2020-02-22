import tkinter as tk


class Window(tk.Frame):
    def __init__(self, master, config = None):
        if config is None:
            config = {}

        super().__init__(master)
        self.master = master
        self.pack()
        self.master.title("Game Client")
        self.create_widgets()

        self.before_quit_action = config.get("before_quit_action")

    def create_widgets(self):
        self.button = tk.Button(self)
        self.button["text"] = "Hello, world!"
        self.button["command"] = self.hello
        self.button.pack(side="top")

        self.master.protocol("WM_DELETE_WINDOW", self.quit)

    def set_canvas(self, canvas):
        self.canvas = canvas

    def hello(self):
        print("Hello!")

    def quit(self):
        if self.before_quit_action is not None:
            self.before_quit_action()

        print("on_quit()")
        self.master.destroy()


def create_window(config):
    root = tk.Tk()
    return Window(root, config)

def start(window):
    window.mainloop()


def window_mainloop():
    root = tk.Tk()
    app = Window(root)
    app.mainloop()


if __name__ == '__main__':
    window_mainloop
