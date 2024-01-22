import socket
from threading import Lock
from multiprocessing import Process, Manager, Queue, Event
from joueur_process import joueur_process
from fonction_serveur import main_server


if __name__ == "__main__":

    nombre_joueurs = int(input("Combien de joueurs vont se connecter ?\n--> "))
    dic_joueurs = {}

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen(nombre_joueurs)

    shared_memory = Manager().dict()
    message_queue = Queue()
    synchro = Event()

    c=1

    while c<=nombre_joueurs:
        print("En l'attente de joueurs...")
        client, addr = server_socket.accept()
        print(f"Joueur {c} connecté ({addr})")
        joueur = Process(target=joueur_process, args=(shared_memory, message_queue,client,synchro))
        joueur.start()
        dic_joueurs[f"joueur_{c}"] = {"client":client,"addresse":addr,"process":joueur}
        c+=1
    for _,lst in dic_joueurs.items():
          lst["client"].sendall(b'\x01')
    synchro.set()
    main_server()

    
    server_socket.close()
