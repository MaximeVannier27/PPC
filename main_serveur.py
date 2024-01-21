import socket
import threading
import multiprocessing
from joueur_process import joueur_process
from fonction_serveur import main_server







if __name__ == "__main__":

    nombre_joueurs = int(input("Combien de joueurs vont se connecter ?\n--> "))
    dic_joueurs = {}

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen(nombre_joueurs)

    shared_memory = multiprocessing.Manager().dict()
    message_queue = multiprocessing.Queue()

    c=1

    while c<=nombre_joueurs:

        client, addr = server_socket.accept()
        print(f"Joueur {c} connecté ({addr})")
        joueur = multiprocessing.Process(target=joueur_process, args=(shared_memory, message_queue,client))
        joueur.start()
        dic_joueurs[f"joueur_{c}"] = joueur
        c+=1
    main_server()
    server_socket.close()
