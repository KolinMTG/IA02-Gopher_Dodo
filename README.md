# Projet IA02 

## Auteurs

Bastien Cuvillier, Colin Manyri

## Introduction

Ce projet est a été réalisé dans le cadre de la formation d'ingénieur en Génie informatique à l'Universitée de Technologie de Compiègne (UTC) et plus présisement dans le cadre de l'UV IA02 : Logique et Résolution de problèmes par la recherche.

L'objectif de ce projet était de coder des algorithmes capables de jouer aux jeux Gopher et Dodo de Mark Steere :
1. Site de Mark Steere : https://www.marksteeregames.com
2. Règles de Dodo : https://www.marksteeregames.com/Dodo_rules.pdf
3. Règles de Gopher : https://www.marksteeregames.com/Gopher_hex_rules.pdf

Par la suite, les differents algorithmes codés par les étudiants se sont affronté lors d'un tournoi résalisé par l'intermediaire d'un serveur en ligne. Les differents joueurs ont également un temps limité pour donner leurs coups, la rapidité et l'optimisation 
des algorithmes est donc de mise.

## Structure globale 

Ce repository est composé de 7 fichiers : 
1. Le fichier `Readme.md`, read me ci-present
2. Le fichier `gnd.client.py` qui implemente les fonctionnalitées du serveur
3. Le fichier `gndserver.exe` qui doit etre executé pour lancer le serveur
4. Le fichier `affichage.py` qui implemente un affichage "userfriendly" des jeu
5. Le fichier `gopher.py` implementes notre algorithme pour Gopher
6. Le fichier `dodo.py` qui implemente notre algorithme pour le jeu Dodo
7. Le fichier `test_client.py` qui permet de jouer sur le serveur avec nos algorithmes


## Choix de l'algorithme utilisé 

Pour notre projet nous voulons un algorithme capable de gagner des partie tout en gardant une grande rapidité d'action, necessaire pour ne pas etre en manque de temps contre d'autre joueur. Un algorithme `alpha-beta` que nous avons fortement optimisé nous a semblé être une option adaptée. Notement, la possibilité de choisir la profondeur de l'argorithme nous permet d'obtenir un algorithme efficasse et suffisement rapide pour repondre au exigences du concour (quitte a diminuer la profondeur).

Toujours dans une volonté d'ameliorer la performance de notre algorithme nous avons implementé de nombreuses optimisations que nous allons detailler :
- Le **calcule local des coups legaux** pour l'agorithme de gopher afin d'economiser du temps de calcule
- L'implementation d'une **fonction de memoïzation** pour l'algorithme alpha-beta
- L'implementation d'une **fonction de tri des noeuds** de l'arbre du alpha-beta pour faire les coupures alpha et beta plus rapidement comme decrit dans le Wikipédia en version allemande du alpha-beta : https://de.wikipedia.org/wiki/Alpha-Beta-Suche 
- L'implementation d'une **fonction de hashage** des grilles de Gopher et Dodo qui permet d'économiser de l'espace mémoire dans le cache des grilles memoïzées


## Choix de representation des données 

La representation de la grille hexagonale du jeu est plus ou moins imposé, en effets, nous devons renvoyer les coups au serveurs selon un système de coordonnée prédéfini. Par soucis de simplicité nous avons gardés ce système de coordonnée sur tout notre projet. Voici le sysmtème de coordonné choisit et la representation de la grille.

