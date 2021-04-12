from client import Client, PyChatError
from clientutils import ServerClosedError
from tkinter import Tk, Menu, StringVar, Entry, Button, Label, Frame
import socket

# Définition des constantes de la fenêtre
TITLE = "PyChat"
SIZE = (720, 480)
ICON = None

DEFAULT_HOST = "127.0.0.1"


# Définition des fonctions
def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()


def toLogin():
    hostBox.pack_forget()
    loginBox.pack()


def toHost():
    loginBox.pack_forget()
    hostBox.pack()


def toChat():
    error("The chat interface doesn't exist !")


def disconnect():
    pass


def login():
    global client

    if usernameEntry['fg'] == usernameEntry.placeholder_color:
        username = ""
    else:
        username = usernameVar.get()
    if passwordEntry['fg'] == passwordEntry.placeholder_color:
        password = ""
    else:
        password = passwordVar.get()

    try:
        client = Client(username, password, hostVar.get())
    except ServerClosedError:
        client.close()
        error("Server closed !")
        toHost()
        return

    try:
        client.connect()
    except PyChatError as e:
        error(e.args[0])
    else:
        toChat()


def signin():
    global client

    if usernameEntry['fg'] == usernameEntry.placeholder_color:
        username = ""
    else:
        username = usernameVar.get()
    if passwordEntry['fg'] == passwordEntry.placeholder_color:
        password = ""
    else:
        password = passwordVar.get()

    try:
        client = Client(username, password, hostVar.get())
    except ServerClosedError:
        client.close()
        error("Server closed !")
        toHost()
        return

    try:
        client.createUser()
    except PyChatError as e:
        error(e.args[0])
    else:
        login()


def validHost():
    if not setHost():
        error("Invalid host !")
    elif not isOpen(hostVar.get(), 11313):
        error("Server closed !")
    else:
        errorVar.set("")
        toLogin()


def checkHost(host):
    if host == "":
        host = DEFAULT_HOST
        return host
    try:
        host = socket.gethostbyname(host)
    except socket.gaierror:
        return False
    else:
        return host


def setHost():
    host = checkHost(hostVar.get())

    if not host:
        hostVar.set("")
        return False

    hostVar.set(host)
    return True


def error(errorMessage):
    errorVar.set(errorMessage)


# Définition d'une classe copiés-collés de stackoverflow (mais je l'ai modifié donc ça vas)
class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, *args, placeholder="PLACEHOLDER", **kwargs):
        super().__init__(master, *args, **kwargs)

        self.default_show = kwargs.get("show", "")
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self["show"] = ""
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self["show"] = self.default_show
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


# Création de la fenêtre
window = Tk()
window.title(TITLE)
window.geometry(f"{SIZE[0]}x{SIZE[1]}")
window.iconbitmap(ICON)

# Création du menu de la fenêtre
menu = Menu(window)
server_menu = Menu(menu, tearoff=0)
server_menu.add_command(label="Disconnect", command=disconnect)
menu.add_cascade(menu=server_menu, label="Server")
window.config(menu=menu)

errorVar = StringVar()

# Host
hostVar = StringVar()

errorLabel = Label(window, textvariable=errorVar, fg="red")

hostBox = Frame(window)

hostEntry = EntryWithPlaceholder(hostBox, placeholder=DEFAULT_HOST, textvariable=hostVar)
hostEntry.bind("<Return>", lambda e: validHost())

validHostButton = Button(hostBox, text="Connect", command=validHost)

hostEntry.pack()
validHostButton.pack()

# Login
client = None

usernameVar = StringVar()
passwordVar = StringVar()

loginBox = Frame(window)

usernameEntry = EntryWithPlaceholder(loginBox, placeholder="Username", textvariable=usernameVar)
passwordEntry = EntryWithPlaceholder(loginBox, placeholder="Password", textvariable=passwordVar, show="●")
usernameEntry.bind("<Return>", lambda e: login())
passwordEntry.bind("<Return>", lambda e: login())

buttonGrid = Frame(loginBox)
loginButton = Button(buttonGrid, text="Log in", command=login)
signInButton = Button(buttonGrid, text="Sign in", command=signin)

usernameEntry.pack()
passwordEntry.pack()

loginButton.grid(row=0, column=0)
signInButton.grid(row=0, column=1)
buttonGrid.pack()

errorLabel.pack()
hostBox.pack()

# Ouverture de la fenêtre
window.mainloop()
