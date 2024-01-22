import multiprocessing
import time

def reception_info(chaussette):
    data = chaussette.recv(1024)
    decoded_data = data.decode("utf-8")
    return decoded_data

def envoi_info(data_str,chaussette):
    data = data_str.encode('utf-8')
    chaussette.send(data)

def joueur_process(shared_memory, message_queue, s,synchro):
    print("joueur process waiting")
    synchro.wait()

    while False:
        # Consulte la shared memory et envoie l'état du jeu au client
        # Attente sur la message queue pour les actions du joueur
        # Envoi des messages sur l'action réalisée au client
        # Attente du signal de lancement du tour suivant
        pass

