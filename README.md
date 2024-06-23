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
- Le calcule uniquement local des coups legaux pour l'agorithme de gopher afin d'economiser du temps de calcule
- L'implementation d'une fonction de memoïzation pour l'algorithme alpha-beta
- L'implementation d'une fonction de tri des noeuds de l'arbre du alpha-beta pour faire les coupures alpha et beta plus rapidement comme decrit dans le Wikipédia en version allemande du alpha-beta : https://de.wikipedia.org/wiki/Alpha-Beta-Suche 
- L'implementation d'une fonction de hashage des grilles de Gopher et Dodo qui permet d'économiser de l'espace mémoire dans le cache des grilles memoïzées


## Choix de representation des données 
- Coordonnées : 
![alt text](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/grid_hex.png)
- Representation par une matrice : 
![alt text](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/matrix_hex.png)


## Calcule local des coups legaux pour Gopher 

Nous avons remarqué que les coups joué par les joueurs dans le cas de Gopher n'influances les coups légaux suivant que sur une partie locale de la grille, nous avons utilisé cette information pour ne recalculer que localement les coups légaux des differents joueurs. 

Exemple : 
Lorsqu'un joueur joue en position `(0,0)`, les coups legaux potentiellements changés sont les coups qui impliquent les cases voisines de la case remplie. Ils suffit donc de tester la legalité des 6 cases voisines, c'est à dire les cases `(1, 1), (1, 0), (0,-1), (-1, -1), (-1, 0), (0, 1)`


Pourquoi ne pas utiliser la même technique sur Dodo ? 
Dodo est un jeu, plus complexe car les jetons ne sont pas uniquement placés sur les cases mais déplacés d'une case à l'autre. Implementer stocker la liste de tous les coups possible sous forme d'un dictionnaire revient alors a stocker tout les couples de cases possibles ce qui prendrais enormement de place. De plus, la complexité de l'update de ce dictionnaire ne ferais finalement pas gagner beaucoup de temps par rapport au calcule naïf de la légalité des coups pour toutes les cases.



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
