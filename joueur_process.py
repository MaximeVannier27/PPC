import pickle
from affichage import affichecarte
from ast import literal_eval as ev
import signal
import os


#FONCTION DE GESTION DU SIGNAL DE FIN DE PARTIE => KILL DES PROCESS
def handler(sig,frame):
    if sig == signal.SIGUSR1:
        process = os.getpid()
        print(f"Destruction du process client {process}")
        os.kill(os.getpid(),signal.SIGKILL)

#FONCTIONS PERMETTANT DE SYNCHRONISER LES ECHANGES TCP CLIENT/SERVEUR -> éviter le surchargement des buffers
def demande_to_client(chaussette):
    demande_to_client = "demande"
    chaussette.send(demande_to_client.encode())

def demande_from_client(chaussette):
    chaussette.recv(1024)


#FONCTIONS D'ENVOI ET DE RECEPTION DES DONNEES ENTRE CLIENT/SERVEUR
def reception_info(chaussette):
    res_code = chaussette.recv(1024)
    res = res_code.decode()
    return res

def envoi_info(data_brut,chaussette):
    if type(data_brut) != bytes:
        data = data_brut
        chaussette.send(data.encode())
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

    shared_memory_dic["shared"].acquire()
    main_actuelle = shared_memory_dic["mains"][f"joueur_{num_joueur}"]
    main_client = []
    #formatage de la main personnelle qui sera envoyé au client en fonction de la connaissance de son jeu réelle (main_actuelle)
    for i in range(len(main_actuelle)):
        if not connaissance[i][0] and not connaissance[i][1]:
            main_client.append(("?","?"))
        if connaissance[i][0] and not connaissance[i][1]:
            main_client.append((main_actuelle[i][0],"?"))
        if not connaissance[i][0] and connaissance[i][1]:
            main_client.append(("?",main_actuelle[i][1]))
        if connaissance[i][0] and connaissance[i][1]:
            main_client.append((main_actuelle[i][0],main_actuelle[i][1]))
    
#Envoi de la main actuelle
    data_main_client = pickle.dumps(main_client)
    envoi_info(data_main_client,s)

#Envoi de la main des autres joueurs
    envoi_info((len(shared_memory_dic["mains"]).to_bytes(1,byteorder='big')),s)
    
    for j,m in shared_memory_dic["mains"].items():
        if j != f"joueur_{num_joueur}":
            data_main_joueurs = pickle.dumps((j, m))
            envoi_info(len(data_main_joueurs).to_bytes(4, byteorder='big'), s)
            envoi_info(data_main_joueurs, s)
    print(f"Process joueur_{num_joueur}: Fin envoi mains")
    shared_memory_dic["shared"].release()

#FONCTION ENVOYANT L'ETAT DES SUITES GRACE AU MODULE PICKLE
def envoi_suites(shared_memory_dic,s):
    envoi = []
    for c,v in shared_memory_dic["suites"].items():
        envoi.append((v,c))
    envoi_info(pickle.dumps(envoi),s)

def mon_tour(num_joueur,shared_memory_dic, message_queue_dic, s, synchro):
    global connaissance
#Vérification de la possiblité ou non de donner un indice (token_info > 0) et envoi du résultat au client
    if shared_memory_dic["indices"].value > 0:
        demande_from_client(s)
        envoi_info("possible",s)
        demande_to_client(s)
        choix_client = reception_info(s)
    else:
        #si pas de choix possible, il est forcé en pose
        demande_from_client(s)
        envoi_info("impossible",s)
        choix_client = "pose"
    
    print(f'Process joueur_{num_joueur}: Reception choix',choix_client)

