import numpy as np
from typing import Union, List, Tuple, Dict
import pprint
import tkinter as tk
import random as rd
import multiprocessing as mp
from math import *
# Types de base utilisés par l'arbitre
Grid = List # Grille de jeu (tableau 2D de cases), 
#chaque case est un tuple (x, y) qui permet d'optenir la Value de la case dans la Grid_value
GameValue = int # Valeur d'une case (0, 1 ou 2)
Cell = Tuple[int, int]
Case = Tuple[Cell, GameValue]


ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int


INF = +inf
EMPTY = 0
ROUGE = 1
BLEU = 2



#? UPDATE, j'ai ajouté un dico qui permet de convertir les coordonnées des cases de jeu en indice du tableau

def init_grille(taille_grille: int) -> Tuple[Grid, Dict]:
    """Initialise la grille de jeu avec des cases vides."""

    taille_array = 2*taille_grille+1
    # grille = (np.full((taille_array, taille_array), [None, EMPTY], dtype=object))
    # grille = [[[None, EMPTY] for _ in range(taille_array)] for _ in range(taille_array)]
    grille = np.full((taille_array, taille_array), [None, EMPTY], dtype=object)
    compteur = taille_grille
    for i in range(taille_grille): #remplir la premiere partie
        for j in range(compteur, taille_array):
            grille[i][j][0] = (j-taille_grille, taille_grille-i)
        compteur -=1
    for j in range(taille_array): #remplir la ligne du milieu
        grille[taille_grille][j][0] = (j-taille_grille, 0)
    compteur = 1
    for i in range(taille_grille+1, taille_array): #remplir le reste
        for j in range(taille_array-compteur):
            grille[i][j][0] = (j-taille_grille, taille_grille-i)
        compteur +=1

    #! ajout d'un dictionnaire pour convertir les coordonnées en indice de tableau
    dico_conversion = {}
    for num_ligne, ligne in enumerate(grille):
        for num_col, case in enumerate(ligne):
            if case[0] != None:
                dico_conversion[case[0]] = (num_ligne, num_col)

    return grille, dico_conversion



#!test
print(init_grille(7))

def existe(dico_conversion:Dict, pos:Cell) -> bool:
    """Renvoie True si la case existe et False sinon"""
    return pos in dico_conversion.keys()

def voisins(grille:Grid,dico_conversion : Dict, pos:Cell) -> List[Case]:
    """renvoie la liste des voisins d'une case donnée de grid_pos"""
    x, y = pos #(x, y) = (0, 0) pour la case du milieu
    liste_absolue = [(x, y-1), (x, y+1), (x+1, y), (x-1, y), (x+1, y+1), (x-1, y-1)]
    liste_voisins = []
    for coord in liste_absolue: 
        if existe(dico_conversion, coord): #l'avantage est que si la case n'existe pas, on le sait car elle n'est pas dans le dico
            liste_voisins.append(grille[dico_conversion[coord]])
    return liste_voisins #renvoie les case !!! donc des listes[case, value]

#!test
# print(voisins(init_grille(7), (6,6)))
# print(voisins(init_grille(7), (0,0)))
# print(voisins(init_grille(7), (3, -3)))



def play_action(grille:Grid,dico_conversion : Dict ,action: ActionGopher, player : Player) -> Grid:
    """modifie la valeur d'une case donnée de position tuple pos"""
    x, y = action #recuperation de la postion 
    grille[dico_conversion[action]] = player #modification de la valeur de la case dans la grille value
    return grille




def est_legal(grille:Grid,dico_conversion: Dict , action:ActionGopher, joueur : Player) -> bool:
    """Renvoie True si le coup est légal pour une grille donnée et False sinon"""

    case_cible = grille[dico_conversion[action]]

    if existe(dico_conversion, action) == False: #si la case n'existe pas alors le coup n'est pas légal
        return False

    if case_cible[1] != EMPTY: #si la case n'est pas vide alors le coup n'est pas légal
        return False

    liste_voisins = voisins(grille, dico_conversion, action)
    nb_case_adverse = 0 #compter le nombre de case adjacentes qui sont à l'autre joueur
    for voisin in liste_voisins:
        if voisin[1] == joueur:
            return False
        elif voisin[1] != EMPTY: # si different de EMPTY et de joueur alors, c'est l'autre joueur qui est sur cette case
            nb_case_adverse+= 1
            if nb_case_adverse>1 :
                return False #il y a au moins 2 cases adjacentes qui sont à l'autre joueur
    return nb_case_adverse == 1 #il y a une seule case adjacente qui est à l'autre joueur 


