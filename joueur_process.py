from multiprocessing import Value,Event
import time
import pickle
from test import affichecarte
from ast import literal_eval as ev
import signal
import os



def handler(sig,frame):
    if sig == signal.SIGUSR1:
        process = os.getpid()
        print(f"Destruction du process client {process}")
        os.kill(os.getpid(),signal.SIGKILL)


def reception_info(chaussette):
    demande = "demande"
    chaussette.send(demande.encode('utf-8'))
    res_code = chaussette.recv(1024)
    res = res_code.decode("utf-8")
    return res

def envoi_info(data_brut,chaussette):
    if type(data_brut) != bytes:
        data = data_brut
        chaussette.send(data.encode("utf-8"))
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
    shared_memory_dic["shared"].acquire()
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
    shared_memory_dic["shared"].release()


def envoi_suites(shared_memory_dic,s):
    envoi = []
    for c,v in shared_memory_dic["suites"].items():
        envoi.append((v,c))
    envoi_info(pickle.dumps(envoi),s)
    

def mon_tour(num_joueur,shared_memory_dic, message_queue_dic, s, synchro):
    synchro.clear()
    envoi_info(str(shared_memory_dic["indices"].value),s)
    choix_client = reception_info(s)
    print('Reception choix',choix_client)
    #GERER L'ABSCENCE DE TOKENS INFORMATION
    if choix_client == "indice":
        joueur_vise = int((s.recv(1)).decode("utf-8"))
        print(f"Joueur visée {joueur_vise}")
        info_donnee = reception_info(s)
        for j,mq in message_queue_dic.items():
            if j!= str(num_joueur):
                print(f"j de mq: {j}")
                mq.send(str((joueur_vise,info_donnee)).encode(),type=3)
        synchro.set()
        shared_memory_dic["shared"].acquire()
        shared_memory_dic["tour"].value = (shared_memory_dic["tour"].value % len(message_queue_dic))+1
        shared_memory_dic["shared"].release()

    

    else:
        indice_carte_choisie = reception_info(s)
        

        # aux autres process --> retrouver le tuple de la carte
        carte_choisie = shared_memory_dic["mains"][f"joueur_{num_joueur}"][int(indice_carte_choisie)-1]
        for j,mq in message_queue_dic.items():
            if j!= num_joueur:
                mq.send(str(carte_choisie).encode(), type = 2)

        # au serveur --> envoyer l'indice
        shared_memory_dic["sem"].release()
        message_queue_dic[f"{num_joueur}"].send(indice_carte_choisie.encode(),type=2)
        synchro.wait()

    

def pas_mon_tour(moi,socket,dic_mq,shared_memory_dic,synchro):
    tour=int(shared_memory_dic["tour"].value)
    receipt, t = dic_mq[f"{moi}"].receive()
    print("receipt",receipt.decode())
    if t==3:
        (joueur,indice) = decodet(receipt)
        print(joueur)
        if joueur==moi:
            info = f"Le joueur {tour} vous informe sur vos cartes {indice}"
            global connaissance
            mescartes=shared_memory_dic["mains"][f"joueur_{moi}"]

            #update des connaissances du joueur en fonction de l'indice reçu
            for i in range(connaissance):
                if str(mescartes[i][0])==indice:
                    connaissance[i][0]=True
                elif str(mescartes[0][i])==indice:
                    connaissance[0][i]=True
        else:
            info = f"Le joueur{tour} a informé le joueur{joueur} sur ses cartes {indice}"
            
    if t==2: 
        (valeur,couleur) = decodet(receipt)
        info = f"Le joueur{tour} a posé une carte" + affichecarte(valeur,couleur)
    envoi_info(info,socket)

    synchro.wait()

def joueur_process(num_joueur,shared_memory_dic, message_queue_dic, s,synchro,debut):
    print(f"joueur {num_joueur} process waiting")
    debut.wait()

    print("Le jeu commence !")
    global main_actuelle
    global connaissance
    connaissance = [[False,False] for i in range(5)]

    signal.signal(signal.SIGUSR1, handler)
    

    while True:
        print("envoi mains ",num_joueur)
        envoi_mains(num_joueur,shared_memory_dic,s)
        envoi_suites(shared_memory_dic,s)
        envoi_info(str(shared_memory_dic["tour"].value),s)
        print("tour/num joueur",shared_memory_dic["tour"].value,num_joueur)
        if  int(shared_memory_dic["tour"].value) == int(num_joueur):
            mon_tour(num_joueur,shared_memory_dic, message_queue_dic, s, synchro)
            



        else:
            pas_mon_tour(num_joueur,s,message_queue_dic,shared_memory_dic,synchro)

    s.close()