- Coordonnées : 
![Systeme de coordonnée presenté pour une grille de taille 7](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/grid_hex.png)
- Representation par une matrice : 
![Representation de la grille de taille 7 sous la forme d'une matrice 2D](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/matrix_hex.png)



## Calcule local des coups legaux pour Gopher 

Nous avons remarqué que les coups joué par les joueurs dans le cas de Gopher n'influances les coups légaux suivant que sur une partie locale de la grille, nous avons utilisé cette information pour ne recalculer que localement les coups légaux des differents joueurs. 

Exemple : 
Lorsqu'un joueur joue en position `(0,0)`, les coups legaux potentiellements changés sont les coups qui impliquent les cases voisines de la case remplie. Ils suffit donc de tester la legalité des 6 cases voisines, c'est à dire les cases `(1, 1), (1, 0), (0,-1), (-1, -1), (-1, 0), (0, 1)`


Stockage de l'information : nous avons choisit de stocker la liste des coups legaux dans un dictionnaire python `dico_legaux` de type `Dict[Case, bool]`, les coup legaux sont ont une value True. 
Ce système de stockage permet a la fois de tester si le coup existe (d'un point de vu de la grille donné, qui est de taille variable )

Dans `Gopher.py`, la fonction `init_dico_legaux_gopher()` permet d'initialiser les dictionnaires des coups légaux (tous les coup à False au début du jeu).
Puis la fonction update_dico_legaux() permet de mettre a jour les dictionnaires des coups légaux pour les deux joueur, après qu'un coup ai été joué. 
Cette fonction est appelé dans la fonction de mise a jours de l'environement `play_action()` qui permet de jouer une action donnée pour un joueur donnée et qui renvoie l'environement (c'est à dire l'ensemble des informations nécéssaire au jeu) modifié par le coup. 

Notre méthode utilisé pour determiner les coups légaux constitue un gain en temps de calcule non négligable. En effet, nous sommes alors restraint au testes de la legalité de au plus six voisins de la dernière action jouée. 
D'un point de vu plus quantitatif :

Une grille hexagonale de taille N, contient 3N(N-1)+1, nous laissons au lecteur le soin de la demonstration (vous pouvez raisonner sur la taille de la matrice donnée dans la partie `choix de la representation des données`).
Notre calcul permet donc de passer d'une complexité O(N^2), en effet 3N(N-1)+1 ~ N^2, à une complexité constante O(1) sur cette partie du calcule de complexité.


**Pourquoi ne pas utiliser la même technique sur Dodo ?**  
Dodo est un jeu, plus complexe car les jetons ne sont pas uniquement placés sur les cases mais déplacés d'une case à l'autre. Implementer stocker la liste de tous les coups possible sous forme d'un dictionnaire revient alors a stocker tout les couples de cases possibles ce qui prendrais enormement de place. De plus, la complexité de l'update de ce dictionnaire ne ferais finalement pas gagner beaucoup de temps par rapport au calcule naïf de la légalité des coups pour toutes les cases.

## Implementation de la memoïzation pour les joueurs 

## Fonction de tri des noeuds de l'alpha-beta 

Après avoir effectué des recherches sur les amélioration possible à apporter au alpha-beta, nous avons apris qu'il était possible de trier les noeuds (c'est-à-dire les coups testé) du alpha-beta. Ce tri de noeuds permet d'effectuer les coupures alpha ou beta plus rapidement, les branches les plus interessantes étant testées en premier. D'après le lien du Wikipedia donné plus tôt, cette implementation permet d'ameliorer le temps de calcule d'un facteur 10 : 

Voici ce qui est indiqué dans le Wiki :  

Algorithmus	Bewertungen	Cutoffs	Anteil der Cutoffs	Rechenzeit in Sekunden  
Minimax	28.018.531	0	0,00 %	134,87 s (Algorithme minmax)  
AlphaBeta	2.005.246	136.478	91,50 %	9,88 s (Algorithme alpha-beta)
AlphaBeta + Zugsortierung	128.307	27.025	99,28 %	0,99 s (Algorithme alpha-beta avec tri des noeuds)


## Fonction de hashage 

## Utilisation du server

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

## Utilisation du client

1. Copier le fichier `gndclient.py` dans votre répertoire de travail
2. Pour tester, copier le répertoire `test_client.py` dans votre répertoire de travail

```bash
# lancer le client
python test_client.py 12 toto totovelo
```
