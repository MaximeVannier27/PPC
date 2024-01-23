import socket
import pickle
import threading
import time

def reception_info(chaussette):
    data = chaussette.recv(1024)
    decoded_data = data.decode("utf-8")
    return decoded_data

def envoi_info(data_brut,chaussette):
    if type(data_brut) != bytes:
        data = data_brut.encode('utf-8')
        chaussette.send(data)
    else:
        chaussette.send(data_brut)


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
    nb_joueurs_exclu = int.from_bytes(client_socket.recv(1), byteorder='big')
    

    c = 1
    while c < nb_joueurs_exclu:
        # Recevoir la taille du message
        taille_info = int.from_bytes(client_socket.recv(4), byteorder='big')
    
        # Recevoir les données
        info_joueurs_codee = b""
        while len(info_joueurs_codee) < taille_info:
            chunk = client_socket.recv(min(4096, taille_info - len(info_joueurs_codee)))
            if not chunk:
                # Gérer une éventuelle fermeture de la connexion
                break
            info_joueurs_codee += chunk
    
        if len(info_joueurs_codee) == taille_info:
            # Désérialiser les données
            info_joueurs = pickle.loads(info_joueurs_codee)
            
            # Afficher les informations
            print(f"Main du joueur {info_joueurs[0]}:")
            print(f"{info_joueurs[1]}")
        
        c += 1
    print("fin envoi mains")
    
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

 