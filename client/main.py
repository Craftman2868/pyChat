from client import Client

client = Client("test", "1234", False)

client.connect()

client.sendMessage("salut")

client.disconnect()
