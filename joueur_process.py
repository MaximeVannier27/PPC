import multiprocessing
import time
import pickle

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


def mon_tour(num_joueur,shared_memory_dic, message_queue_dic,s):
    global main_actuelle
    global connaissance

    "ATTENTION AUX CLES DES SHARED MEMORY"

    #main_actuelle = shared_memory_dic[mains][f"joueur_{num_joueur}"]
    main_actuelle = [(1,"rouge"),(2,"vert"),(1,"bleu"),(4,"vert"),(1,"blanc")]
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
    #for j,m in shared_memory_dic[mains]:
    dico = {"joueur_1": [(1,"rouge"),(2,"vert"),(1,"bleu"),(4,"vert"),(1,"blanc")], "joueur_2": [(5,"rouge"),(2,"bleu"),(1,"rouge"),(1,"vert"),(2,"blanc")],"joueur_3": [(3,"rouge"),(3,"vert"),(3,"bleu"),(3,"vert"),(3,"blanc")]}
    envoi_info(len(dico).to_bytes(1, byteorder='big'),s)
    for j,m in dico.items():
        if j != f"joueur_{num_joueur}":
            data_main_joueurs = pickle.dumps((j,m))
            envoi_info(data_main_joueurs,s)
            
    

    print("fin envoi mains")

    # DEMANDE_ACTIONS_AU_CLIENT(s)

    # if donner_info:

    


def joueur_process(num_joueur,shared_memory_dic, message_queue_dic, s,synchro):
    print(f"joueur {num_joueur} process waiting")
    synchro.wait()

    print("Le jeu commence !")
    global main_actuelle
    global connaissance
    connaissance = [(True,True) for i in range(5)]

    mon_tour(num_joueur,shared_memory_dic, message_queue_dic,s)

    # while True:
    #     # Consulte la shared memory et envoie l'état du jeu au client
    #     # Attente sur la message queue pour les actions du joueur
    #     # Envoi des messages sur l'action réalisée au client
    #     # Attente du signal de lancement du tour suivant



    #     pass

