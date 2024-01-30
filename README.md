# HANNABIS
### Intro
Ce code permet de jouer à une version simplifiée du jeu hanabi, pour un nombre de joueurs allant de 2 à 5.

### Règles
Afin de réaliser le plus beau feu d'artifice possible, vous devez compléter autant de suites de 5 cartes numérotées de 1 à 5 qu'il y a de joueurs. Chaque suite à compléter correspond à une couleur et vous ne voyez pas vos propres cartes mais seulement celles des autres joueurs. Les cartes d'une suite doivent être posées dans l'ordre croissant.
A chaque tour où vous jouez, vous aurez le choix de poser une carte de votre main ou informer un joueur sur toutes les cartes qu'il a corespondant au chiffre ou à une couleur que vous avez spécifié. Mais attention, vous disposez d'un nombre limité d'indices à donner qui n'augmente que lorsque vous complétez une suite et n'avez le droit qu'à trois erreurs. 
Un score totalisant la plus haute carte posée pour chaque suite vous sera donné en fin de partie.

### Lancer une partie
Pour lancer une partie : 
- lancez le programme main_serveur.py (si vous avez python3, commande : python3 main_serveur.py).
Vous allez devoir préciser le nombre de joueurs souhaité puis ensuite le port sur lequel vous voulez héberger la partie (cela permet d'éviter des problèmes de disponibilité lorsque plusieurs parties sont lancées successivement).
- lancez le programme main_client.py pour créer un joueur. Vous devrez ensuite renseigner le port de la partie. 

Une fois le bon nombre de joueurs connectés, vous pouvez jouer!!
