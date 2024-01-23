import socket
from threading import Lock,Thread
from multiprocessing import Process, Manager, Value
from multiprocessing Lock as mLock
from joueur_process import joueur_process
from fonction_serveur import main_server, distribution,piocheCarte
import threading      
from sysv_ipc import MessageQueue,IPC_CREAT
     
    
    

if __name__ == "__main__":

    nombre_joueurs = int(input("Combien de joueurs vont se connecter ?\n--> "))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen(nombre_joueurs)

    #initialisation des variables
    mains = Manager().dict()
    tour = Value('I',(1,),lock=False)
    n_indices = nombre_joueurs + 3
    indices = Value('I',(n_indices,),lock=False)
    shared_memory = {"indices":indices,"mains":mains,"tour":tour}
    
    erreurs = 3 
    dic_mq = {}
    for i in range(1,nombre_joueurs+1):
        dic_mq[f"{i}"]=MessageQueue(i, sysv_ipc.IPC_CREAT)

    thread_pioche = Thread(target=distribution,args=(nombre_joueurs,))
    thread_pioche.start()
    c=1
    dic_joueurs = {}
    while c<=nombre_joueurs:
        print("En l'attente de joueurs...")
        client, addr = server_socket.accept()
        print(f"Joueur {c} connecté ({addr})")
        joueur = Process(target=joueur_process, args=(c,shared_memory, dic_mq,client,synchro))
        joueur.start()
        dic_joueurs[f"joueur_{c}"] = {"client":client,"addresse":addr,"process":joueur}
        
        c+=1
    thread_pioche.join()

    

    #envoi d'un bit pour signaler le début de la partie
    for _,lst in dic_joueurs.items():
          lst["client"].sendall(b'\x01')
    


    main_server()
    server_socket.close()
