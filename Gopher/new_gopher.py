import numpy as np
from typing import Union
import pprint 
import tkinter as tk
import random as rd

# Types de base utilisés par l'arbitre
Grid_pos = np.ndarray # Grille de jeu (tableau 2D de cases), 
#chaque case est un tuple (x, y) qui permet d'optenir la Value de la case dans la Grid_value
Grid_value = np.ndarray # Grille de jeu (tableau 2D de GameValue)
Grids = tuple[Grid_pos, Grid_value] # Ensemble des deux grilles (la grille de coordonnées et la grille de valeurs)
GameValue = int # Valeur d'une case (0, 1 ou 2)
# Environment = ... # Ensemble des données utiles (cache, état de jeu...) pour
#               # que votre IA puisse jouer (objet, dictionnaire, autre...)
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int



INF = 1000000
EMPTY = 0
ROUGE = 1
BLEU = 2


def init_grille(taille_grille: int) -> Grids:
    """Initialise la grille de jeu avec des cases vides."""

    taille_array = 2*taille_grille+1
    grilles = (np.full((taille_array, taille_array), None), np.full((taille_array, taille_array), EMPTY))
    compteur = taille_grille
    for i in range(taille_grille): #remplir la premiere partie
        for j in range(compteur, taille_array):
            grilles[0][i][j] = (j-taille_grille, taille_grille-i)
        compteur -=1
    for j in range(taille_array): #remplir la ligne du milieu
        grilles[0][taille_grille][j] = (j-taille_grille, 0)
    compteur = 1
    for i in range(taille_grille+1, taille_array): #remplir le reste
        for j in range(taille_array-compteur):
            grilles[0][i][j] = (j-taille_grille, taille_grille-i)
            
        compteur +=1
    return grilles

#!test
#print(init_grille(7))

def voisins(grille:Grid_pos, pos:Cell) -> list[Cell]:
    """renvoie la liste des voisins d'une case donnée de grid_pos"""
    taille_max_array = np.shape(grille[0])[0] //2-1
    x, y = pos
    liste_absolue = [(x, y-1), (x, y+1), (x+1, y), (x-1, y), (x+1, y+1), (x-1, y-1)]
    liste_voisins =[]
    for element in liste_absolue:
        if (element[0]*element[1]>=0 or abs(element[0])+abs(element[1])<=taille_max_array) and ((abs(element[0])<=taille_max_array) and (abs(element[1])<=taille_max_array)):
            liste_voisins.append(element)
    return liste_voisins

#!test
# print(voisins(init_grille(7), (6,6)))
# print(voisins(init_grille(7), (0,0)))
#print(voisins(init_grille(7), (3, -3)))

def get_value(grille:Grid_value, pos:Cell) -> GameValue:
    """renvoie la valeur d'une case donnée de position tuple pos"""
    taille_max_array = np.shape(grille)[0] //2-1
    x, y = pos
    x += taille_max_array
    y += taille_max_array
    return grille[x, y]

#!test
# print(get_value(init_grille(7)[1], (-6,0)))
# print(get_value(init_grille(7)[1], (0,0)))
# print(get_value(init_grille(7)[1], (6,6)))


def play_action(grille:Grid_value, action: ActionGopher, player : Player) -> Grid_value:
    """modifie la valeur d'une case donnée de position tuple pos"""
    taille_max_array = np.shape(grille)[0] //2-1 
    x, y = action #recuperation de la postion 
    x += taille_max_array #conversion vers la position dans le tableau_value
    y += taille_max_array
    grille[x, y] = player #modification de la valeur de la case dans la grille value
    return grille


def est_legal(grille:Grids, coup:ActionGopher, joueur : Player) -> bool:
    """Renvoie True si le coup est légal pour une grille donnée et False sinon"""
    grid_pos = grille[0]
    grid_value = grille[1]
    x, y = coup
    if grid_value[x, y] != EMPTY: #si la case est deja prise
        return False

    liste_voisins = voisins(grid_pos, coup)
    joueur_1 = 0
    joueur_2 = 0
    for voisin in liste_voisins:
        if get_value(grid_value, voisin) == joueur: #si la case est en contacte avec une case du même joueur 
            joueur_1 +=1
        elif grid_value[voisin] != EMPTY: #si la case est en contacte avec une case du joueur adverse
            joueur_2 +=1
    if joueur_1 == 0 and joueur_2 == 1: #exactement 0 cases du joueur et 1 case du joueur adverse
        return True
    
def liste_coup_legaux(grille:Grids, joueur:Player) -> list[ActionGopher]:
    """Renvoie la liste de tous les coups légaux pour un joueur donné"""
    liste_coups = []
    for ligne_coup in grille[0]:
        for coup in ligne_coup: #parcours de tout les coup (qui sont des Cell = tuple(int, int) ou des None)
            if coup != None and est_legal(grille, coup, joueur): #si le coup est légal
                liste_coups.append(coup) #on l'ajoute à la liste des coups légaux
    return liste_coups


def a_perdu(grille:Grids, joueur:Player) -> bool:
    """Renvoie True si le joueur a perdu et False sinon"""
    return liste_coup_legaux(grille, joueur) == []

def final(grille:Grids) -> Score:
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


