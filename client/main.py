from client import Client, \
    InvalidPasswordError, UserNotFoundError, UserAlreadyExistError, ClientDisconnectedError, \
    ClientAlreadyDisconnectedError
from socket import gethostbyname, gaierror
from sys import exit

WELCOME_MESSAGE = "Bienvenue sur PyChat 0.0.1 !"


def askYesNo(question: str):
    question = str(question).strip()
    response = "a"
    while response not in "yn":
        response = input(question + " (Y/N): ").lower()
        if response == "":
            response = "a"
    return response == "y"


def menu(*choices):
    print("Menu:")
    for i, c in enumerate(choices):
        print(f"    {i + 1}.{c}")
    response = "a"
    while response not in (str(c) for c in range(1, len(choices) + 1)):
        response = input(f"Que voulez-vous faire ? (de 1 à {len(choices)}): ")
        if response == "":
            response = "a"
    return int(response)


print(WELCOME_MESSAGE + "\n")

client = None
try:
    while True:
        client = None
        host = ""
        while True:
            host = input("Quel est l'adresse du server (par défaut l'adresse local) ? ")
            if host == "":
                host = "127.0.0.1"
                break
            try:
                host = gethostbyname(host)
            except gaierror:
                print("Adresse incorrecte")
            else:
                break

        if askYesNo("Avez vous un compte ?"):
            while True:
                username = input("Nom d'utilisateur > ")
                password = input("Mot de passe > ")
                client = Client(username, password, host)

                print("Connexion...")
                try:
                    client.connect()
                except InvalidPasswordError:
                    print("Mot de passe invalide")
                    continue
                except UserNotFoundError:
                    print("Utilisateur introuvable")
                    continue
                print("Connecté !")
                break
        else:
            print("Pour continuer vous devez créer un compte")
            if not askYesNo("Voulez-vous continuer ?"):
                break

            while True:
                username = input("Nom d'utilisateur > ")
                password = input("Mot de passe > ")

                client = Client(username, password, host)

                print("Création du compte...")
                try:
                    client.createUser()
                except UserAlreadyExistError:
                    print("Un utilisateur avec le pseudo existe déjà")
                    continue
                print("Compte créé !")
                break

            print("Connexion...")
            client.connect()
            print("Connecté !")

        while True:
            action = menu("supprimer le compte", "envoyer des message", "se déconnecter")

            if action == 1:
                if askYesNo("Voulez-vous vraiment supprimer votre compte (Cette action est irréversible) ?"):
                    try:
                        client.deleteUser()
                    except ClientDisconnectedError:
                        client.connect()
                        client.deleteUser()
                    break
            elif action == 2:
                msg = ""
                print("Entrez 'quit' pour quitter")
                while True:
                    try:
                        messages = client.getMessages()
                    except ClientDisconnectedError:
                        client.reconnect()
                        client.connect()
                        messages = client.getMessages()
                    for m in messages:
                        print(m)
                    try:
                        msg = input(client.username + " : ")
                        if msg == "quit":
                            print("------------------------------")
                            break
                        if msg.strip() == "":
                            print("------------------------------")
                            continue
                        client.sendMessage(msg.strip())
                    except ClientDisconnectedError:
                        client.reconnect()
                        client.connect()
                        client.sendMessage(msg)
            else:
                print("Déconnexion...")
                try:
                    client.disconnect()
                except ClientDisconnectedError:
                    print("Déjà déconnecté")
                else:
                    print("Déconnecté !")
                break

        while True:
            if askYesNo("Voulez-vous vous connecter à un autre compte ?"):
                print("------------------------------")
                break
            else:
                exit()
except SystemExit:
    pass
except KeyboardInterrupt:
    if client:
        try:
            client.disconnect()
        except ClientDisconnectedError:
            pass
except:
    if client:
        try:
            client.disconnect()
        except ClientDisconnectedError:
            pass
    raise

print("Au revoir")
