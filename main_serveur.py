import socket
from threading import Thread
from multiprocessing import Process, Manager, Event, Semaphore, Value
from multiprocessing import Lock as mLock
from joueur_process import joueur_process     
from sysv_ipc import MessageQueue,IPC_CREAT
from fonction_serveur import *
        
#Début du programme qui lance le serveur
if __name__ == "__main__":
    nombre_joueurs = 0
    while nombre_joueurs < 2 or nombre_joueurs > 5:
        nombre_joueurs = int(input("Combien de joueurs (2 à 5) vont se connecter ?\n--> "))

#Ouverture de la socket et établissement de la connexion TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(input("port: "))
    server_socket.bind(('localhost', port))
    server_socket.listen(nombre_joueurs)
 
    

#Initialisation des variables partagées 
    mains = Manager().dict()
    tour = Value('I',1,lock=False)
    n_indices = nombre_joueurs + 3 #nombre de tokens d'informations (basic: nb_joueurs + 3)
    indices = Value('I',n_indices,lock=False)
    shared = mLock()
    sem = Semaphore(0)
    suites=Manager().dict()
    shared_memory = {"indices":indices,"mains":mains,"tour":tour,"shared":shared,"sem":sem,"suites":suites}

    synchro= Event()
    debut = Event()
    dic_mq = {}
    pioche = []
    erreurs = 3 #nombre de tokens d'erreurs (basic: 3)

#Création d'une messagequeue pour chacun des joueurs
    for i in range(1,nombre_joueurs+1):
        dic_mq[f"{i}"]=MessageQueue(i, IPC_CREAT)

#Création d'un thread pour gérer la création de la pioche et la distribution des cartes pendant que les joueurs se connectent (pour gagner du temps)
    thread_pioche = Thread(target=distribution,args=(nombre_joueurs,pioche,shared_memory))
    thread_pioche.start()

    #mains spéciales pour tester la gagne
    # couleurs = ["bleu","vert"]
    # for i in range(0,1):
    #         main_temp = []
    #         for j in range(1,5):
    #                 maintemp = (j,couleurs[i])
    #         shared_memory["mains"][f"joueur_{i+1}"]=maintemp
    #         print(f"Main de test :",shared_memory["mains"][f"joueur_{i+1}"])
                    

    c=1
    dic_joueurs = {}

#Attente de connexions de TOUS mes joueurs
    while c<=nombre_joueurs:
        print("En l'attente de joueurs...")
        client, addr = server_socket.accept()
        print(f"Joueur {c} connecté ({addr})")
        #Lancement des process joueurs associés à chaque client (socket)
        joueur = Process(target=joueur_process, args=(c,shared_memory, dic_mq,client,synchro,debut))
        joueur.start()
        dic_joueurs[f"joueur_{c}"] = {"client":client,"addresse":addr,"process":joueur} #dic gardant en mémoire les caractéristiques des clients 
        c+=1

    #On attend que la distribution du thread soit terminée
    thread_pioche.join()

    #Envoi de leur numéro de joueur aux clients pour signaler directement le début de la partie
    for i,lst in dic_joueurs.items():
        envoi_info(i[-1],lst["client"])

    #Event signalant aux process joueurs le début de la partie
    debut.set()

    #Lancement de la partie côté serveur
    #fin prend une valeur de fin (plus de fuse token ou tous les 5 posés)
    fin = main_server(shared_memory,pioche,dic_mq,erreurs,synchro)

#Gestion de fin de partie 
    fin_partie(shared_memory,dic_mq,fin,dic_joueurs)
    print("Fin du jeu. Merci à tous.tes.")

    #Fermeture des connexions client
    for joueur in dic_joueurs.keys():
        finsocket = dic_joueurs[joueur]["client"]
        finsocket.close()

    #Fermeture des mq
    for mq in dic_mq.values():
        mq.remove()
