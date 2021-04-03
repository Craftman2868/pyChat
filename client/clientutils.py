from socket import socket


class CommandNotFound(Exception):
    pass


port = 1313

commands = ["connect", "message", "disconnect"]


def sendCommand(sock: socket, command: str, arg=[]):
    if command not in commands:
        raise CommandNotFound("Command '" + command + "' not found")
    command = commands.index(command)
    if type(arg) == str:
        arg = arg.encode()
    elif type(arg) == int:
        arg = [arg]
    elif type(arg) == list:
        for i, a in enumerate(arg):
            if type(a) == str:
                arg[i] = a.encode()
        arg = b";".join(arg)
    sock.send(bytearray([command, *arg]))
    print("En attente de réponse...")
    r = sock.recv(1024)
    print("Réponse reçue:", r)
    if not r:
        return 0,
    return int(r[0]), r[1:]


def init(host: str = "localhost", sock: socket = None):
    sock = sock or socket()
    sock.connect((host, port))
    return sock
