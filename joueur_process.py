from multiprocessing import Value,Event
import time
import pickle

from ast import literal_eval as ev
import signal
import os
from main_serveur import handler



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

def decodet(message):
    """
    Permet de récuper directement un tuple à partir des données reçue dans la messagequeue
    """
    return ev(message.decode())


def envoi_mains(num_joueur,shared_memory_dic,s):
    
    global main_actuelle
    global connaissance

    """ATTENTION AUX CLES DES SHARED MEMORY"""
    #shared_memory_dic["shared"].acquire()
    main_actuelle = shared_memory_dic["mains"][f"joueur_{num_joueur}"]
    main_client = []

    for i in range(len(main_actuelle)):
        if not connaissance[i][0] and not connaissance[i][1]:
            main_client.append(("?","?"))
        if connaissance[i][0] and not connaissance[i][1]:
            main_client.append((main_actuelle[i][0],"?"))
        if not connaissance[i][0] and connaissance[i][1]:
            main_client.append(("?",main_actuelle[i][1]))
        if connaissance[i][0] and connaissance[i][1]:
            main_client.append((main_actuelle[i][0],main_actuelle[i][1]))
    
# envoi de la main actuelle
    data_main_client = pickle.dumps(main_client)
    envoi_info(data_main_client,s)

# envoi de la main des autres joueurs
    envoi_info((len(shared_memory_dic["mains"]).to_bytes(1,byteorder='big')),s)
    
    for j,m in shared_memory_dic["mains"].items():
        if j != f"joueur_{num_joueur}":
            data_main_joueurs = pickle.dumps((j, m))
            envoi_info(len(data_main_joueurs).to_bytes(4, byteorder='big'), s)
            envoi_info(data_main_joueurs, s)
    print("fin envoi mains")
    #shared_memory_dic["shared"].release()


#DEF ENVOI ETAT DES SUITES
def envoi_suites(shared_memory_dic,s):
    envoi = []
    for c,v in shared_memory_dic["suites"]:
        envoi.append((c,v))
    envoi_info(pickle.dumps(envoi),s)
    



def mon_tour(num_joueur,shared_memory_dic, message_queue_dic, s, synchro):
    synchro.clear()
    envoi_info(str(shared_memory_dic["indices"].value),s)
    choix_client = reception_info(s)
    #GERER L'ABSCENCE DE TOKENS INFORMATION
    if choix_client == "indice":
        joueur_vise = reception_info(s)
        info_donnee = reception_info(s)
        for j,mq in message_queue_dic.items():
            if j!= num_joueur:
                mq.send(str((joueur_vise,info_donnee)).encode(),type=3)
        synchro.set()

    else:
        indice_carte_choisie = reception_info(s)
        # au serveur --> envoyer l'indice
        shared_memory_dic["sem"].release()
        message_queue_dic[f"{num_joueur}"].send(indice_carte_choisie.encode(),type=2)

        # aux autres process --> retrouver le tuple de la carte
        carte_choisie = shared_memory_dic["mains"][f"joueur_{num_joueur}"][indice_carte_choisie-1]
        for j,mq in message_queue_dic.items():
            if j!= num_joueur:
                mq.send(str(carte_choisie).encode(), type = 2)

    shared_memory_dic["shared"].acquire()
    shared_memory_dic["tour"].value = (shared_memory_dic["tour"].value + 1) % 3
    shared_memory_dic["shared"].release()

    synchro.wait()



def joueur_process(num_joueur,shared_memory_dic, message_queue_dic, s,synchro):
    print(f"joueur {num_joueur} process waiting")
    synchro.wait()

    print("Le jeu commence !")
    global main_actuelle
    global connaissance
    connaissance = [[True,True] for i in range(5)]


    

    while True:
        envoi_mains(num_joueur,shared_memory_dic,s)
        envoi_suites(shared_memory_dic,s)
        envoi_info(str(shared_memory_dic["tour"].value),s)
        if  shared_memory_dic["tour"].value == num_joueur:
            mon_tour(num_joueur,shared_memory_dic, message_queue_dic, s, synchro)
            



        else:
            envoi_info("0",s)






        break
        
    #     # Consulte la shared memory et envoie l'état du jeu au client
    #     # Attente sur la message queue pour les actions du joueur
    #     # Envoi des messages sur l'action réalisée au client
    #     # Attente du signal de lancement du tour suivant

    s.close()

    #     pass

