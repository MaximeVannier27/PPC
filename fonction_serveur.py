def main_server():
    print("main_server")

    # Code pour demander le nombre de joueurs, créer les processus, etc.

def piocheCarte(pioche):
    return

pioche = []

def distribution(nombre_joueurs):
    couleurs = ["rouge","vert","bleu","jaune","blanc"]
    global pioche
    for color in range(nombre_joueurs):
        pioche+= [(1,couleurs[color])]*3
        pioche+= [(2,couleurs[color]),(3,couleurs[color]),(4,couleurs[color])]*2
        pioche+= [(5,couleurs[color])]
    print(pioche)

    