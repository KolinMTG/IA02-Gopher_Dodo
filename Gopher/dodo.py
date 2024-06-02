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


INF = +inf
EMPTY = 0 #à utiliser pour les cases vides
ROUGE = 1
BLEU = 2 
NDEF = -1 # a utiliser pour les cases qui n'existes pas

def transform_to_hexagonal_grid(data):
    rows, cols = data.shape
    new_data = np.full((rows, cols + rows // 2), -1)

    for i in range(rows):
        if i % 2 == 0:
            new_data[i, i // 2: i // 2 + cols] = data[i]
        else:
            new_data[i, (i + 1) // 2: (i + 1) // 2 + cols] = data[i]
    
    return new_data

def draw_hex_grid(data):
    data = transform_to_hexagonal_grid(data)

    # Constants for the hexagon geometry
    hex_height = np.sqrt(3)
    hex_width = 2
    vert_dist = hex_height
    horiz_dist = 1.5

    fig, ax = plt.subplots(1)
    ax.set_aspect('equal')

    # Colors for different cell values
    colors = {2: 'red', 1: 'blue', 0: 'white'}

    # Draw the hexagons
    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            value = data[row, col]
            if value == -1:
                continue
            color = colors.get(value, 'white')
            x = col * horiz_dist
            y = row * vert_dist * 0.87  # Using 0.87 to adjust for the vertical spacing of hexagons
            hexagon = patches.RegularPolygon((x, y), numVertices=6, radius=1, orientation=np.radians(30),
                                             edgecolor='black', facecolor=color)
            ax.add_patch(hexagon)

    plt.xlim(-1, data.shape[1] * horiz_dist + 1)
    plt.ylim(-1, data.shape[0] * vert_dist + 1)
    plt.axis('off')
    plt.show()

#!   /!\ le dico_conversion contient des clés de type Cell_hex et des valeurs de type Cell_mat /!\
def init_grille_dodo(taille_grille: int) -> Tuple[Grid, Dict]: #!OK
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
        if key[0]+key[1] >= taille_grille: #on remplit la grille avec les pions
            grille[x_cell][y_cell] = BLEU
        elif key[0]+key[1] <= -taille_grille: #on remplit la grille avec les pions
            grille[x_cell][y_cell] = ROUGE
        else:
            grille[x_cell][y_cell] = EMPTY #on remplit la grille avec les cases vides
    return grille, dico_conversion

#!test
# grille, dico_conversion = init_grille_dodo(7)
# print(grille)
# print(dico_conversion)


def init_dico_legaux(dico_conversion:Dict) -> Tuple[Dict, Dict]: #!OK
    """Initialise les dictionnaires des coup legaux des cases de jeu"""
    dict_rouge = {}
    dict_bleu = {}
    for case in dico_conversion.keys():
        dict_rouge[case] = False
        dict_bleu[case] = False
    return dict_rouge, dict_bleu

# # #!test
# # dict_legaux_rouge, dict_legaux_bleu = init_dico_legaux(init_grille(7)[1])


def existe(dico_conversion:Dict, pos:Cell) -> bool: #!OK
    """Renvoie True si la case existe et False sinon"""
    return pos in dico_conversion.keys()

# # #!test
# print(existe(init_grille_dodo(6)[1], (0, 0))) #normalement True
# print(existe(init_grille_dodo(6)[1], (7, 0))) #normalement False


def voisins(dico_conversion : Dict, pos:Cell_hex) -> List[Cell_mat]:
    """renvoie la liste des voisins d'une case donnée de grid_pos"""
    x, y = pos #(x, y) = (0, 0) pour la case du milieu
    liste_absolue = [(x, y-1), (x, y+1), (x+1, y), (x-1, y), (x+1, y+1), (x-1, y-1)]
    liste_voisins = []
    for coord in liste_absolue: 
        if existe(dico_conversion, coord): #l'avantage est que si la case n'existe pas, on le sait car elle n'est pas dans le dico
            liste_voisins.append(dico_conversion[coord])
    return liste_voisins 

# #!test
# print(voisins(init_grille_dodo(6)[1], (6,6)))
# print(voisins(init_grille_dodo(6)[1], (0,0)))
# print(voisins(init_grille_dodo(6)[1], (3, -3)))


# def est_legal(grille:Grid,dico_conversion: Dict , action:ActionGopher, joueur : Player) -> bool:
#     """Renvoie True si le coup est légal pour une grille donnée et False sinon"""
#     cell = dico_conversion[action]
#     case_cible = grille[cell[0]][cell[1]]
#     if not(existe(dico_conversion, action)): #si la case n'existe pas alors le coup n'est pas légal
#         return False
#     if case_cible[1] != EMPTY: #si la case n'est pas vide alors le coup n'est pas légal
#         return False
    
#     nb_case_adverse = 0
    
#     cases_voisins = voisins(grille, dico_conversion, action)
#     for case in cases_voisins:
#         if case[1] == joueur:
#             return False
#         elif case[1] != EMPTY: #si la case est adverse alors on incrémente le compteur
#             nb_case_adverse += 1
#             if nb_case_adverse >= 2:
#                 return False
#     return nb_case_adverse > 0




def rotation(grille : Grid, dico_conversion : Dict) -> List[Grid]: #! A REVOIR 
    """effectue une rotation de 60° de la grille hexagonale, utile pour les symétries"""
    taille_grille = len(grille)//2
    rot_1 = init_grille_dodo(taille_grille)[0]
    rot_2 = copy.deepcopy(rot_1)
    rot_3 = copy.deepcopy(rot_1)
    rot_4 = copy.deepcopy(rot_1)
    rot_5 = copy.deepcopy(rot_1)
    

    #!rotation 60°
    for cell in dico_conversion.keys(): #enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1]-cell[0])
        rot_1[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[dico_conversion[cell][0]][dico_conversion[cell][1]]

    #!rotation 120°
    for cell in dico_conversion.keys(): #enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1]-cell[0])
        rot_2[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_1[dico_conversion[cell][0]][dico_conversion[cell][1]]

    #!rotation 180°
    for cell in dico_conversion.keys(): #enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1]-cell[0])
        rot_3[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_2[dico_conversion[cell][0]][dico_conversion[cell][1]]
    
    #!rotation 240°
    for cell in dico_conversion.keys(): #enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1]-cell[0])
        rot_4[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_3[dico_conversion[cell][0]][dico_conversion[cell][1]]
    
    #!rotation 300°
    for cell in dico_conversion.keys(): #enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1]-cell[0])
        rot_5[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_4[dico_conversion[cell][0]][dico_conversion[cell][1]]

    return [grille, rot_1, rot_2, rot_3, rot_4, rot_5]
    
# #!test
for rot in rotation(init_grille_dodo(6)[0], init_grille_dodo(6)[1]):
    print("******************************ROT******************************")
    print(rot)
    draw_hex_grid(rot)




# def est_legal(grille : Grid, dico_conversion : Dict, action : ActionDodo, joueur : Player) -> bool:
#     """Renvoie True si le coup est légal pour une grille donnée et False sinon"""
#     cell_depart, cell_arrivee = action
#     #! verifier si la cell de depart appartient au joueur
#     if dico_conversion[cell_depart][1] != joueur:
#         print("La case de départ n'appartient pas au joueur")
#         return False
#     #! verifier si la cell d'arrivee est vide
#     if dico_conversion[cell_arrivee][1] != EMPTY:
#         print("La case d'arrivée n'est pas vide")
#         return False

#     #! verifier si la cell d'arrivee est un voisin de la cell de depart au sens de dodo




def reflexion(grille : Grid, dico_conversion : Dict) -> List[Grid]:
    """effectue les 6 reflexions possible d'une grille donnée, utile pour les symétries"""
    taille_grille = len(grille)//2 
    ref_1 = init_grille_dodo(taille_grille)[0]
    ref_2 = copy.deepcopy(ref_1)
    ref_3 = copy.deepcopy(ref_1)
    ref_4 = copy.deepcopy(ref_1)
    ref_5 = copy.deepcopy(ref_1)
    ref_6 = copy.deepcopy(ref_1)

    for cell in dico_conversion.keys(): #enumeration de tout les element de la matrice

        #! symetrie axiale verticale
        new_cell = (cell[1], cell[0])
        ref_1[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[dico_conversion[cell][0]][dico_conversion[cell][1]]
    
        #! symetrie axiale horizontale
        new_cell = (-cell[1], -cell[0])
        ref_2[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[dico_conversion[cell][0]][dico_conversion[cell][1]]

        #! symetrie axe bleu
        new_cell = (-cell[0], cell[1]-cell[0])
        ref_3[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[dico_conversion[cell][0]][dico_conversion[cell][1]]

        #! symetrie axe rouge
        new_cell = (cell[0] - cell[1], -cell[1])
        ref_4[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[dico_conversion[cell][0]][dico_conversion[cell][1]]

         #! autre axe 
        new_cell = (cell[0], cell[0]-cell[1])
        ref_5[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[dico_conversion[cell][0]][dico_conversion[cell][1]]
    
        #! autre axe 
        new_cell = (cell[1] - cell[0], cell[1])
        ref_6[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[dico_conversion[cell][0]][dico_conversion[cell][1]]

    return [ref_1, ref_2, ref_3, ref_4, ref_5, ref_6]


#!test
# for ref in reflexion(init_grille_dodo(7)[0], init_grille_dodo(7)[1]):
#     print("******************************REF******************************")
#     print(ref)
#     draw_hex_grid(ref)



#! def grid_to_hash(grille:Grid) -> str:
#!     """Renvoie le hash d'une grille donnée"""

#! pour faire ca on prend la grille, pour chaque element de la grille, on transrofme en binaire sur 2 bits 
#! on recup aussi la taille de la grille, qu on code sur 8 bits (histoire d'avoir de la marge, apres on peut aussi prendre 6, je pense qu'on depassera jamais 64 en taille de grille)
#! chacun de ces codes binaires sont concaténés pour former le hash de la grille sous forme binaire,
#! on convertit ensuite ce hash en hexadécimal pour avoir un hash plus lisible
#! on renvoie l'hexa sous forme d'un string

#! def hash_to_grid(hash:str) -> Grid:
#!     """Renvoie la grille correspondant à un hash donné"""


# def memoize(fonction):
#     cache = {} # closure
#     def g(state: State, player: Player):
#         if state in cache:
#             # print("Appel memoize")
#             return cache[state]
#         val = fonction(state, player)
#         cache[state] = val
#         return val
#     return g

# @memoize
# def minmax_action_gopher(grid : Grids, player : Player) -> tuple[Score, ActionGopher]:
#     best_value_max = -INF
#     best_value_min = INF
#     best_action = None

#     res = final(grid) #renvoie le score si la partie est finie, 0 sinon
#     if res:
#         return res, None

#     for action in liste_coup_legaux(grid):
#         grid_suiv =(grid[0], play_action(grid, action, player))
#         if player == ROUGE:
#             value = minmax_action_gopher(grid_suiv, BLEU)[0]
#             if value > best_value_max:
#                 best_value_max = value
#                 best_action = action

#         elif player == BLEU:
#             value = minmax_action_gopher(grid_suiv, ROUGE)[0]
#             if value < best_value_min:
#                 best_value_min = value
#                 best_action = action
#     if player == ROUGE:
#         return best_value_max, best_action
#     else:
#         return best_value_min, best_action



# ### SOUS PROBLEMES GOPHER ###    


# def minmax_sousprob_gopher(grid: Grids, player: Player,centre: tuple[int,int],taille:int) -> tuple[Score,ActionGopher]:
#     '''Renvoie le meilleur coup possible dans le cas d'un sous-problème sur Gopher'''
#     newgrid = []
#     for i in range(centre[0]-taille,centre[0]+taille):
#         for j in range(centre[1]-taille,centre[1]+taille):
#             if grid[i][j] != None:
#                 newgrid.append(grid[i][j]) #Une erreur est possible ici car grid[i][j] n'éxiste pas forcément.
#     return minmax_action_gopher(newgrid,player)

# def action_all_sous_prob(grid: Grids, player: Player, taille: int) -> list[tuple[Score,ActionGopher]]:
#     '''Réalise l'ensemble des sous_problèmes centrés sur les coups légaux et de taille taille'''
    
#     liste_action = []
    
#     for centres in est_legal(grid,player):
#         liste_action.append(minmax_sousprob_gopher(grid,player,centres,taille))
    
#     ponderation_action={}
    
#     for actions in liste_action:
#         if actions not in ponderation_action:
#             ponderation_action[actions] = 1
#         else:
#             ponderation_action[actions] += 1
    
#     best_action=ponderation_action[0]
#     for pond_action in ponderation_action.items():
#         if pond_action[1]>best_action[1]:
#             best_action=pond_action[0]
            
#     return best_action

# def test_sous_prob(actionMinMax: tuple[Score,ActionGopher], actionSousProblèmes: tuple[Score,ActionGopher]) -> tuple[Score,ActionGopher]:
#     '''Renvoie de l'action si les deux techniques sont d'accords'''
#     best_action = []
#     if actionMinMax == actionSousProblèmes:
#         best_action = actionMinMax
#     return best_action

# def best_taille_for_grid(grid: Grids, player: Player) -> list[list[Cell]]:
#     '''Renvoie la taille de la sous-grille où la technique de minmax est la plus efficace'''
#     matrice_taille = []
#     taille = 1
#     max_taille = 50 #à voir s'il a mis une taille maximum pour la grille dans l'API.
#     #à terminer...
#     for i in range(taille,max_taille):
#         pass
#     return matrice_taille

#TODO A FAIRE : 
#TODO OBTERNIR LE SERVEUR DE TEST
#TODO COMMENCER DODO (COUPS LEGAUX, MINMAX, SOUS-PROBLEMES) => ATTENTION HEURISTIQUE! 
#TODO IMPLEMENTER MULTIPROCESSING (MULTITHREADING)

#TODO IMPLEMENTER DICTIONNAIRE COUP LEGAUX LOCAUX
#TODO TERMINER SOUS-PROBLEMES
#TODO IMPLEMENTER LES FONCTION DE HASHAGE
