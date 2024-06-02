#! ---------------------- IMPORTS ---------------------- !#
import numpy as np
from typing import Union, List, Tuple, Dict
from numpy.typing import NDArray
import random as rd
import multiprocessing as mp
from math import *
import itertools as it
import copy
#import new_affichage as aff
import matplotlib.pyplot as plt


#! ---------------------- CONSTANTES ---------------------- !#
INF = +inf
EMPTY = 0
ROUGE = 1
BLEU = 2
NDEF = -1 #case non définie


#! ---------------------- TYPES ---------------------- !#
Player = int #Joueur : donc ROUGE ou BLEU
GameValue = int #valeur d'une case : donc NDEF, EMPTY, ROUGE, BLEU
Grid = NDArray[2] #La grille de jeu, est un tableau numpy 2D de GameValue

Cell = Tuple[int, int] #Coordonnées d'une case
CellMat = Cell  #Coordonnées d'une case dans la matrice
CellHex = Cell #Coordonnées d'une case dans l'affichage hexagonal a fournir au serveur

ActionGopher = CellHex #Action du gopher
ActionDodo = Tuple[CellHex, CellHex] #Action du dodo
Action = Union[ActionGopher, ActionDodo] #Action du joueur

DictConv = Dict[CellMat, CellHex] #Dictionnaire de conversion de coordonnées
DictLegauxGopher = Dict[Player, Dict[ActionGopher, bool]] #Dictionnaire des coups légaux
DictLegauxDodo = Dict[Player, Dict[ActionDodo, bool]] #Dictionnaire des coups légaux

State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int

#! ---------------------- FONCTIONS ---------------------- !#

#!   /!\ le dico_conversion contient des clés de type Cell_hex et des valeurs de type Cell_mat /!\
def init_grille_gopher(taille_grille: int) -> Tuple[Grid, Dict]: #!OK
    """Initialise la grille de jeu avec les pions au bon endroit. Et initialisation du dico de conversion."""
    taille_array = 2*taille_grille+1
    dico_conversion = {}
    grille = np.full((taille_array, taille_array), NDEF)

    #! initialisation du dico de conversion pour les coordonnées des cases de jeu
    compteur = taille_grille
    for i in range(taille_grille): #remplir la premiere partie
        for j in range(compteur, taille_array):
            dico_conversion[(j-taille_grille, taille_grille-i)] = (i,j)
        compteur -=1
    for j in range(taille_array): #remplir la ligne du milieu
        dico_conversion[(j-taille_grille,0)] = (taille_grille,j)
    compteur = 1
    for i in range(taille_grille+1, taille_array): #remplir le reste
        for j in range(taille_array-compteur):
            dico_conversion[(j-taille_grille, taille_grille-i)] = (i,j)
        compteur +=1
    
    for val in dico_conversion.values(): #initialisation de la grille : toutes les cases qui ne sont pas en clé du dico n'existent pas
        grille[val[0]][val[1]] = EMPTY
    return grille, dico_conversion

#!test
# grille, dico_conversion = init_grille_gopher(6)
# print(grille)
# print(dico_conversion)



def existe(dico_conversion:Dict, pos:CellHex) -> bool: #!OK
    """Renvoie True si la case existe et False sinon"""
    return pos in dico_conversion.keys()

#!test
# grille, dico_conversion = init_grille_gopher(6)
# print(existe(dico_conversion, (0,0))) #normalement True
# print(existe(dico_conversion, (0,7))) #normalement False


def voisins(dico_conversion : DictConv, pos:CellHex) -> List[CellHex]: #!OK 
    """renvoie la liste des voisins d'une case donnée de grid_pos, attention au types de coordonnées"""
    x, y = pos #(x, y) = (0, 0) pour la case du milieu
    liste_absolue = [(x, y-1), (x, y+1), (x+1, y), (x-1, y), (x+1, y+1), (x-1, y-1)]
    liste_voisins = []
    for coord in liste_absolue: 
        if existe(dico_conversion, coord): #l'avantage est que si la case n'existe pas, on le sait car elle n'est pas dans le dico
            liste_voisins.append(coord)
    return liste_voisins

#!test
# grille, dico_conversion = init_grille_gopher(6)
# print(voisins(dico_conversion, (0,0))) #normalement [(7, 6), (5, 6), (6, 7), (6, 5), (5, 7), (7, 5)]

