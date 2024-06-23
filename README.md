# Projet IA02 

## Auteurs

Bastien Cuvillier, Colin Manyri

## Introduction

Ce projet a été réalisé dans le cadre de la formation d'ingénieur en Génie Informatique à l'Université de Technologie de Compiègne (UTC) et plus précisément dans le cadre de l'UV IA02 : Logique et Résolution de problèmes par la recherche.

L'objectif de ce projet était de coder des algorithmes capables de jouer aux jeux Gopher et Dodo de Mark Steere :
1. Site de Mark Steere : https://www.marksteeregames.com
2. Règles de Dodo : https://www.marksteeregames.com/Dodo_rules.pdf
3. Règles de Gopher : https://www.marksteeregames.com/Gopher_hex_rules.pdf

Par la suite, les différents algorithmes codés par les étudiants se sont affrontés lors d'un tournoi réalisé par l'intermédiaire d'un serveur en ligne. Les différents joueurs ont également un temps limité pour donner leurs coups, la rapidité et l'optimisation 
des algorithmes est donc de mise.

## Structure globale 

Ce repository est composé de 7 fichiers : 
1. Le fichier `Readme.md`, read me ci-présent
2. Le fichier `gnd.client.py` qui implémente les fonctionnalités du serveur
3. Le fichier `gndserver.exe` qui doit être exécuté pour lancer le serveur
4. Le fichier `affichage.py` qui implémente un affichage "userfriendly" des jeux
5. Le fichier `gopher.py` implémente notre algorithme pour Gopher
6. Le fichier `dodo.py` qui implémente notre algorithme pour Dodo
7. Le fichier `test_client.py` qui permet de jouer sur le serveur avec nos algorithmes


## Choix de l'algorithme utilisé 

Pour notre projet nous voulions développer un algorithme capable de gagner des parties tout en gardant une grande rapidité d'exécution, nécessaire pour ne pas être en manque de temps contre d'autres joueurs. Un algorithme `alpha-beta` que nous avons fortement optimisé nous a semblé être une option adaptée. Notamment, la possibilité de choisir la profondeur de l'algorithme nous permet d'obtenir un algorithme efficace et suffisamment rapide pour répondre aux exigences du concours (quitte à diminuer la profondeur).

Toujours dans une volonté d'améliorer les performances de notre algorithme nous avons implémenté de nombreuses optimisations que nous allons détailler :
- Le calcule uniquement local des coups légaux pour gopher afin d'économiser du temps de calcul.
- L'implémentation d'une fonction de mémoïzation pour l'algorithme alpha-beta.
- L'implémentation d'une fonction de tri des nœuds de l'arbre de l'alpha-beta pour faire les coupures alpha et beta plus rapidement comme décrit dans le Wikipédia en version allemande de l'alpha-beta : https://de.wikipedia.org/wiki/Alpha-Beta-Suche 
- L'implémentation d'une fonction de hashage des grilles de Gopher et Dodo qui permet d'économiser de l'espace mémoire dans le cache des grilles memoïzées.


