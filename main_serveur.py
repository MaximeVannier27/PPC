import socket
from threading import Lock,Thread
from multiprocessing import Process, Manager, Event, Semaphore, Value
from multiprocessing import Lock as mLock
from joueur_process import joueur_process
from fonction_serveur import main_server, distribution
import threading      
from sysv_ipc import MessageQueue,IPC_CREAT
import signal
import time
from fonction_serveur import *

def handler(sig,frame):
    if sig == signal.SIGUSR1:
        process = os.getpid()
        print(f"Destruction du process client {process}")
        os.kill(os.getpid(),signal.SIGKILL)

if __name__ == "__main__":

    nombre_joueurs = int(input("Combien de joueurs vont se connecter ?\n--> "))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen(nombre_joueurs)

    #initialisation du handler de fin de partie
    signal.signal(signal.SIGUSR1, handler)

    #initialisation des variables
    mains = Manager().dict()
    tour = Value('I',1,lock=False)
    n_indices = nombre_joueurs + 3
    indices = Value('I',n_indices,lock=False)
    shared = mLock()
    sem = Semaphore(0)
    suites=Manager().dict()
    shared_memory = {"indices":indices,"mains":mains,"tour":tour,"shared":shared,"sem":sem,"suites":suites}

    synchro= Event()
    dic_mq = {}
    pioche = []
    erreurs = 3 

    #création d'une messagequeue pour chacun des joueurs
    for i in range(1,nombre_joueurs+1):
        dic_mq[f"{i}"]=MessageQueue(i, IPC_CREAT)

    #création d'un thread pour gérer la création de la pioche et la distribution des cartes pendant qu'ils se connectent
    thread_pioche = Thread(target=distribution,args=(nombre_joueurs,pioche,shared_memory))
    thread_pioche.start()

    c=1
    dic_joueurs = {}

    #connexion des joueurs
    while c<=nombre_joueurs:
        print("En l'attente de joueurs...")
        client, addr = server_socket.accept()
        print(f"Joueur {c} connecté ({addr})")
        joueur = Process(target=joueur_process, args=(c,shared_memory, dic_mq,client,synchro))
        joueur.start()
        dic_joueurs[f"joueur_{c}"] = {"client":client,"addresse":addr,"process":joueur}
        c+=1

    #on attend que la distribution soit terminée
    thread_pioche.join()

    #envoi d'un bit pour signaler le début de la partie directement aux sockets clients
    for i,lst in dic_joueurs.items():
          lst["client"].sendall(i[-1].encode('utf-8'))

    #Event signalant aux process joueurs le début de la partie
    synchro.set()

    #lancement de la partie côté serveur
    main_server(shared_memory,pioche,dic_mq,erreurs,synchro)

    #fermeture des connexions client
    for joueur in dic_joueurs:
        joueur["client"].close()

    #fermeture des mq
    for mq in dic_mq.values():
        mq.remove()
