from fonction_serveur import decodet
from joueur_process import envoi_info
from test import affichecarte

def pas_mon_tour(moi,socket,dic_mq,shared_memory_dic,synchro):
    tour=shared_memory_dic["tour"]
    receipt, t = dic_mq[f"{joueur}"].receive()
    if t==1:
        (joueur,indice) = decodet(receipt)
        if joueur==moi:
            info = f"Le joueur {joueur} vous informe sur vos cartes {indice}"
            global connaissance
            mescartes=shared_memory_dic["mains"][f"joueur_{moi}"]
            for i in range(connaissance):
                if str(connaissance[i][0])==indice:
                    pass
                #update de connaissances, c'est pas fini
        else:
            info = f"Le joueur{tour} a informé le joueur{joueur} sur ses cartes {indice}"
    if t==2: 
        (valeur,couleur) = decodet(receipt)
        info = f"Le joueur{tour} a posé une carte" + affichecarte(valeur,couleur)
    envoi_info(info,socket)

    synchro.wait()
