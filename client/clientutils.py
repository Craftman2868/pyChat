from socket import socket


class CommandNotFound(Exception):
    def __init__(self, command):
        self.args = f"Command '{command}' not found",


port = 1313

commands = ["connect", "message", "disconnect", "createuser"]


def sendCommand(sock: socket, command: str, arg=[]):
    if command not in commands:
        raise CommandNotFound(command)
    command = commands.index(command)
    if type(arg) == str:
        arg = arg.encode()
    elif type(arg) == int:
        arg = [arg]
    elif type(arg) == list:
        print(arg)
        for i, a in enumerate(arg):
            if type(a) == str:
                arg[i] = a.encode()
            else:
                arg[i] = bytes(a)
        arg = b";".join(arg)
    while arg.endswith(b";"):
        arg = arg[:-1]
    sock.send(bytearray([command, *arg]))
    print("En attente de réponse...")
    r = sock.recv(1024)
    print("Réponse reçue:", r)
    if not r:
        return 0,
    return int(r[0]), r[1:]


def init(host: str = "localhost", sock: socket = None):
    try:
        sock = sock or socket()
        sock.connect((host, port))
    except ConnectionRefusedError:
        print("Server fermé")
        exit()
    return sock
