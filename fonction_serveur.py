from random import randint
import signal
import os
from joueur_process import envoi_info

#FONCTION DE FIN DE PARTIE: fermeture des process et envoi aux clients du message de fin de partie (en fonction du type de fin de partie)
def fin_partie(shared_memory,dic_mq,typefin,dic_joueurs):

    if typefin=="erreur":
        score = 0
        for chiffre in shared_memory["suites"].values():
            score+=chiffre
        message = f"Il n'y a plus de jetons erreurs, la partie est terminée! Le score final est de {score}"
        
    else:
        score=5*len(dic_mq.values())
        message = f"La partie est terminée, toutes les suites sont complètes! Le score final est de {score}"

    for i in range(1,len(dic_mq.values())+1):
        os.kill(dic_joueurs[f"joueur_{i}"]["process"].pid, signal.SIGUSR1)
        envoi_info(message,dic_joueurs[f"joueur_{i}"]["client"])


def main_server(shared_memory,pioche,dic_mq,erreurs,synchro):
#Boucle principale côté serveur
    while True:
        print("Process main_serveur: main_server start")
        #Attend qu'un joueur Signale une pioche
        shared_memory["sem"].acquire()

        #Récupère l'acccès aux variables partagées
        shared_memory["shared"].acquire()

        #Récupère l'info sur la carte piochée en écoutant sur la mq du joueur qui a posé
        j = shared_memory["tour"].value
        print("TOUR DANS MQ",j)
        message, t = dic_mq[f"{j}"].receive()
        if t!=1:
            print("Erreur lors de la réception de l'indice d'une carte posée")

        i_carte = int(message.decode())-1
        print("Process main_serveur: Indice de la carte posée",i_carte)
        (valeur,couleur) = shared_memory["mains"][f"joueur_{j}"][i_carte]
        print("Process main_serveur: valeur/couleur de la carte posée",valeur,couleur)

#Test sur la carte posée et sa validité
        if valeur != (shared_memory["suites"][couleur]+1):
            erreurs-=1
            if erreurs<=0:
                return "erreur"

        elif valeur==5:
            shared_memory["indices"]+=1
            if shared_memory["suites"].values.count(5)==len(shared_memory["suites"].values):
                fin_partie(shared_memory,dic_mq,"bouche")
                break

        else:
            shared_memory["suites"][couleur]+=1

        #Distribution d'une nouvelle carte au joueur qui a posé
        if len(pioche)>0:
            main_temp = shared_memory["mains"][f"joueur_{j}"]
            main_temp.pop(i_carte)
            main_temp.insert(i_carte,pioche.pop(randint(0,len(pioche)-1)))
            shared_memory["mains"][f"joueur_{j}"]=main_temp
            print("Process main_serveur: nouvelle main du joueur:\n\t",shared_memory["mains"][f"joueur_{j}"])
        else:
            shared_memory["mains"][f"joueur_{j}"][i_carte] = (None,None) #Envoi d'une carte NULL si la pioche est vide (peu probable)

        #Incrémentation du tour 
        print("Process main_serveur: tour avant incrémentation",shared_memory["tour"])
        shared_memory["tour"].value=j%len(dic_mq)+1

        #Lance le tour suivant après avoir libéré le lock sur les variables partagées
        shared_memory["shared"].release()
        synchro.set()




#FONCTION D'INITIALISATION DE LA PIOCHE, DES MAINS DES JOUEURS ET DES SUITES
def distribution(nombre_joueurs,pioche,shared_memory):

    couleurs = ["rouge","vert","bleu","jaune","violet"]
    shared_memory["shared"].acquire()

    for color in range(nombre_joueurs):
        pioche+= [(1,couleurs[color])]*3
        pioche+= [(2,couleurs[color]),(3,couleurs[color]),(4,couleurs[color])]*2
        pioche+= [(5,couleurs[color])]
        shared_memory["suites"][couleurs[color]]=0

    for i in range(1,nombre_joueurs+1):
        shared_memory["mains"][f"joueur_{i}"]=[]
        for j in range(5):
            carte=pioche.pop(randint(0,len(pioche)-1))
            shared_memory["mains"][f"joueur_{i}"]+=[carte]

    shared_memory["shared"].release()

