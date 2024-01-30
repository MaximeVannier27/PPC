
#mains_test = (("?","vert"),("?","bleu"),(1,"?"),(2,"violet"),(5,"rouge"))


#Affichage des cartes avec la couleur qui leur sont associées
def affichemain(main):
    print("✺",end='  ')
    for (valeur,couleur) in main:
        print(affichecarte(valeur,couleur),end=" ")
    print('\033[0m' + " ✺")


def affichecarte(valeur,couleur):
    stil = {"?":'\033[90;1m',"rouge":'\033[31;1m',"vert":'\033[32;1m',"jaune":'\033[33;1m',"bleu":'\033[34;1m',"violet":'\033[35;1m'}
    #print(stil[couleur],valeur, end=' ')
    return stil[couleur] + str(valeur)
