import multiprocessing
import time

def joueur_process(shared_memory, message_queue, s):
    print("joueur process")
    while False:
        # Consulte la shared memory et envoie l'état du jeu au client
        # Attente sur la message queue pour les actions du joueur
        # Envoi des messages sur l'action réalisée au client
        # Attente du signal de lancement du tour suivant
        pass

