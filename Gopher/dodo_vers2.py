import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Union, List, Tuple, Dict
import pprint
import tkinter as tk
import random as rd
import multiprocessing as mp
from numpy.typing import NDArray
from math import *
import itertools as it
import copy
import affichage as aff
# import affichage as aff
# Types de base utilisés par l'arbitre
Grid = NDArray# Grille de jeu (tableau 2D de cases), 
#chaque case est un tuple (x, y) qui permet d'optenir la Value de la case dans la Grid_value
GameValue = int # Valeur d'une case (0, 1 ou 2)
Cell = Tuple[int, int]
Cell_hex = Tuple[int, int] # coordonnées hexagonales c'est a dire celles du prof, qui doivent etre données au serveur
Cell_mat = Tuple[int, int] # coordonnées de type indice (x,y) d'une matrice numpy, acceder a une valeur de grille avec grille[x][y]
Case = Tuple[Cell, GameValue]


ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int
DirectionJeu = Dict #contient un vecteur direction qui selon lequel chaque joueur doit progresser pour gagner
# DicoLegaux = Dict[Dict]


INF = +inf
EMPTY = 0 #à utiliser pour les cases vides
ROUGE = 1
BLEU = 2 
NDEF = -1 # a utiliser pour les cases qui n'existes pas



#!   /!\ le dico_conversion contient des clés de type Cell_hex et des valeurs de type Cell_mat /!\
def init_grille_dodo(taille_grille: int) -> Tuple[Grid, Dict, DirectionJeu]: #!OK
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
    
    for key in dico_conversion.keys(): #initialisation de la grille : toutes les cases qui ne sont pas en clé du dico n'existent pas
        x_cell, y_cell = dico_conversion[key] #! type de dico_conversion[key] : Cell_mat
        if key[0]+key[1] >= taille_grille-1: #on remplit la grille avec les pions
            grille[x_cell][y_cell] = BLEU
        elif key[0]+key[1] <= -taille_grille+1: #on remplit la grille avec les pions
            grille[x_cell][y_cell] = ROUGE
        else:
            grille[x_cell][y_cell] = EMPTY #on remplit la grille avec les cases vides
    return grille, dico_conversion, {ROUGE: [(1,0),(0,1), (1,1)], BLEU: [(-1,0), (-1, -1), (0,-1)]}

#!test
grille, dico_conversion, direction = init_grille_dodo(3)
# print(grille)
# print(dico_conversion)
aff.afficher_hex(grille, dico_conversion)


def existe(dico_conversion:Dict, pos:Cell) -> bool: #!OK
    """Renvoie True si la case existe et False sinon"""
    return pos in dico_conversion.keys()

# # #!test
# print(existe(init_grille_dodo(6)[1], (0, 0))) #normalement True
# print(existe(init_grille_dodo(6)[1], (7, 0))) #normalement False


def voisins(dico_conversion : Dict, pos:Cell_hex) -> List[Cell_hex]:
    """renvoie la liste des voisins d'une case donnée de grid_pos"""
    x, y = pos #(x, y) = (0, 0) pour la case du milieu
    liste_absolue = [(x, y-1), (x, y+1), (x+1, y), (x-1, y), (x+1, y+1), (x-1, y-1)]
    liste_voisins = []
    for coord in liste_absolue: 
        if existe(dico_conversion, coord): #l'avantage est que si la case n'existe pas, on le sait car elle n'est pas dans le dico
            liste_voisins.append(coord)
    return liste_voisins 

# #!test
# print(voisins(init_grille_dodo(6)[1], (6,6)))
# print(voisins(init_grille_dodo(6)[1], (0,0)))
# print(voisins(init_grille_dodo(6)[1], (3, -3)))


def est_legal(grille : Grid, dico_conversion : Dict, direction: DirectionJeu, action : ActionDodo, joueur : Player) -> bool:
    """Renvoie True si le coup est légal pour une grille donnée et False sinon"""
    cell_depart, cell_arrivee = action

    #!verifier que la cellule de depart et d'arrivee existent
    if not existe(dico_conversion, cell_depart) or not existe(dico_conversion, cell_arrivee):
        return False

    #! verifier si la cell de depart appartient au joueur
    if grille[dico_conversion[cell_depart][0]][dico_conversion[cell_depart][1]] != joueur:
        return False
    
    #! verifier si la cell d'arrivee est vide
    if grille[dico_conversion[cell_arrivee][0]][dico_conversion[cell_arrivee][1]] != EMPTY:
        return False
    
    #! verifier si la cell de depart est adjacente à la cell d'arrivée et dans le bon sens :
    for dir_x, dir_y in direction[joueur]: 
        if cell_arrivee == (cell_depart[0]+dir_x, cell_depart[1]+dir_y): #on s'est déplacé dans une direction autorisée
            return True 
    return False


def liste_coup_legaux(grille: Grid, dico_conversion: Dict, direction: DirectionJeu, joueur: Player) -> List[ActionDodo]:
    """Renvoie la liste des coups légaux pour un joueur donné"""
    liste_coups = []
    for cell_depart in dico_conversion.keys():
        for cell_arrivee in voisins(dico_conversion, cell_depart):
            if est_legal(grille, dico_conversion, direction, (cell_depart, cell_arrivee), joueur):
                liste_coups.append((cell_depart, cell_arrivee))
    return liste_coups


