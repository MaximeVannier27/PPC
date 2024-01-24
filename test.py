
mains = (("?","vert"),("?","bleu"),(1,"?"),(2,"violet"),(5,"rouge"))

def affichemain(main):
    print("✺",end='  ')
    stil = {"?":'\033[90;1m',"rouge":'\033[31;1m',"vert":'\033[32;1m',"jaune":'\033[33;1m',"bleu":'\033[34;1m',"violet":'\033[35;1m'}
    for (valeur,couleur) in main:
        print(stil[couleur],valeur, end=' ')
    print('\033[0m' + " ✺")

affichemain(mains)