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

## Structure gobale 

Ce repository est composé de 7 fichiers : 
1. Le Readme ci-present
2. Le fichier `gnd.client.py` qui implemente les fonctionnalitées du serveur
3. Le fichier `gndserver.exe` qui doit etre executé pour lancer le serveur
4. Le fichier `affichage.py` qui implemente un affichage "userfriendly" des jeu
5. Le fichier `gopher.py` implementes notre algorithme pour Gopher
6. Le fichier `dodo.py` qui implemente notre algorithme pour le jeu Dodo
7. Le fichier `test_client.py` qui permet de jouer sur le serveur avec nos algorithmes





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
