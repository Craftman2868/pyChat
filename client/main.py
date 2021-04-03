from client import Client

client = Client("test", "1234")

client.sendMessage("salut")

client.disconnect()

client.close()
