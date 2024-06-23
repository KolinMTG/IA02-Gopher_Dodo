

# Projet IA02

## Auteurs

Bastien Cuvillier, Colin Manyri

## Introduction

Ce projet a été réalisé dans le cadre de la formation d'ingénieur en Génie Informatique à l'Université de Technologie de Compiègne (UTC) et plus précisément dans le cadre de l'UV IA02 : Logique et Résolution de problèmes par la recherche.

L'objectif de ce projet était de coder des algorithmes capables de jouer aux jeux Gopher et Dodo de Mark Steere :
1. Site de Mark Steere : https://www.marksteeregames.com
2. Règles de Dodo : https://www.marksteeregames.com/Dodo_rules.pdf
3. Règles de Gopher : https://www.marksteeregames.com/Gopher_hex_rules.pdf

Par la suite, les différents algorithmes codés par les étudiants se sont affrontés lors d'un tournoi réalisé par l'intermédiaire d'un serveur en ligne. Les différents joueurs ont également un temps limité pour donner leurs coups, la rapidité et l'optimisation des algorithmes sont donc de mise.


## Structure globale

Ce repository est composé de 7 fichiers :
1. Le fichier `Readme.md`, le présent fichier README
2. Le fichier `gnd.client.py` qui implémente les fonctionnalités du serveur
3. Le fichier `gndserver.exe` qui doit être exécuté pour lancer le serveur
4. Le fichier `affichage.py` qui implémente un affichage convivial des jeux
5. Le fichier `gopher.py` qui implémente notre algorithme pour Gopher
6. Le fichier `dodo.py` qui implémente notre algorithme pour Dodo
7. Le fichier `test_client.py` qui permet de jouer sur le serveur avec nos algorithmes

## Choix de représentation des données

