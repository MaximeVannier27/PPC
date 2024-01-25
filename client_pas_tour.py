from fonction_serveur import decodet
from joueur_process import envoi_info
from test import affichecarte

def pas_mon_tour(moi,socket,dic_mq,shared_memory_dic,synchro):
    tour=shared_memory_dic["tour"]
    receipt, t = dic_mq[f"{joueur}"].receive()
    if t==3:
        (joueur,indice) = decodet(receipt)
        if joueur==moi:
            info = f"Le joueur {tour+1} vous informe sur vos cartes {indice}"
            global connaissance
            mescartes=shared_memory_dic["mains"][f"joueur_{moi}"]

            #update des connaissances du joueur en fonction de l'indice reçu
            for i in range(connaissance):
                if str(mescartes[i][0])==indice:
                    connaissance[i][0]=True
                elif str(mescartes[0][i])==indice:
                    connaissance[0][i]=True
        else:
            info = f"Le joueur{tour+1} a informé le joueur{joueur} sur ses cartes {indice}"

    if t==2: 
        (valeur,couleur) = decodet(receipt)
        info = f"Le joueur{tour+1} a posé une carte" + affichecarte(valeur,couleur)
    envoi_info(info,socket)

    synchro.wait()