## Choix de représentation des données 
- Coordonnées : 
![Systeme de coordonnées presenté pour une grille de taille 7](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/grid_hex.png)
- Représentation par une matrice : 
![Representation de la grille de taille 7 sous la forme d'une matrice 2D](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/matrix_hex.png)




## Calcul local des coups légaux pour Gopher 

Nous avons remarqué que les coups joués par les joueurs dans le cas de Gopher n'influencent les coups légaux suivant que sur une partie locale de la grille, nous avons utilisé cette information pour ne recalculer que localement les coups légaux des différents joueurs. 

Exemple : 
Lorsqu'un joueur joue en position `(0,0)`, les coups légaux potentiellement changés sont les coups qui impliquent les cases voisines de la case remplie. Il suffit donc de tester la légalité des 6 cases voisines, c'est à dire les cases `(1, 1), (1, 0), (0,-1), (-1, -1), (-1, 0), (0, 1)`

Stockage de l'information : nous avons choisi de stocker la liste des coups légaux dans un dictionnaire python `dico_legaux` de type `Dict[Case, bool]`, les coups légaux ont une value True. 
Ce système de stockage permet de tester si le coup existe (d'un point de vue de la grille donné, qui est de taille variable)

Dans `Gopher.py`, la fonction `init_dico_legaux_gopher()` permet d'initialiser les dictionnaires des coups légaux (tous les coups à False au début du jeu).
Puis la fonction update_dico_legaux() permet de mettre à jour les dictionnaires des coups légaux pour les deux joueurs, après qu'un coup ait été joué. 
Cette fonction est appelée dans la fonction de mise à jour de l'environnement `play_action()` qui permet de jouer une action donnée pour un joueur donné et qui renvoie l'environnement (c'est à dire l'ensemble des informations nécéssaires au jeu) modifié par le coup. 

Notre méthode utilisé pour determiner les coups légaux constitue un gain en temps de calcule non négligable. En effet, nous sommes alors restraint au testes de la legalité de au plus six voisins de la dernière action jouée. 
D'un point de vu plus quantitatif :

Une grille hexagonale de taille N, contient 3N(N-1)+1, nous laissons au lecteur le soin de la demonstration (vous pouvez raisonner sur la taille de la matrice donnée dans la partie `choix de la representation des données`).
Notre calcul permet donc de passer d'une complexité O(N^2), en effet 3N(N-1)+1 ~ N^2, à une complexité constante O(1) sur cette partie du calcule de complexité.

Pourquoi ne pas utiliser la même technique sur Dodo ? 
Dodo est un jeu plus complexe car les jetons ne sont pas uniquement placés sur les cases mais déplacés d'une case à l'autre. Implémenter le stockage de la liste de tous les coups possibles sous forme d'un dictionnaire revient alors à stocker tous les couples de cases possibles ce qui prendrait énormément de place. De plus, la complexité de l'update de ce dictionnaire ne ferait finalement pas gagner beaucoup de temps par rapport au calcul naïf de la légalité des coups pour toutes les cases.

## Implementation de la memoïzation pour les joueurs 

Lors de la recherche des coups possibles pour un joueur, il est possible de tomber sur des états de jeu déjà rencontrés.

Pour éviter de recalculer les coups possibles via notre algorithme alphabeta amélioré, nous avons implémenté une fonction de memoïzation qui permet de stocker le meilleur coup pour un état de jeu déjà rencontré.

### Fonction de hashage des grilles

Afin de représenter au mieux l'état de jeu, que cela soit sur dodo ou gopher, nous avons choisi d'utiliser une fonction de hashage qui permet de stocker l'état de jeu sous forme de chaine de caractère. Cette chaine de caractère est ensuite utilisée comme clé dans un dictionnaire qui stocke les coups possibles pour un état de jeu donné.

Comment obtenir cette chaine de caractère?

Nous utilison la fonction `hashing` qui prend en paramètre la grille actuelle des *GameValues*. Elle va parcourir la grille et à chaque case rencontrée, elle va ajouter dans la chaine de caractère de sortie le chiffre 0, 1 ou 2.
- 0 si la case est innocupée (`EMPTY`)
- 1 si la case est occupée par le joueur rouge (`ROUGE`)
- 2 si la case est occupée par le joueur bleu (`BLEU`)

Nous obtenons alors un grand nombre représentant l'état de la grille à un moment donné. Ce nombre est ensuite converti de la base 10 à la base 64 (fonction `base64`) pour obtenir une chaine de caractère plus courte. Nous occupons ainsi moins de place en mémoire.

`hashing` renvoie alors la chaine de caractère convertie précédemment en base 64. Pour information, nous utilisons l'alphabet suivant : `0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,`.

### Fonction de memoïzation

La fonction `memoize` est ensuite utilisée comme *decorator* de la fonction `alpha_beta`. Elle permet à chaque coup calculé (ou non) par celui-ci de stocker le nouveau coup calculé dans un dictionnaire de la forme `Dict[str, Tuple[int, int]]` (pour gopher) ou `Dict[str, Tuple[Tuple[int, int],Tuple[int, int]]]` (pour dodo). La clé de ce dictionnaire est la chaine de caractère obtenue par la fonction `hashing` et la valeur associée est le meilleur coup calculé pour cet état de jeu.

Le cas de gopher est particulier car le plateau de jeu comporte un grand nombre de symétries. A chaque nouveau coup calculé, nous stockons si cela n'a pas déjà été fait, les 6 reflexions ainsi que les 6 rotations provenant de ces réflexions dans le cache. Donc à chaque coup, nous stockons potentiellement 36 états de jeu dans le cache.


## Utilisation de notre programme:

### Localement

Pour lancer une partie de dodo ou gopher avec notre propre boucle de jeu, il suffit de se rendre dans le fichier `dodo.py` ou `gopher.py` et de lancer les fonctions correspondantes aux boucles de jeux contre un joueur random à savoir:
- `boucle_rd_alpha_beta(taille_grille: int, depth: int) -> float` pour dodo.
- `boucle_rd_ai(taille_grille: int, depth: int) -> float:` pour gopher.

Pour l'affichage de l'état de jeu, il suffit de décommenter la/les lignes `aff.afficher_hex(grille, dico_conversion)`.

Ces deux fonctions vous renvoie alors le score de la partie jouée.

### Via le serveur

*Depuis le readme donné dans le repository du serveur*

***__START__***
Le serveur s'exécute en ligne de commande (terminal sous linux et macOS, powershell sous windows) 

1. Copier le bon executable dans votre répertoire de travail. On suppose par la suite que l'exécutable s'appelle `gndserver`
2. Ajouter les droits en exécution (si besoin sous linux et MaxOS) : `chmod a+x gndserver`
3. Vérifier le fonctionnement et voir les options : `./gndserver`

```bash
# toutes les options
./gndserver -h
```

```bash
# lancer un serveur de dodo contre un joueur random
./gndserver -game dodo -random 
```

```bash
# lancer un serveur de gopher contre un joueur random
./gndserver -game gopher -random
```

```bash
# lancer un serveur de gopher contre un joueur random gopher qui sera la joueur bleu
./gndserver -game gopher -rcolor blue -random
```

```bash
# tout réinitialiser
rm config.json server.json
```
***__FINISH__***

Il faut donc dans un premier temps lancer un terminal et se rendre dans le répertoire où se trouve le serveur. On y lance le serveur avec les options souhaitées.

## Utilisation du client

Rendez-vous encore une fois dans un terminal après avoir lancé le serveur. Veillez au préalable d'avoir:

1. Copié le fichier `gndclient.py` dans votre répertoire de travail
2. Copié le fichier `test_client.py` dans votre répertoire de travail

Enfin, dans ce même terminal, lancez la commande suivante:

```bash
# lancer le client
python test_client.py 12 toto totovelo
```

Avec `12` le numéro de groupe, `toto` le nom du joueur et `totovelo` le mot de passe du joueur.

Un partie devrait alors se lancer et se jouer devant vos yeux.