from clientutils import init, sendCommand


class UserNotFoundError(Exception):
    def __init__(self, client):
        self.args = f"User '{client.username}' not found",
        client.close()


class UserAlreadyExistError(Exception):
    def __init__(self, client):
        self.args = f"User '{client.username}' already exist",
        client.close()


class InvalidPasswordError(Exception):
    def __init__(self, client):
        self.args = "Invalid password",
        client.close()


class ClientDisconnectedError(Exception):
    def __init__(self, client):
        self.args = "Client disconnected",
        client.close()


class ClientAlreadyDisconnectedError(ClientDisconnectedError):
    def __init__(self, client):
        self.args = "Client already disconnected",
        client.close()


class Client:
    def __init__(self, username, password, host="localhost"):
        self.username = username
        self.password = password
        self.token = None
        self.host = host

        self.sock = init(self.host)

    def command(self, command, arg=None):
        try:
            return sendCommand(self.sock, command, [self.token, str(arg) if arg is not None else []])
        except:
            raise ClientDisconnectedError(self)

    def connect(self):
        r = sendCommand(self.sock, "connect", [self.username, self.password])
        if not r:
            raise
        if r[0] == 1:
            self.token = r[1]
        elif r[0] == 2:
            raise UserNotFoundError(self)
        elif r[0] == 3:
            raise InvalidPasswordError(self)
    
    def createUser(self):
        r = sendCommand(self.sock, "createuser", [self.username, self.password])
        if r[0] == 2:
            raise UserAlreadyExistError(self)

    def deleteUser(self):
        if not self.token:
            raise ClientDisconnectedError(self)
        r = self.command("deleteuser")
        if r == (1,):
            self.token = None
        if r == (2,):
            raise ClientDisconnectedError(self)

    def disconnect(self):
        if not self.token:
            raise ClientAlreadyDisconnectedError(self)
        r = self.command("disconnect")
        if r == 1:
            self.token = None
        self.close()

    def close(self):
        self.sock.close()

    def reconnect(self):
        self.close()
        self.sock = init(self.host)

    def sendMessage(self, message):
        if not self.token:
            raise ClientDisconnectedError(self)
        r = self.command("message", message)
        if r == (1,):
            print("Message envoyé !")
        if r == (2,):
            raise ClientDisconnectedError(self)

    def getMessages(self):
        r = self.command("getmessages")
        print(r)
        if r[0] == 1:
            r = r[1:]
            r = b"".join(r)
            r = r.decode()
            r = r.split(";")
            return r
        if r == (2,):
            raise ClientDisconnectedError(self)
        if r == (3,):
            return []
