from socket import socket
from random import randint
from json import load, dump
from hashlib import md5
from time import time, sleep
from threading import Thread

EXPIRATION_TIME = 10  # en minutes


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
    while b";" in token or token in tokens:
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
        return getUser(userId=tokens[token][0])
    if username is None and userId is None:
        print("ok")
        return
    with open("users.json", "r") as f:
        data = load(f)
    for u in data:
        if u["username"] == username or u["id"] == userId:
            return u


def connect(username, password, ip):
    user = getUser(username=username)
    if not user:
        print("User not found")
        return 2,  # User not found
    if md5(password.encode()).hexdigest() != user["password"]:
        print("Invalid password")
        return 3,  # Invalid password
    print("Client connected")
    return 1, *generateToken(user["id"], ip)  # Return token


def disconnect(token):
    if token not in tokens:
        return 2,
    del tokens[token]
    print("Client disconnected")
    return -1,


def send(token, message):
    print(getUser(token=token)["username"], ":", message)
    sleep(1)
    return 1,


def clientThread(conn, addr):
    while True:
        data = conn.recv(1024)

        if data:
            commandId = int(data[0])
            command = commands[commandId]
            args = data[1:]

            if command == connect:
                args = args.decode().split(";")
                r = command(*args, addr[0])
            else:
                args = args.split(b";")
                if len(args) > 1:
                    args[1] = args[1].decode()
                r = command(*args)

            if r == (-1,):
                conn.send(bytearray(1))
                break

            conn.send(bytearray(r))
    conn.close()


commands = [connect, send, disconnect]

threads = []
tokens = {}

host = ""
port = 1313

sock = socket()

try:
    sock.bind((host, port))

    sock.listen()

    print("Serveur lancé")

    launched = True

    while launched:
        conn, addr = sock.accept()

        removeExpiredTokens()

        threads.append(Thread(target=lambda: clientThread(conn, addr)))
        threads[-1].run()

finally:
    sock.close()