def jouer_aleatoir_aleatoir() -> Player:
    """fait jouer deux aleatoires a gopher, renvoie le joueur gagnat"""
    grille = init_grille(6)
    print(grille[0])




    # while not a_perdu(grille, joueur):
    #     print("Joueur : ", joueur)
    #     liste_coup = liste_coup_legaux(grille, joueur)
    #     print("Liste des coups possibles : ", liste_coup)
    #     coup = liste_coup[rd.randint(0, len(liste_coup)-1)]
    #     print("Coup choisit : ", coup)
    #     grille = (grille[0], put_value(grille[ROUGE], coup, joueur))
    #     joueur = ROUGE if joueur == BLEU else BLEU #changement de joueur

    # joueur = ROUGE if joueur == BLEU else BLEU

jouer_aleatoir_aleatoir()


def memoize(fonction):
    cache = {} # closure
    def g(state: State, player: Player):
        if state in cache:
            # print("Appel memoize")
            return cache[state]
        val = fonction(state, player)
        cache[state] = val
        return val
    return g

@memoize
def minmax_action_gopher(grid : Grids, player : Player) -> tuple[Score, ActionGopher]:
    best_value_max = -INF
    best_value_min = INF
    best_action = None

    res = final(grid) #renvoie le score si la partie est finie, 0 sinon
    if res:
        return res, None

    for action in liste_coup_legaux(grid):
        grid_suiv =(grid[0], play_action(grid, action, player))
        if player == ROUGE:
            value = minmax_action_gopher(grid_suiv, BLEU)[0]
            if value > best_value_max:
                best_value_max = value
                best_action = action

        elif player == BLEU:
            value = minmax_action_gopher(grid_suiv, ROUGE)[0]
            if value < best_value_min:
                best_value_min = value
                best_action = action
    if player == ROUGE:
        return best_value_max, best_action
    else:
        return best_value_min, best_action



# def rotate (grid: Grids) -> Grids:
#     grid_pos = grid[0]
#     grid_value = grid[1]
#     taille_max_array = np.shape(grid_value)[0] //2-1
#     new_grid_pos = np.full((2*taille_max_array+1, 2*taille_max_array+1), None)
#     new_grid_value = np.full((2*taille_max_array+1, 2*taille_max_array+1), EMPTY)
#     for i in range(2*taille_max_array+1):
#         for j in range(2*taille_max_array+1):
#             new_grid_pos[i][j] = (-grid_pos[j][i][1], grid_pos[j][i][0])
#             new_grid_value[i][j] = grid_value[j][i]
#     return (new_grid_pos, new_grid_value)

# def show_grid_value(grille:Grid_value) -> None:
#     """utilise tkinter pour afficher la grille de jeu"""
#     root = tk.Tk()
#     for i in range(len(grille)):
#         for j in range(len(grille[i])):
#             label = tk.Label(root, text=f"{grille[i][j]}", borderwidth=1, relief="solid")
#             label.grid(row=i, column=j)
#     root.mainloop()

# #!test
# show_grid_value(init_grille(7)[1])
# show_grid_value(rotate(init_grille(7)))[1]


### SOUS PROBLEMES GOPHER ###    


def minmax_sousprob_gopher(grid: Grids, player: Player,centre: tuple[int,int],taille:int) -> tuple[Score,ActionGopher]:
    '''Renvoie le meilleur coup possible dans le cas d'un sous-problème sur Gopher'''
    newgrid = []
    for i in range(centre[0]-taille,centre[0]+taille):
        for j in range(centre[1]-taille,centre[1]+taille):
            if grid[i][j] != None:
                newgrid.append(grid[i][j]) #Une erreur est possible ici car grid[i][j] n'éxiste pas forcément.
    return minmax_action_gopher(newgrid,player)

def action_all_sous_prob(grid: Grids, player: Player, taille: int) -> list[tuple[Score,ActionGopher]]:
    '''Réalise l'ensemble des sous_problèmes centrés sur les coups légaux et de taille taille'''
    
    liste_action = []
    
    for centres in est_legal(grid,player):
        liste_action.append(minmax_sousprob_gopher(grid,player,centres,taille))
    
    ponderation_action={}
    
    for actions in liste_action:
        if actions not in ponderation_action:
            ponderation_action[actions] = 1
        else:
            ponderation_action[actions] += 1
    
    best_action=ponderation_action[0]
    for pond_action in ponderation_action.items():
        if pond_action[1]>best_action[1]:
            best_action=pond_action[0]
            
    return best_action

def test_sous_prob(actionMinMax: tuple[Score,ActionGopher], actionSousProblèmes: tuple[Score,ActionGopher]) -> tuple[Score,ActionGopher]:
    '''Renvoie de l'action si les deux techniques sont d'accords'''
    best_action = []
    if actionMinMax == actionSousProblèmes:
        best_action = actionMinMax
    return best_action

def best_taille_for_grid(grid: Grids, player: Player) -> list[list[Cell]]:
    '''Renvoie la taille de la sous-grille où la technique de minmax est la plus efficace'''
    matrice_taille = []
    taille = 1
    max_taille = 50 #à voir s'il a mis une taille maximum pour la grille dans l'API.
    #à terminer...
    return matrice_taille
