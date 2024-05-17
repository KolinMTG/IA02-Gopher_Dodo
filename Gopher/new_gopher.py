import numpy as np
from typing import Union
import pprint 
import tkinter as tk
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

EMPTY = 0


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
print(init_grille(7))

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
    print(x, y)
    return grille[x, y]

#!test
# print(get_value(init_grille(7)[1], (-6,0)))
# print(get_value(init_grille(7)[1], (0,0)))
# print(get_value(init_grille(7)[1], (6,6)))


def put_value(grille:Grid_value, pos:Cell, value:GameValue) -> Grid_value:
    """modifie la valeur d'une case donnée de position tuple pos"""
    taille_max_array = np.shape(grille)[0] //2-1 
    x, y = pos #recuperation de la postion 
    x += taille_max_array #conversion vers la position dans le tableau_value
    y += taille_max_array
    grille[x, y] = value #recuperation du tableau value
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


    






    
    




# def show_grid(grille:Grid) -> None:
#     """utilise tkinter pour afficher la grille de jeu"""
#     root = tk.Tk()
#     for i in range(len(grille)):
#         for j in range(len(grille[i])):
#             if grille[i][j] is not None:
#                 label = tk.Label(root, text=f"{grille[i][j]}", borderwidth=1, relief="solid")
#                 label.grid(row=i, column=j)
#     root.mainloop()





