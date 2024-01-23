import socket
import pickle
import threading
import time

def reception_info(chaussette):
    data = chaussette.recv(1024)
    decoded_data = data.decode("utf-8")
    return decoded_data

def envoi_info(data_str,chaussette):
    data = data_str.encode('utf-8')
    chaussette.send(data)


def client_program():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8000))  # Replace with your server details
    print("Connecté au serveur !")
    print("---------------------")
    print("En attente des autres joueurs...")

    client_socket.recv(1)
    print("TOUT LE MONDE EST CONNECTE")
    print("-------------------")

    """DEBUT DE TOUR CLIENT"""

    print("Voici votre jeu: ")
    print(pickle.loads(client_socket.recv(4096)))

    print("-------------------")
    while True:
        info_joueurs_codee = client_socket.recv(4096)
        info_joueurs = pickle.loads(info_joueurs_codee)
        if info_joueurs != pickle.dumps("STOP"):
            print(f"Main du joueur {info_joueurs[0]}:")
            print(f"{info_joueurs[1]}")
        else:
            break
    print("STOP")
    
    # Code pour demander la connexion, attendre les joueurs, etc.

    # while True:
    #     message = client_socket.recv(1024).decode()
    #     if not message:
    #         break

    #     # Traitement des messages selon le flag correspondant
    #     if message.startswith("GAME_STATE"):
    #         # Affichage de l'état du jeu
    #         print(message[11:])
    #     elif message.startswith("YOUR_TURN"):
    #         # C'est le tour du joueur
    #         user_action = input("Choisissez une action (indice/poser): ")
    #         client_socket.send(user_action.encode())


    client_socket.close()

if __name__ == "__main__":
    client_program()