- Coordonnées :
![Système de coordonnées présenté pour une grille de taille 7](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/grid_hex.png)
- Représentation par une matrice :
![Représentation de la grille de taille 7 sous forme d'une matrice 2D](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/matrix_hex.png)

## Choix de l'algorithme utilisé

Pour notre projet, nous avons développé un algorithme visant à maximiser les performances tout en maintenant une grande rapidité d'exécution, indispensable pour répondre aux contraintes de temps du concours contre d'autres joueurs. Nous avons choisi d'implémenter l'algorithme `alpha-beta`, que nous avons optimisé de manière significative. La flexibilité offerte par la possibilité de régler la profondeur de l'algorithme nous permet d'obtenir une solution efficace et suffisamment rapide en ajustant cette profondeur au besoin.

Dans notre démarche d'amélioration des performances de l'algorithme, nous avons mis en œuvre plusieurs optimisations détaillées ci-dessous :
- Calcul localisé des coups légaux pour Gopher afin d'économiser du temps de calcul.
- Utilisation d'une fonction de mémorisation pour l'algorithme alpha-beta.
- Tri des nœuds de l'arbre alpha-beta pour optimiser les coupures alpha et beta, inspiré des pratiques décrites dans la version allemande de l'article Wikipédia sur l'alpha-beta : [Alpha-Beta-Suche](https://de.wikipedia.org/wiki/Alpha-Beta-Suche).
- Mise en place d'une fonction de hachage pour les grilles de Gopher et Dodo, permettant d'économiser de l'espace mémoire en conservant les grilles mémorisées.




## Calcul local des coups légaux pour Gopher

Nous avons remarqué que les coups joués par les joueurs dans le cas de Gopher n'influencent les coups légaux suivants que sur une partie locale de la grille. Nous avons utilisé cette information pour ne recalculer que localement les coups légaux des différents joueurs.

Exemple :
Lorsqu'un joueur joue en position `(0,0)`, les coups légaux potentiellement changés sont les coups qui impliquent les cases voisines de la case remplie. Il suffit donc de tester la légalité des 6 cases voisines : `(1, 1), (1, 0), (0, -1), (-1, -1), (-1, 0), (0, 1)`.

Stockage de l'information : nous avons choisi de stocker la liste des coups légaux dans un dictionnaire Python `dico_legaux` de type `Dict[Case, bool]`, où les coups légaux sont représentés par `True`. Ce système permet de vérifier rapidement l'existence d'un coup dans la grille, qui peut varier en taille.

Dans `Gopher.py`, la fonction `init_dico_legaux_gopher()` initialise les dictionnaires des coups légaux (tous les coups sont initialisés à `False` au début du jeu). Ensuite, la fonction `update_dico_legaux()` met à jour ces dictionnaires après qu'un coup a été joué par un joueur. Cette fonction est appelée depuis la fonction `play_action()`, qui gère l'exécution d'une action pour un joueur donné et retourne l'environnement modifié (c'est-à-dire toutes les informations nécessaires au jeu).

Notre méthode pour déterminer les coups légaux offre un gain significatif en termes de temps de calcul. En restreignant le test à au plus six voisins de la dernière action jouée, nous passons d'une complexité O(N^2), où N est la taille de la grille, à une complexité constante O(1) pour cette partie du calcul.

Pourquoi ne pas utiliser la même technique pour Dodo ?
Dodo est un jeu plus complexe où les jetons peuvent être déplacés d'une case à l'autre, et non seulement placés sur des cases. Stocker la liste complète de tous les coups possibles sous forme de dictionnaire serait donc très coûteux en termes de mémoire. De plus, la complexité de la mise à jour de ce dictionnaire ne justifierait pas l'économie de temps par rapport au calcul direct de la légalité des coups pour toutes les cases.

## Tri des noeuds de l'alpha-beta

En explorant les améliorations possibles de l'algorithme alpha-beta, nous avons découvert qu'il était bénéfique de trier les noeuds (c'est-à-dire les coups testés) de l'alpha-beta. Ce tri permet d'effectuer les coupures alpha ou beta plus rapidement, en testant d'abord les branches les plus prometteuses. Selon l'article de Wikipedia précédemment mentionné, cette optimisation peut réduire le temps de calcul par un facteur significatif :

Voici ce qui est indiqué dans l'article :
Algorithmus	Bewertungen	Cutoffs	Anteil der Cutoffs	Rechenzeit in Sekunden  
**Minimax**	28.018.531	0	0,00 %	134,87 s (Algorithme minmax)  
**AlphaBeta**	2.005.246	136.478	91,50 %	9,88 s (Algorithme alpha-beta)  
**AlphaBeta + Zugsortierung**	128.307	27.025	99,28 %	0,99 s (Algorithme alpha-beta avec tri des noeuds)  


## Implementation de la memoïzation pour les joueurs

Lors de la recherche des coups possibles pour un joueur, il est possible de tomber sur des états de jeu déjà rencontrés.  
Pour éviter de recalculer les coups possibles via notre algorithme alphabeta amélioré, nous avons implémenté une fonction de memoïzation qui permet de stocker le meilleur coup pour un état de jeu déjà rencontré.


### Fonction de hashage des grilles

Afin de représenter au mieux l'état de jeu, que cela soit sur dodo ou gopher, nous avons choisi d'utiliser une fonction de hashage qui permet de stocker l'état de jeu sous forme de chaine de caractère. Cette chaine de caractère est ensuite utilisée comme clé dans un dictionnaire qui stocke les coups possibles pour un état de jeu donné.

Comment obtenir cette chaine de caractère?

Nous utilison la fonction `hashing()` qui prend en paramètre la grille actuelle des *GameValues*. Elle va parcourir la grille et à chaque case rencontrée, elle va ajouter dans la chaine de caractère de sortie le chiffre 0, 1 ou 2.
- 0 si la case est innocupée (`EMPTY`)
- 1 si la case est occupée par le joueur rouge (`ROUGE`)
- 2 si la case est occupée par le joueur bleu (`BLEU`)

Nous obtenons alors un grand nombre représentant l'état de la grille à un moment donné. Ce nombre est ensuite converti de la base 10 à la base 64 (fonction `base64()`) pour obtenir une chaine de caractère plus courte. Nous occupons ainsi moins de place en mémoire.

`hashing()` renvoie alors la chaine de caractère convertie précédemment en base 64. Pour information, nous utilisons l'alphabet suivant : `0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,`.

### Gestion des symetries

Une grille hexagonale comporte de nombreux axes de symétries (6 au total), il est donc utile d'implementer un calcule de ces symétries. Nous avons fait le choix d'implementer le calcule des symetries dans notre memoïzation, ainsi à chaque fois qu'une position est memoïzé, les 5 autres positions, symétriques et donc strictements équivalentes sont également ajouté au cache.
La fonction `reflexion()` permet de calculer l'ensemble des symetries pour une grille donnée.

### Fonction de memoïzation

La fonction `memoize()` est ensuite utilisée comme *decorator* de la fonction `alpha_beta()`. Elle permet à chaque coup calculé (ou non) par celui-ci de stocker le nouveau coup calculé dans un dictionnaire de la forme `Dict[str, Tuple[int, int]]` (pour gopher) ou `Dict[str, Tuple[Tuple[int, int],Tuple[int, int]]]` (pour dodo). La clé de ce dictionnaire est la chaine de caractère obtenue par la fonction `hashing()` et la valeur associée est le meilleur coup calculé pour cet état de jeu.

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