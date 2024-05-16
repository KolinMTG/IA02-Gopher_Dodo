import numpy as np
from typing import Union
import pprint 
import tkinter as tk
# Types de base utilisés par l'arbitre
Grid = np.ndarray
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


def init_grille(taille_grille: int) -> Grid:
    """Initialise la grille de jeu avec des cases vides."""

    taille_array = 2*taille_grille+1
    grille = np.full((taille_array, taille_array), None)
    compteur = taille_grille
    for i in range(taille_grille): #remplir la premiere partie
        for j in range(compteur, taille_array):
            grille[i][j] = (j-taille_grille, taille_grille-i)
        compteur -=1
    for j in range(taille_array): #remplir la ligne du milieu
        grille[taille_grille][j] = (j-taille_grille, 0)
    compteur = 1
    for i in range(taille_grille+1, taille_array): #remplir le reste
        for j in range(taille_array-compteur):
            grille[i][j] = (j-taille_grille, taille_grille-i)
        compteur +=1
    return grille

print(init_grille(57))


# def show_grid(grille:Grid) -> None:
#     """utilise tkinter pour afficher la grille de jeu"""
#     root = tk.Tk()
#     for i in range(len(grille)):
#         for j in range(len(grille[i])):
#             if grille[i][j] is not None:
#                 label = tk.Label(root, text=f"{grille[i][j]}", borderwidth=1, relief="solid")
#                 label.grid(row=i, column=j)
#     root.mainloop()





