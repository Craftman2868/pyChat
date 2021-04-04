from client import Client

client = Client("test", "1234")

client.connect()

client.sendMessage("salut")

client.disconnect()