def init_dico_legaux_gopher(grille:Grid, dico_conversion:DictConv) -> DictLegauxGopher: #! OK
    """Initialise le dictionnaire des coups légaux pour le gopher"""
    dico_legaux = {ROUGE:{}, BLEU:{}}
    for joueur in dico_legaux.keys():
        for action in dico_conversion.keys():
            dico_legaux[joueur][action] = False
    return dico_legaux

def play_action(grille:Grid, dico_conversion:DictConv, action:ActionGopher, joueur:Player) -> Grid: #
    """Joue un coup pour un joueur donné, /!\ verifier que l'action est légale, l'action est de type Cell_hex"""
    cell_mat = dico_conversion[action]
    grille[cell_mat[0]][cell_mat[1]] = joueur
    return grille

#!test
# grille, dico_conversion = init_grille_gopher(6)
# grille = play_action(grille, dico_conversion, (0,0), ROUGE)
# aff.draw_hex_grid(grille) #normalement la case (0,0) est rouge


def est_legal(grille:Grid,dico_conversion: Dict , action:ActionGopher, joueur : Player) -> bool:
    """Renvoie True si le coup est légal pour une grille donnée et False sinon"""

    if not(existe(dico_conversion, action)): #si la case n'existe pas alors le coup n'est pas légal
        # print("case n'existe pas")
        return False
    
    cell_cible = dico_conversion[action] #cell est une CellMat
    if grille[cell_cible[0]][cell_cible[1]] != EMPTY: #si la case n'est pas vide alors le coup n'est pas légal
        # print("case non vide")
        return False
    nb_voisin = 0
    print(action)
    print("voisins : ", voisins(dico_conversion, action))
    for cell_voisin in voisins(dico_conversion, action): #on regarde les cases voisines
        if grille[dico_conversion[cell_voisin][0]][dico_conversion[cell_voisin][1]] == joueur:
            # print("deja une case du joueur sur une case voisine")
            return False
        
        elif grille[dico_conversion[cell_voisin][0]][dico_conversion[cell_voisin][1]] != EMPTY:
            nb_voisin +=1 #on a trouvé une case adeverse
            if nb_voisin == 2: #si on a trouvé plus d'une case adverse alors le coup n'est pas légal
                # print("au moins deux cases adverse trouvées")
                return False

    return nb_voisin == 1 #si on a trouvé une case adverse exactement alors le coup est légal



#!test
# grille, dico_conversion = init_grille_gopher(6)
# grille = play_action(grille, dico_conversion, (0,0), ROUGE)
# print(est_legal(grille, dico_conversion, (0,0), ROUGE)) #normalement False
# print(est_legal(grille, dico_conversion, (0,1), ROUGE)) #normalement False
# print(est_legal(grille, dico_conversion, (0,1), BLEU)) #normalement True


def liste_coup_legaux(dico_legaux:DictLegauxGopher, joueur:Player) -> List[ActionGopher]: #! OK
    """Renvoie la liste des coups légaux pour un joueur donné"""
    return [action for action in dico_legaux[joueur].keys() if dico_legaux[joueur][action] == True]

def update_dico_legaux(dico_legaux:DictLegauxGopher, grille:Grid, dico_conversion:DictConv, action:ActionGopher) -> DictLegauxGopher: # ? A REVOIR
    """Met à jour le dictionnaire des coups légaux pour un joueur donné"""

    for joueur in dico_legaux.keys():
        dico_legaux[joueur][action] = False #on ne peut pas rejouer la case jouée en action
        for cell in voisins(dico_conversion, action): # update des cases voisines de la case jouée
            if est_legal(grille, dico_conversion, cell, joueur):

                dico_legaux[joueur][cell] = True
            else :
                dico_legaux[joueur][cell] = False
    return dico_legaux




def score_final(dico_legaux: DictLegauxGopher) -> int: #!OK
    """Renvoie le score final, renvoie 0 si la partie n'est pas fini, 1 si le joueur ROUGE a gagné, -1 si le joueur BLEU a gagné"""
    if liste_coup_legaux(dico_legaux, ROUGE) == []: return -1
    if liste_coup_legaux(dico_legaux, BLEU) == []: return 1
    return 0



