from socket import socket
from random import randint
from json import load, dump
from hashlib import md5
from time import time, sleep

EXPIRATION_TIME = 10

tokens = {}


def randbytes(n: int = 1):
    b = bytearray()
    for _ in range(n):
        b.append(randint(0, 255))
    return bytes(b)


def removeExpiredTokens():
    for token, (_, _, expirationTime) in tokens.copy().items():
        if expirationTime <= time():
            del tokens[token]


def generateId():
    with open("lastId", "+") as f:
        id = int(f.read()) + 1
        f.write(str(id))
        return id


def generateToken(userId, ip):
    token = b";"
    while b";" in token:
        token = randbytes(16)
    tokens[token] = [userId, ip, time() + (EXPIRATION_TIME * 60)]
    return token


def createUser(username: str, password: str):
    user = {
        "id": generateId(),
        "username": username,
        "passwosrd": md5(password.encode()).hexdigest()
    }
    with open("users.json", "r") as f:
        data = load(f)
    data.append(user)
    with open("users.json", "w") as f:
        dump(data, f)


def getUser(*, username=None, userId=None, token=None):
    if token:
        print(type(list(tokens.keys())[0]), type(token))
        return getUser(userId=tokens[token][2])
    if not username and not userId:
        return
    with open("users.json", "r") as f:
        data = load(f)
    for u in data:
        if u["username"] == username or u["id"] == userId:
            return u


def connect(username, password, ip):
    user = getUser(username=username)
    if not user:
        return [1]  # User not found
    if md5(password.encode()).hexdigest() != user["password"]:
        return [2]  # Invalid password
    return [0, *generateToken(user["id"], ip)]  # Return token


def disconnect(token):
    if token not in tokens:
        return [1]
    del tokens[token]
    return [0]


def send(token, message):
    print(getUser(token=token), ":", message)
    sleep(1)
    return [1]


commands = [connect, send, disconnect]

host = ""
port = 1313

sock = socket()

try:
    sock.bind((host, port))

    print("Serveur lancé")

    launched = True

    sock.listen()

    conn, addr = sock.accept()

    while launched:

        removeExpiredTokens()

        data = conn.recv(1024)

        if data:
            commandId = int(data[0])
            command = commands[commandId]
            args = data[1:]

            print(args)

            if command == connect:
                args = args.decode().split(";")
                r = command(*args, addr[0])
            else:
                args = args.split(b";")
                args[1] = args[1].decode()
                r = command(*args)

            print(r)
            conn.send(bytearray(r))
            print("Réponse envoyé !")

finally:
    sock.close()
