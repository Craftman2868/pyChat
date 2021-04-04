from socket import socket
from random import randint
from json import load, dump
from hashlib import md5
from time import time
from threading import Thread

EXPIRATION_TIME = 10  # en minutes


def randbytes(n: int = 1):
    b = bytearray()
    for _ in range(n):
        b.append(randint(0, 255))
    return bytes(b)


def removeExpiredTokens():
    for token, (user, _, expirationTime) in tokens.copy().items():
        if expirationTime <= time():
            del tokens[token]
            print(f"Token for '{getUser(userId=user)}' user deleted")


def generateId():
    with open("users.json", "r") as f:
        data = load(f)
    data["lastId"] += 1
    with open("users.json", "w") as f:
        dump(data, f)
    return data["lastId"]


def generateToken(userId, ip):
    token = b";"
    while b";" in token or token in tokens:
        token = randbytes(16)
    tokens[token] = [userId, ip, time() + (EXPIRATION_TIME * 60)]
    return token


def createUser(username: str, password: str):
    print(f"Creating '{username}' user...")
    with open("users.json", "r") as f:
        data = load(f)
    for u in data["users"]:
        if username == u["username"]:
            print("User already exist")
            return 2,
    user = {
        "id": generateId(),
        "username": username,
        "password": md5(password.encode()).hexdigest()
    }
    data["users"].append(user)
    with open("users.json", "w") as f:
        dump(data, f, indent=4)
    print("User created")
    return 1,


def getUser(*, username=None, userId=None, token=None):
    if token:
        return getUser(userId=tokens[token][0])
    if username is None and userId is None:
        return
    with open("users.json", "r") as f:
        data = load(f)
    for u in data["users"]:
        if u["username"] == username or u["id"] == userId:
            return u


def connect(username, password, ip):
    print(f"{ip}: connecting...")
    user = getUser(username=username)
    if not user:
        print(f"User '{username}' not found")
        return 2,  # User not found
    if md5(password.encode()).hexdigest() != user["password"]:
        print("Invalid password")
        return 3,  # Invalid password
    print("Client connected")
    return 1, *generateToken(user["id"], ip)  # Return token


def disconnect(token):
    if token not in tokens:
        return 2,
    print(f"{tokens[token][1]}: client disconnected")
    del tokens[token]
    return -1,


def send(token, message):
    if token not in tokens:
        return 2,
    print(getUser(token=token)["username"], ":", message)
    return 1,


def deleteUser(token):
    if token not in tokens:
        return 2,
    u = getUser(token=token)
    if not u:
        return 3,
    print(f"Deleting '{u['username']}' user...")
    with open("users.json", "r") as f:
        data = load(f)
    data["users"].remove(u)
    with open("users.json", "w") as f:
        dump(data, f, indent=4)
    print("User deleted")
    return -1,


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
            elif command == createUser:
                args = args.decode().split(";")
                r = command(*args)
            else:
                args = args.split(b";")
                if len(args) > 1:
                    args[1] = args[1].decode()
                r = command(*args)

            if r[0] != 1:
                if r == (-1,):
                    r = 1,
                conn.send(bytearray(r))
                break

            conn.send(bytearray(r))
    conn.close()


commands = [connect, send, disconnect, createUser, deleteUser]

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
