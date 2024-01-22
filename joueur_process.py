import multiprocessing
import time

def reception_info(chaussette):
    data = chaussette.recv(1024)
    decoded_data = data.decode("utf-8")
    return decoded_data

def envoi_info(data_str,chaussette):
    data = data_str.encode('utf-8')
    chaussette.send(data)


def mon_tour(num_joueur,shared_memory_dic, message_queue_dic,s):
    global main_actuelle
    global connaissance

    "ATTENTION AUX CLES DES SHARED MEMORY"

    main_actuelle = shared_memory_dic[etat_main][f"joueur_{num_joueur}"]
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
    
    


    DEMANDE_ACTIONS_AU_CLIENT(s)

    if donner_info:

    


def joueur_process(num_joueur,shared_memory_dic, message_queue_dic, s,synchro):
    print("joueur process waiting")
    synchro.wait()

    print("Le jeu commence !")
    global main_actuelle
    global connaissance
    connaissance = [(False,False) for i in range(5)]

    while True:
        # Consulte la shared memory et envoie l'état du jeu au client
        # Attente sur la message queue pour les actions du joueur
        # Envoi des messages sur l'action réalisée au client
        # Attente du signal de lancement du tour suivant



        pass