def liste_coup_legaux(grille:Grid,dico_conversion:Dict, joueur:Player) -> list[ActionGopher]:
    """Renvoie la liste de tous les coups légaux pour un joueur donné"""
    liste_coups = []
    for ligne_case in grille:
        for case_grille in ligne_case:
            coup = case_grille[0] #un coup est associé à une case
            if coup != None and est_legal(grille, dico_conversion,  coup, joueur):
                liste_coups.append(coup)
    return liste_coups


def a_perdu(grille:Grid,dico_conversion:Dict, joueur:Player) -> bool:
    """Renvoie True si le joueur a perdu et False sinon"""
    return liste_coup_legaux(grille,dico_conversion, joueur) == []

def score_final(grille:Grid) -> Score: #permet à la fois de teste si le jeu est dans un état final et de renvoyer le score
    """Renvoie le score de la partie pour le joueur ROUGE"""
    if a_perdu(grille, ROUGE):
        return -1
    elif a_perdu(grille, BLEU):
        return 1
    else:
        return 0

# def show_grid(grille:Grid_pos) -> None:
#     """utilise tkinter pour afficher la grille de jeu"""
#     root = tk.Tk()
#     for i in range(len(grille)):
#         for j in range(len(grille[i])):
#             if grille[i][j] is not None:
#                 label = tk.Label(root, text=f"{grille[i][j]}", borderwidth=1, relief="solid")
#                 label.grid(row=i, column=j)
#     root.mainloop()

#!test
# show_grid(init_grille(7)[0])
# show_grid_value(init_grille(7)[1])






    # while not a_perdu(grille, joueur):
    #     print("Joueur : ", joueur)
    #     liste_coup = liste_coup_legaux(grille, joueur)
    #     print("Liste des coups possibles : ", liste_coup)
    #     coup = liste_coup[rd.randint(0, len(liste_coup)-1)]
    #     print("Coup choisit : ", coup)
    #     grille = (grille[0], put_value(grille[ROUGE], coup, joueur))
    #     joueur = ROUGE if joueur == BLEU else BLEU #changement de joueur

    # joueur = ROUGE if joueur == BLEU else BLEU

# jouer_aleatoir_aleatoir()


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



# # def rotate (grid: Grids) -> Grids:
# #     grid_pos = grid[0]
# #     grid_value = grid[1]
# #     taille_max_array = np.shape(grid_value)[0] //2-1
# #     new_grid_pos = np.full((2*taille_max_array+1, 2*taille_max_array+1), None)
# #     new_grid_value = np.full((2*taille_max_array+1, 2*taille_max_array+1), EMPTY)
# #     for i in range(2*taille_max_array+1):
# #         for j in range(2*taille_max_array+1):
# #             new_grid_pos[i][j] = (-grid_pos[j][i][1], grid_pos[j][i][0])
# #             new_grid_value[i][j] = grid_value[j][i]
# #     return (new_grid_pos, new_grid_value)

# # def show_grid_value(grille:Grid_value) -> None:
# #     """utilise tkinter pour afficher la grille de jeu"""
# #     root = tk.Tk()
# #     for i in range(len(grille)):
# #         for j in range(len(grille[i])):
# #             label = tk.Label(root, text=f"{grille[i][j]}", borderwidth=1, relief="solid")
# #             label.grid(row=i, column=j)
# #     root.mainloop()

# # #!test
# # show_grid_value(init_grille(7)[1])
# # show_grid_value(rotate(init_grille(7)))[1]


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

# A FAIRE : 
# OBTERNIR LE SERVEUR DE TEST
# COMMENCER DODO (COUPS LEGAUX, MINMAX, SOUS-PROBLEMES) => ATTENTION HEURISTIQUE!
# IMPLEMENTER MULTIPROCESSING (MULTITHREADING)

# IMPLEMENTER DICTIONNAIRE COUP LEGAUX LOCAUX
# TERMINER SOUS-PROBLEMES