def boucle_rd_rd(): # ! boucle de jeu OK
    """Boucle de jeu pour deux joueurs aléatoires"""

    grille, dico_conversion = init_grille_gopher(6)
    actions_possible = list(dico_conversion.keys())
    joueur = ROUGE
    action_debut = rd.choice(actions_possible)
    print("Joueur de debut : ", joueur)
    print("Action de debut : ", action_debut)
    grille = play_action(grille, dico_conversion, action_debut, joueur)
    dico_legaux = init_dico_legaux_gopher(grille, dico_conversion)
    # print("DicoLegaux: ", dico_legaux)
    dico_legaux = update_dico_legaux(dico_legaux, grille, dico_conversion, action_debut)
    # print("DicoLegaux UPDATE : ", dico_legaux)
    joueur = ROUGE if joueur == BLEU else BLEU
    while True:
        print("Joueur : ", joueur)
        actions_legales = liste_coup_legaux(dico_legaux, joueur)
        print("Liste coup legaux : ", liste_coup_legaux(dico_legaux, joueur))
        if actions_legales == []:
            break
        action = rd.choice(actions_legales)
        print("Action : ", action)
        grille = play_action(grille, dico_conversion, action, joueur)
        dico_legaux = update_dico_legaux(dico_legaux, grille, dico_conversion, action)
        
        
        
        joueur = ROUGE if joueur == BLEU else BLEU

        if score_final(dico_legaux) != 0:
            break
    #aff.draw_hex_grid(grille)
    return score_final(dico_legaux)

#!test
#print(boucle_rd_rd())

### Fonctions de hashage et de déhashage ###

def hashing(gameValueGrid:list[list[GameValue]]) -> str:
    """Fonction de hashage d'une grille"""
    hashage=""
    for Dimension in gameValueGrid:
        for GameValue in Dimension:
            if GameValue == ROUGE: #1
                hashage+="1"
            elif GameValue == BLEU: #2
                hashage+="2"
            elif GameValue == EMPTY: #0
                hashage+="0"
            else: #cas NDEF
                hashage+="3"
    return (str(hex(int(hashage)))[2:])

def dehashing(hashage:str,taille:int) -> list[list[GameValue]]:
    """Fonction de dehashage d'une grille"""
    gameValueGrid=[]
    hashage=str(int(hashage,16))
    for i in range(taille*2+1):
        gameValueGrid.append([])
        for j in range(taille*2+1):
            if hashage[0]=="1":
                gameValueGrid[i].append(ROUGE)
            elif hashage[0]=="2":
                gameValueGrid[i].append(BLEU)
            elif hashage[0]=="0":
                gameValueGrid[i].append(EMPTY)
            else:
                gameValueGrid[i].append(NDEF)
            hashage=hashage[1:]
    return(gameValueGrid)

#!test

def state_generator(taille:int) -> Grid:
    """Génère un état de jeu aléatoire"""
    grille, dico_conversion = init_grille_gopher(taille)
    dico_legaux = init_dico_legaux_gopher(grille, dico_conversion)
    actions_possible = list(dico_conversion.keys())
    joueur = ROUGE
    action_debut = rd.choice(actions_possible)
    grille = play_action(grille, dico_conversion, action_debut, joueur)
    dico_legaux = update_dico_legaux(dico_legaux, grille, dico_conversion, action_debut)
    joueur = ROUGE if joueur == BLEU else BLEU
    while True:
        actions_legales = liste_coup_legaux(dico_legaux, joueur)
        if actions_legales == []:
            break
        action = rd.choice(actions_legales)
        grille = play_action(grille, dico_conversion, action, joueur)
        dico_legaux = update_dico_legaux(dico_legaux, grille, dico_conversion, action)
        joueur = ROUGE if joueur == BLEU else BLEU
        if score_final(dico_legaux) != 0:
            break
    return grille

def test_hashage_dehashage(taille:int) -> bool:
    """Teste la fonction de hashage et de déhashage"""
    grille=state_generator(taille)
    hashage=hashing(grille)
    grille2=dehashing(hashage,taille)
    print(hashage)
    bool_test=(grille==grille2)
    for elt in bool_test:
        for booleen in elt:
            if not(booleen):
                return False
    return True
 
print(test_hashage_dehashage(15))