import socket
import pickle
import threading
import time
from test import affichecarte,affichemain


def reception_info(chaussette):
    res_code = chaussette.recv(1024)
    res = res_code.decode("utf-8")
    return res

def envoi_info(data_brut,chaussette):
    if chaussette.recv(1024).decode("utf-8") == "demande":
        if type(data_brut) != bytes:
            data = data_brut
            chaussette.send(data.encode("utf-8"))
        else:
            chaussette.send(data_brut)
    else:
        print("PROBLEME SYNCHRO ENVOI/RECEPTION")

def mon_tour(s):
    print("C'est ton tour !")
    token_info = int(reception_info(s))
    if token_info>0:
        choix = input("Que veux-tu faire ? (indice/poser)")
        envoi_info(choix,s)
        if choix == "indice":
            joueur = input("Sur la main de quel joueur veux-tu donner une info ?")
            info = input("Ecrire l'info à partager (une couleur/un nombre): ")
            print("---------------------------------")
            envoi_info(joueur,s)
            envoi_info(info,s)
        else:
            carte_choisie = input("Quelle est la carte que vous souhaitez poser (Choisir un entier entre 1 et 5):")
            envoi_info(carte_choisie,s)
    else:
        envoi_info("poser",s)
        carte_choisie = input("Vous n'avez plus de jetons d'information, veuillez choisir une carte à poser (entier entre 1 et 5)")
        envoi_info(carte_choisie,s)
    print("FIN DU TOUR")
    print("---------------------------------")

def pas_mon_tour(s):
    print("Ce n'est pas ton tour, en attente d'actions d'autres joueurs...")
    affichage_info = reception_info(s)
    print(affichage_info)


def client_program():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8000)) 
    print("Connecté au serveur !")
    print("---------------------")
    print("En attente des autres joueurs...")

    num_joueur = reception_info(client_socket)
    print("TOUT LE MONDE EST CONNECTE")
    print("VOUS ETES LE JOUEUR",num_joueur)
    print("-------------------")

    """DEBUT DE TOUR CLIENT"""

    print("Voici votre jeu: ")
    affichemain(pickle.loads(client_socket.recv(4096)))

    print("-------------------")
    nb_joueurs_exclu = int.from_bytes(client_socket.recv(1), byteorder='big')
    
    #Reception des mains des autres joueurs
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
            affichemain(info_joueurs[1])
        c += 1
    
    print("fin envoi mains")

    #RECEPTION ETAT DES SUITES

    suites = pickle.loads(client_socket.recv(4096))
    print("Etat actuel des suites:")
    affichemain(suites)

####################################################################################


    while True:
        tour = int(reception_info(client_socket))
        print(tour,num_joueur)
        if  int(tour) == int(num_joueur):
            mon_tour(client_socket)

        

        else:
            pas_mon_tour(client_socket)
            pass
        
        break
    
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


if __name__ == "__main__":
    client_program()

 