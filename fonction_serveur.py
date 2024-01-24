from random import randint
import sysv_ipc
from ast import literal_eval as ev
import signal
import os
 
def handler(sig,frame):
    if sig == signal.SIGUSR1:
        global dic_mq
        dic_mq

def fin_partie(shared_memory,dic_mq,typefin):
    global dic_joueurs

    if typefin=="erreur":
        print("Il n'y a plus de jetons erreurs, la partie est terminée!")
        flag=47
        score = 0
        for chiffre in shared_memory["suites"].values():
            score+=chiffre
        
    else:
        print("La partie est terminée, toutes les suites sont complètes!")
        flag=43
        score=5*len(dic_mq.values())

    for i in range(len(dic_mq.values())):
        os.kill(dic_joueurs[f"joueur_{i}"]["process"].pid, signal.SIGUSR1)
        score.encode()
        dic_mq[f"{i}"].send(score,type=flag)

    

def decodet(message):
    """
    Permet de récuper directement un tuple à partir des données reçue dans la messagequeue
    """
    return ev(message.decode())


def main_server(shared_memory,pioche,dic_mq,erreurs,synchro):
    while True:
        print("main_server")
        #attend qu'un joueur sSignale une pioche
        shared_memory["sem"].acquire()

        #récupère l'acccès aux variables partagées
        shared_memory["shared"].acquire()

        #récupère l'info sur la carte piochée en écoutant sur la mq du joueur qui a posé
        j = shared_memory["tour"].value
        message, flag = dic_mq[f"{j}"].listen()
        i_carte = int(message.decode())
        (valeur,couleur) = shared_memory["mains"][f"{j}"][i_carte]

        if valeur != (shared_memory["suites"][couleur]+1):
            erreurs-=1
            if erreurs<=0:
                fin_partie(shared_memory,dic_mq,"erreur")
                break

        elif valeur==5:
            shared_memory["indices"]+=1
            if shared_memory["suites"].values.count(5)==len(shared_memory["suites"].values):
                fin_partie(shared_memory,dic_mq,"bouche")
                break

        else:
            shared_memory["suites"][couleur]+=1

        #distribution d'une nouvelle carte au joueur qui a posé
        if len(pioche)>0:
            shared_memory["mains"][f"tour"][i_carte] = pioche.pop(randint(0,len(pioche)-1))
        else:
            shared_memory["mains"][f"tour"][i_carte] = (None,None)

        #incrémentation du tour 
        shared_memory["tour"]+=1

        #lance le tour suivant après avoir libéré le lock sur les variables partagées
        shared_memory["shared"].release()
        synchro.set()




    
def distribution(nombre_joueurs,pioche,shared_memory):

    couleurs = ["rouge","vert","bleu","jaune","violet"]
    shared_memory["shared"].acquire()

    for color in range(nombre_joueurs):
        pioche+= [(1,couleurs[color])]*3
        pioche+= [(2,couleurs[color]),(3,couleurs[color]),(4,couleurs[color])]*2
        pioche+= [(5,couleurs[color])]
        shared_memory["suites"][color]=0

    for i in range(1,nombre_joueurs+1):
        shared_memory["mains"][f"joueur_{i}"]=[]
        for j in range(5):
            carte=pioche.pop(randint(0,len(pioche)-1))
            shared_memory["mains"][f"joueur_{i}"]+=[carte]

    shared_memory["shared"].release()

