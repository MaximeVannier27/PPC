import socket
import pickle #module permettant un échange simple de liste à travers les sockets tcp (désérialisation automatique  des listes)
import sys
from os import system
from affichage import affichemain

#FONCTIONS D'ENVOI ET DE RECEPTION DES DONNEES ENTRE CLIENT/SERVEUR
def reception_info(socket):
    res_code = socket.recv(1024)
    res = res_code.decode()

    return res

def envoi_info(data_brut,socket):
    if type(data_brut) != bytes:
        data = data_brut
        socket.send(data.encode())
    else:
        socket.send(data_brut)


#FONCTIONS PERMETTANT DE SYNCHRONISER LES ECHANGES TCP CLIENT/SERVEUR -> éviter le surchargement des buffers  
def demande_from_serveur(socket):
    socket.recv(1024)

def demande_to_serveur(socket):
    demande_to_client = "demande"
    socket.send(demande_to_client.encode())



def mon_tour(socket):
#Vérification si la demande de choix est possible (envoyé par le process serveur en fonction de la présence ou non de token d'informations)
    print("\033[1m-----------------------\033[0mC'est ton tour !\033[1m-----------------------\033[0m")
    demande_to_serveur(socket)
    possibilité_choix = reception_info(socket)

#Disjonction de cas en fonction de la possibilité du choix
    if possibilité_choix == "possible":

#Demande de choix au client: donner un INDICE ou POSER une carte
        demande_from_serveur(socket)
        choix =""
        while choix not in ["indice","poser"]:
            choix = input("Que veux-tu faire ? \033[3m(indice/poser)\033[0m\nreponse> ")

        envoi_info(choix,socket)
#Disjonction de cas en fonction du choix 
        if choix == "indice":
            demande_from_serveur(socket)
            joueur = input("Sur la main de quel joueur veux-tu donner une info ?\nreponse> ")
            envoi_info(joueur,socket)
            demande_from_serveur(socket)
            info = "0"
            while info not in ["1","2","3","4","5","rouge","vert","bleu","jaune","violet"]:
                info = input("Ecrire l'info à partager \033[3m(une couleur/un nombre)\033[0m\nreponse> ") 
            envoi_info(info,socket)
        else:
            demande_from_serveur(socket)
            carte_choisie = "0"
            while int(carte_choisie) >5 or int(carte_choisie) <1:
                carte_choisie = input("Quelle est la carte que vous souhaitez poser (Choisir un entier entre 1 et 5)\nreponse> ")
            envoi_info(carte_choisie,socket)
            demande_to_serveur(socket)
            print(reception_info(socket))
    else:

#Si plus de token d'informations, le choix de poser une carte est forcé
        demande_from_serveur(socket)
        carte_choisie = "0"
        while int(carte_choisie) >5 or int(carte_choisie) <1:
            carte_choisie = input("Vous n'avez plus de jetons d'information, veuillez choisir une carte à poser (entier entre 1 et 5)\nreponse> ")
        envoi_info(carte_choisie,socket)
        demande_to_serveur(socket)
#Affichage du résultat de la pose (réussite ou échec en fonction de l'état des suites)
        print(reception_info(socket))
    print("=============================\n\tFIN DU TOUR\n=============================")

def pas_mon_tour(socket):
    demande_to_serveur(socket)
    print("\033[3mCe n'est pas ton tour, en attente d'actions d'autres joueurs...\033[0m")
    affichage_info = reception_info(socket)
    print(affichage_info)
    print("=============================\n\tFIN DU TOUR\n=============================")

def reception_mains_suites(client_socket):
#Reception de la main du joueur (formatée en fonction des informations données pendant la partie) + test si fin de partie 
    main_perso = client_socket.recv(4096)
    try:
        main_perso_decode = pickle.loads(main_perso)
        print("\033[1mVoici votre jeu: \033[0m")
        print("---------------")
        affichemain(main_perso_decode)
    except pickle.UnpicklingError:
        print(main_perso.decode())
        sys.exit()
    print("---------------")
    print('\n')

    nb_joueurs = int.from_bytes(client_socket.recv(1), byteorder='big')
    
#Reception des mains des autres joueurs en fonction
    c = 1
    while c < nb_joueurs:
#Reception de la taille du message pour plus de stabilité à la reception
        taille_info = int.from_bytes(client_socket.recv(4), byteorder='big')
    
#Reception des données
        info_joueurs_codee = b""
        while len(info_joueurs_codee) < taille_info:
            chunk = client_socket.recv(min(4096, taille_info - len(info_joueurs_codee)))
            if not chunk:
                # Gérer une éventuelle fermeture de la connexion en cas de problème
                break
            info_joueurs_codee += chunk
    
        if len(info_joueurs_codee) == taille_info:
            # Désérialiser les données
            info_joueurs = pickle.loads(info_joueurs_codee)
            
            # Afficher les informations
            print(f"Main du joueur \033[1m{info_joueurs[0]}\033[0m:")
            affichemain(info_joueurs[1])
            print('\n')
        c += 1

#Reception de l'état courant des suites
    suites = pickle.loads(client_socket.recv(4096))
    print("Etat actuel des suites:")
    affichemain(suites)

def client_program():
#Initialisation de la connexion avec le serveur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(input("port: "))
    client_socket.connect(('localhost', port)) 
    print("Connecté au serveur !")
    print("===================================")
    print("En attente des autres joueurs...")

#Signal annonçant le début du jeu quand tous les joueurs sont connectés + reception du numéro de joueur courant
    num_joueur = int(reception_info(client_socket))
    system('clear')
    print("TOUT LE MONDE EST CONNECTE")
    print("\033[1mVOUS ETES LE JOUEUR",num_joueur,"\033[0m")
    print("-------------------")

#Boucle de jeu principal côté client
    while True:
        demande_to_serveur(client_socket)
        reception_mains_suites(client_socket)
        print('\n')

#Lancement de la fonction adaptée en fonction de quel joueur dois jouer
        demande_to_serveur(client_socket)
        tour = int(reception_info(client_socket))
        if tour == num_joueur:
            mon_tour(client_socket)
        else:
            pas_mon_tour(client_socket)

#Garde-fou client
if __name__ == "__main__":
    client_program()

 
