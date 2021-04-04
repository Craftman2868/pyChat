from client import Client

client = Client(username="test", password="1234")

client.connect()

msg = ""
print("Entrez 'quit' pour quitter")
while msg.lower() != "quit":
    msg = input(client.username+" : ")
    client.sendMessage(msg)

client.disconnect()