#Disjonction de cas en fonction du choix
    if choix_client == "indice":
        demande_to_client(s)
        joueur_vise = int(reception_info(s))
        print(f"Process joueur_{num_joueur}: Joueur visé {joueur_vise}")
        demande_to_client(s)
        info_donnee = reception_info(s)
        synchro.clear()
        #envoi de l'indice et du joueur visée par celui-ci à tous les autres joueurs/process à travers leur message queue
        for j,mq in message_queue_dic.items():
            if j!= str(num_joueur):
                mq.send(str((joueur_vise,info_donnee)).encode(),type=3)
        synchro.set()
        #modification des valeurs en shared memory
        shared_memory_dic["shared"].acquire()
        shared_memory_dic["indices"].value -= 1
        shared_memory_dic["tour"].value = (shared_memory_dic["tour"].value % len(message_queue_dic))+1
        shared_memory_dic["shared"].release()

    else:
        demande_to_client(s)
        indice_carte_choisie = reception_info(s)
        #la carte posée est défaussée, et la nouvelle piochée devient alors inconnue au joueur
        connaissance[int(indice_carte_choisie)-1] = [False,False]
        
        carte_choisie = shared_memory_dic["mains"][f"joueur_{num_joueur}"][int(indice_carte_choisie)-1]
        #envoi de la réussite ou non de la pose en fonction de l'état actuel des suites et signalisation en conséquence au client
        if carte_choisie[0] != (shared_memory_dic["suites"][str(carte_choisie[1])]+1):
            demande_from_client(s)
            envoi_info("Mauvaise carte ! Vous perdez un fuse token",s)
        else:
            demande_from_client(s)
            envoi_info("Bien joué ! Les suites avancent !!",s)
        
        
        synchro.clear()
        #envoi des informations sur la carte posée aux autres joueur/process à travers leur message queue
        for j,mq in message_queue_dic.items():
            if j!= str(num_joueur):
                mq.send(str(carte_choisie).encode(), type = 2)

        # envoi au serveur principal (process parent) de l'indice de la carte choisir pour que celui-ci gère la pioche et l'actualisation des shared memory (suites, états des mains,...)
        shared_memory_dic["sem"].release()
        message_queue_dic[f"{num_joueur}"].send(indice_carte_choisie.encode(),type=2)
        
        synchro.wait() 

def pas_mon_tour(moi,socket,dic_mq,shared_memory_dic,synchro):
#Stockage du numéro du joueur qui joue actuellement à travers la variable partagée "tour"
    tour=int(shared_memory_dic["tour"].value)
#Réception de l'information sur ce qu'a joué le joueur courant (IPC à travers la message queue)
    receipt, t = dic_mq[f"{moi}"].receive()
#Disjonction de cas en fonction du tag du message récupérée (3: un indice a été donné; 2: une carte a été posée)
    if t==3:
        #joueur: joueur visé par l'indice; indice: information donnée (couleur ou chiffre)
        (joueur,indice) = decodet(receipt)
        if joueur==moi:
            info = f"Le joueur {tour} vous informe sur vos cartes {indice}"
            global connaissance
            mescartes=shared_memory_dic["mains"][f"joueur_{moi}"]

            #Mise à jour des connaissances du joueur en fonction de l'indice reçu, s'il lui été adressé
            for i in range(len(connaissance)):
                if str(mescartes[i][0])==indice:
                    connaissance[i][0]=True
                elif str(mescartes[i][1])==indice:
                    connaissance[i][1]=True
        else:
            #Si pas concerné, les autres joueurs reçoivent quand même l'information sur l'indice donné
            info = f"Le joueur {tour} a informé le joueur {joueur} sur ses cartes: {indice}"
            
    if t==2: 
        print(f"Process joueur_{moi}: receipt carte posée",receipt.decode())
        #(valeur,couleur) : carte posée
        #Formatage de l'information pour les joueurs en attente
        (valeur,couleur) = decodet(receipt)
        info = f"Le joueur {tour} a posé une carte " + affichecarte(valeur,couleur) + '\033[0m'
    demande_from_client(socket)
    envoi_info(info,socket)
#gestion synchro
    synchro.wait()

def joueur_process(num_joueur,shared_memory_dic, message_queue_dic, s,synchro,debut):
#Annonce côté serveur que le processus est en attente que tous les joueurs se connectent au serveur
    print(f"Joueur {num_joueur} process waiting")
    debut.wait()

#Initialisation des informations sur la main du joueur (local) 
    print(f"Process joueur_{num_joueur}: Le jeu commence !")
    global main_actuelle
    global connaissance
    connaissance = [[False,False] for i in range(5)]

#Amorçage du signal de fin de partie
    signal.signal(signal.SIGUSR1, handler)
    
#Début de la boucle principale du jeu
    while True:
        print(f"Process joueur_{num_joueur}: Envoi mains ")
#Envoi de la main du joueur formatée + celles des autres joueurs en clair à chaque nouveau tour
        demande_from_client(s)
        envoi_mains(num_joueur,shared_memory_dic,s)
        envoi_suites(shared_memory_dic,s)
#Envoi du numero de tour courant (= numero du joueur pour qui c'est le tour)
        print(f"Process joueur_{num_joueur}: Numéro de tour envoyé",str(shared_memory_dic["tour"].value))
        demande_from_client(s)
        envoi_info(str(shared_memory_dic["tour"].value),s)

#Discjonction de cas en fonction de la valeur du tour
        if  int(shared_memory_dic["tour"].value) == num_joueur:
            mon_tour(num_joueur,shared_memory_dic, message_queue_dic, s, synchro)
        else:
            pas_mon_tour(num_joueur,s,message_queue_dic,shared_memory_dic,synchro)
