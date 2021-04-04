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
    def __init__(self, username, password, autoConnect=False):
        self.username = username
        self.password = password
        self.token = None

        self.sock = init()

        if autoConnect:
            try:
                self.connect()
            except UserNotFoundError:
                self.reconnect()
                self.createUser()
                self.connect()

    def command(self, command, arg=None):
        return sendCommand(self.sock, command, [self.token, str(arg) if arg is not None else []])

    def connect(self):
        r = sendCommand(self.sock, "connect", [self.username, self.password])
        if not r:
            raise
        if r[0] == 1:
            self.token = r[1]
            print("Connected")
        elif r[0] == 2:
            raise UserNotFoundError(self)
        elif r[0] == 3:
            raise InvalidPasswordError(self)
    
    def createUser(self):
        r = sendCommand(self.sock, "createuser", [self.username, self.password])
        if r[0] == 1:
            print("User created")
        elif r[0] == 2:
            raise UserAlreadyExistError(self)

    def deleteUser(self):
        if not self.token:
            raise ClientDisconnectedError(self)
        r = self.command("deleteuser")
        print("aaaaaaaaaaaaaaaaa ", r)
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
        self.sock = init()

    def sendMessage(self, message):
        if not self.token:
            raise ClientDisconnectedError(self)
        print("Envoi du message...")
        r = self.command("message", message)
        if r == 1:
            print("Message envoyé !")
            print(self.username, ":", message)
        if r == 2:
            raise ClientDisconnectedError(self)
