from clientutils import init, sendCommand


class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

        self.sock = init()

        self.connect()

    def command(self, command, arg=None):
        return sendCommand(self.sock, command, [self.token, str(arg) if arg is not None else []])

    def connect(self):
        r = sendCommand(self.sock, "connect", [self.username, self.password])
        if r[0] == 1:
            self.token = r[1]
            print("Connected")
        elif r[0] == 2:
            print("User not found")
        elif r[0] == 3:
            print("Invalid password")

    def disconnect(self):
        r = self.command("disconnect")
        if r:
            pass

    def close(self):
        self.sock.close()

    def sendMessage(self, message):
        print("Envoi du message...")
        r = self.command("message", message)
        if r:
            print("Message envoyé !")
            print(self.username, ":", message)
