from socket import socket
from random import randint
from json import load, dump
from hashlib import md5
from time import time
from threading import Thread
from traceback import print_exc

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
            print(f"Token for '{getUser(userId=user)['username']}' user deleted")


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
        "id": data["lastId"],
        "username": username,
        "password": md5(password.encode()).hexdigest(),
        "lastMsg": -1
    }
    data["users"].append(user)
    data["lastId"] += 1
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


def createMessage(user, message):
    with open("messages.json", "r") as f:
        data = load(f)
    id = len(data["messages"])
    data["messages"].append([user["id"], message])
    with open("messages.json", "w") as f:
        dump(data, f, indent=4)

    with open("users.json", "r") as f:
        data = load(f)

    for i, u in enumerate(data["users"]):
        if u["lastMsg"] == -1:
            data["users"][i]["lastMsg"] = id

    with open("users.json", "w") as f:
        dump(data, f, indent=4)

    return id


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


def send(token, *message):
    message = ";".join((m.decode() if type(m) == bytes else m) for m in message)
    if token not in tokens:
        return 2,
    u = getUser(token=token)
    createMessage(u, message)
    print(getUser(token=token)["username"], ":", message)
    return 1,


def deleteUser(token):
    if token not in tokens:
        return 2,
    u = getUser(token=token)
    print(f"Deleting '{u['username']}' user...")
    with open("users.json", "r") as f:
        data = load(f)
    data["users"].remove(u)
    with open("users.json", "w") as f:
        dump(data, f, indent=4)
    print("User deleted")
    return -1,


def getMessages(token):
    if token not in tokens:
        return 2,
    u = getUser(token=token)
    with open("messages.json", "r") as f:
        messages = load(f)["messages"]
    messages = messages[u["lastMsg"]:]
    for i, m in enumerate(messages):
        if m[0] == u["id"]:
            del messages[i]
    u["lastMsg"] = -1
    with open("users.json", "r") as f:
        data = load(f)
    for i, user in enumerate(data["users"]):
        if user["id"] == u["id"]:
            data["users"][i] = u
    with open("users.json", "w") as f:
        dump(data, f, indent=4)
    if not messages:
        return 4,
    else:
        messages = (getUser(userId=m[0])["username"]+" : "+m[1] for m in messages)
        return 1, *";".join(messages).encode()


def clientThread(conn, addr):
    data = None
    try:
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
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Error:")
        print("  Ip       : "+addr[0])
        print("  Type     : "+e.__class__.__qualname__)
        print("  Args     : "+", ".join(str(a) for a in e.args))
        print("  Locals   :")
        for n, v in locals().items():
            if n in ["e", "addr", "conn"]:
                continue
            print("    "+n+" = "+repr(v))
        print_exc()
    finally:
        conn.close()


commands = [connect, send, disconnect, createUser, deleteUser, getMessages]

tokens = {}

host = ""
port = 1313

sock = socket()

try:
    sock.bind((host, port))

    print("Serveur launched")

    launched = True

    while launched:
        sock.listen(5)

        conn, addr = sock.accept()

        removeExpiredTokens()

        Thread(target=lambda: clientThread(conn, addr)).start()

finally:
    sock.close()