def play_action(grille: Grid, dico_conversion: Dict, action: ActionDodo, joueur: Player) -> Grid:
    """Renvoie la grille après avoir joué un coup"""
    cell_depart, cell_arrivee = action
    grille[dico_conversion[cell_depart][0]][dico_conversion[cell_depart][1]] = EMPTY
    grille[dico_conversion[cell_arrivee][0]][dico_conversion[cell_arrivee][1]] = joueur
    return grille


def score(grille, dico_conversion, direction, joueur_max) -> Score:

    if joueur_max == ROUGE:
        return -len(liste_coup_legaux(grille, dico_conversion, direction, joueur_max)) + len(liste_coup_legaux(grille, dico_conversion, direction, BLEU))
    else:
        return -len(liste_coup_legaux(grille, dico_conversion, direction, joueur_max)) + len(liste_coup_legaux(grille, dico_conversion, direction, ROUGE))

def final(grille, dico_conversion, direction) -> float:
    if len(liste_coup_legaux(grille, dico_conversion, direction, ROUGE)) == 0 :
        return -INF
    elif len(liste_coup_legaux(grille, dico_conversion, direction, BLEU)) == 0:
        return INF
    else :
        return 0




# #!test
# grille, dico_conversion, direction = init_grille_dodo(6)
# # print(grille)
# grille = play_action(grille, dico_conversion, ((2,3), (1,2)), BLEU)
# aff.afficher_hex(grille, dico_conversion)


def rd_rd_dodo() -> float:
    """fait jouer deux randoms pour le joueur donné"""
    grille, dico_conversion, direction = init_grille_dodo(3)

    joueur = ROUGE
    while True:
        liste_coups = liste_coup_legaux(grille, dico_conversion, direction, joueur)
        coup = rd.choice(liste_coups)
        grille = play_action(grille, dico_conversion, coup, joueur)

        if final(grille, dico_conversion, direction):
            # aff.afficher_hex(grille, dico_conversion)
            break;
        if joueur == ROUGE : joueur = BLEU
        else : joueur = ROUGE
    

    return final(grille, dico_conversion, direction)

#!test

X = [i for i in range(1, 11)]
Y = [0 for i in range(1, 11)]
for i in range(100):
    boucle = 0
    for i in range(10):
        if rd_rd_dodo() == INF:
            boucle += 1
    Y[boucle] += 1
plt.plot(X, Y)
plt.show()



def alpha_beta(grid : Grid,dico_conversion : DictConv, player_max : Player, dico_legaux: DictLegauxGopher, depth, alpha, beta) -> Tuple[Score, ActionGopher]:

    if depth == 0 or final(player_max, dico_legaux):
        return evaluation(dico_legaux, player_max), None

    if player_max == ROUGE:
        best_value = -INF
        best_action = None
        for action in trier_actions(grid, dico_conversion, liste_coup_legaux(dico_legaux, ROUGE),dico_legaux, player_max):#! pas d'erreur dans trier_actions
            new_dico_legaux = copy.deepcopy(dico_legaux)
            new_dict_temp = copy.deepcopy(dico_legaux)
            # new_grid, new_dico_legaux = play_action(grid, dico_conversion, action, ROUGE, dico_legaux)
            new_grid, new_dico_legaux = play_action(grid, dico_conversion, action, ROUGE, new_dict_temp)
            new_dict_temp = copy.deepcopy(new_dico_legaux)
            # new_value, _ = alpha_beta(new_grid,dico_conversion, BLEU, new_dico_legaux, depth - 1, alpha, beta)
            new_value, _ = alpha_beta(new_grid,dico_conversion, BLEU, new_dict_temp, depth - 1, alpha, beta)
            if new_value > best_value:
                best_value = new_value
                best_action = action
            alpha = max(alpha, new_value)
            if beta <= alpha:
                break  # Coupe bêta
        return best_value, best_action
    else: #! problème quelquepart dans bleu
        min_value = INF
        best_action = None
        for action in trier_actions(grid, dico_conversion, liste_coup_legaux(dico_legaux, BLEU),dico_legaux, player_max): #! pas d'erreur dans trier_actions
            new_dico_legaux = copy.deepcopy(dico_legaux)
            new_dict_temp = copy.deepcopy(dico_legaux)
            # new_grid, new_dico_legaux = play_action(grid, dico_conversion, action, BLEU, dico_legaux)
            new_grid, new_dico_legaux = play_action(grid, dico_conversion, action, BLEU, new_dict_temp)
            new_dict_temp = copy.deepcopy(new_dico_legaux)
            # new_value, _ = alpha_beta(new_grid,dico_conversion, ROUGE, new_dico_legaux, depth - 1, alpha, beta)
            new_value, _ = alpha_beta(new_grid,dico_conversion, ROUGE, new_dict_temp, depth - 1, alpha, beta)
            if new_value < min_value:
                min_value = new_value
                best_action = action
            beta = min(beta, new_value)
            if beta <= alpha:
                break  # Coupe alpha
        return min_value, best_action

#TODO A FAIRE : 
#TODO OBTERNIR LE SERVEUR DE TEST
#TODO COMMENCER DODO (COUPS LEGAUX, MINMAX, SOUS-PROBLEMES) => ATTENTION HEURISTIQUE! 
#TODO IMPLEMENTER MULTIPROCESSING (MULTITHREADING)

#TODO IMPLEMENTER DICTIONNAIRE COUP LEGAUX LOCAUX
#TODO TERMINER SOUS-PROBLEMES
#TODO IMPLEMENTER LES FONCTION DE HASHAGE
