"""auteur : Bastien CUVILLIER,Colin MANYRI,
date : 19/06/2024, version : 1.32
fichier contenant les fonctions pour le jeu dodo"""


from typing import Union, List, Tuple, Dict, Any
import random as rd
from math import inf
from numpy.typing import NDArray
import numpy as np

import affichage as aff


# Types de base utilisés par l'arbitre
Grid = tuple[tuple[Any,...],...]  # Grille de jeu (tableau 2D de cases)
# chaque case est un tuple (x, y) qui permet d'optenir la Value de la case dans la Grid_value
GameValue = int  # Valeur d'une case (0, 1 ou 2)
Cell = Tuple[int, int]
CellHex = Tuple[int, int]
# coordonnées hexagonales c'est a dire celles du prof, qui doivent etre données au serveur
CellMat = Tuple[int, int]
# coordonnées de type indice (x,y) d'une matrice numpy,
# accècs a une valeur de grille avec grille[x][y]
Case = Tuple[Cell, GameValue]

ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]  # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int  # 1 ou 2
State = list[tuple[Cell, Player]]  # État du jeu pour la boucle de jeu
Score = float
Time = int
DirectionJeu = Dict
# contient un vecteur direction qui selon lequel chaque joueur doit progresser pour gagner
# DicoLegaux = Dict[Dict]

INF = +inf
EMPTY = 0  # à utiliser pour les cases vides
ROUGE = 1
BLEU = 2
NDEF = -1  # a utiliser pour les cases qui n'existes pas


def tuple_to_list(tup: Tuple) -> List:
    """Transforme un tuple en liste"""
    liste_tmp = [tup[i] for i in range(len(tup))]
    for i, _ in enumerate(liste_tmp):
        if isinstance(liste_tmp[i], tuple):
            liste_tmp[i] = tuple_to_list(liste_tmp[i])
    return liste_tmp


print(tuple_to_list(((1, 2), (3, 4), (5, 6))))


def liste_to_tuple(lis: List) -> Tuple:
    """Transforme une liste en tuple"""
    liste_tmp = [tuple(lis[i]) for i in range(len(lis))]
    return tuple(liste_tmp)


#!test
# print(liste_to_tuple([[1,2], [3,4], [5,6]]))

# initialisation de la grille en suivant les règle
# du jeu dodo pour n'importe quelles tailles de grilles
#!   /!\ le dico_conversion contient des clés de type Cell_hex et des valeurs de type Cell_mat /!\
def init_grille_dodo_one_line(taille_grille: int) -> Tuple[Grid, Dict[tuple[int,int],tuple[int,int]], DirectionJeu]:  #!OK
    """Initialise la grille de jeu avec les pions au bon endroit.
    Et initialisation du dico de conversion."""
    taille_array = 2 * taille_grille + 1
    dico_conversion = {}
    grille = np.full((taille_array, taille_array), NDEF)

    #! initialisation du dico de conversion pour les coordonnées des cases de jeu
    compteur = taille_grille
    for i in range(taille_grille):  # remplir la premiere partie
        for j in range(compteur, taille_array):
            dico_conversion[(j - taille_grille, taille_grille - i)] = (i, j)
        compteur -= 1
    for j in range(taille_array):  # remplir la ligne du milieu
        dico_conversion[(j - taille_grille, 0)] = (taille_grille, j)
    compteur = 1
    for i in range(taille_grille + 1, taille_array):  # remplir le reste
        for j in range(taille_array - compteur):
            dico_conversion[(j - taille_grille, taille_grille - i)] = (i, j)
        compteur += 1
    # initialisation de la grille : toutes les cases qui ne sont pas en clé du dico n'existent pas
    for items in dico_conversion.items():
        key = items[0]
        x_cell, y_cell = dico_conversion[key]  #! type de dico_conversion[key] : CellMat
        if key[0] + key[1] >= taille_grille - 1:  # on remplit la grille avec les pions
            grille[x_cell][y_cell] = BLEU
        elif (
            key[0] + key[1] <= -taille_grille + 1
        ):  # on remplit la grille avec les pions
            grille[x_cell][y_cell] = ROUGE
        else:
            grille[x_cell][y_cell] = EMPTY  # on remplit la grille avec les cases vides

    liste_tmp = [tuple(grille[i]) for i in range(taille_array)]
    grille_finale = tuple(liste_tmp)
    return (
        grille_finale,
        dico_conversion,
        {ROUGE: [(1, 0), (0, 1), (1, 1)], BLEU: [(-1, 0), (-1, -1), (0, -1)]},
    )


# Initialisation de dodo pour un jeu en mode corners et
# une taille de grille de 3 (cas du serveur avec petite grille)
#!   /!\ le dico_conversion contient des clés de type Cell_hex et des valeurs de type Cell_mat /!\
def init_grille_dodo_corners(taille_grille: int) -> Tuple[Grid, Dict, DirectionJeu]:  #!OK
    """Initialise la grille de jeu avec les pions au bon endroit. Et initialisation du dico de conversion."""

    taille_array = 2 * taille_grille + 1
    dico_conversion = {}
    grille = np.full((taille_array, taille_array), NDEF)

    #! initialisation du dico de conversion pour les coordonnées des cases de jeu
    compteur = taille_grille
    for i in range(taille_grille):  # remplir la premiere partie
        for j in range(compteur, taille_array):
            dico_conversion[(j - taille_grille, taille_grille - i)] = (i, j)
        compteur -= 1
    for j in range(taille_array):  # remplir la ligne du milieu
        dico_conversion[(j - taille_grille, 0)] = (taille_grille, j)
    compteur = 1
    for i in range(taille_grille + 1, taille_array):  # remplir le reste
        for j in range(taille_array - compteur):
            dico_conversion[(j - taille_grille, taille_grille - i)] = (i, j)
        compteur += 1

    for key in dico_conversion.keys():  # initialisation de la grille :
        # toutes les cases qui ne sont pas en clé du dico n'existent pas
        x_cell, y_cell = dico_conversion[
            key
        ]  #! type de dico_conversion[key] : Cell_mat
        if key[0] + key[1] >= taille_grille:  # on remplit la grille avec les pions bleu
            grille[x_cell][y_cell] = BLEU
        elif (
            key[0] + key[1] <= -taille_grille
        ):  # on remplit la grille avec les pions rouges
            grille[x_cell][y_cell] = ROUGE
        else:
            grille[x_cell][y_cell] = EMPTY  # on remplit la grille avec les cases vides

    liste_tmp = [tuple(grille[i]) for i in range(taille_array)]
    grille_finale = tuple(liste_tmp)
    return (
        grille_finale,
        dico_conversion,
        {ROUGE: [(1, 0), (0, 1), (1, 1)], BLEU: [(-1, 0), (-1, -1), (0, -1)]},
    )


# initialisation du jeu dodo pour une grille de taille 5 avec ligne blanche au centre (deuxième cas du serveur)
# #!   /!\ le dico_conversion contient des clés de type Cell_hex et des valeurs de type Cell_mat /!\
# def init_grille_dodo_one_ligne() -> Tuple[Grid, Dict, DirectionJeu]:  #!OK
#     """Initialise la grille de jeu avec les pions au bon endroit. Et initialisation du dico de conversion."""
#     taille_grille = 5
#     taille_array = 2 * taille_grille + 1
#     dico_conversion = {}
#     grille = np.full((taille_array, taille_array), NDEF)

#     #! initialisation du dico de conversion pour les coordonnées des cases de jeu
#     compteur = taille_grille
#     for i in range(taille_grille):  # remplir la premiere partie
#         for j in range(compteur, taille_array):
#             dico_conversion[(j - taille_grille, taille_grille - i)] = (i, j)
#         compteur -= 1
#     for j in range(taille_array):  # remplir la ligne du milieu
#         dico_conversion[(j - taille_grille, 0)] = (taille_grille, j)
#     compteur = 1
#     for i in range(taille_grille + 1, taille_array):  # remplir le reste
#         for j in range(taille_array - compteur):
#             dico_conversion[(j - taille_grille, taille_grille - i)] = (i, j)
#         compteur += 1

#     for (
#         key
#     ) in (
#         dico_conversion.keys()
#     ):  # initialisation de la grille : toutes les cases qui ne sont pas en clé du dico n'existent pas
#         x_cell, y_cell = dico_conversion[
#             key
#         ]  #! type de dico_conversion[key] : Cell_mat
#         if (
#             key[0] + key[1] >= taille_grille - 2
#         ):  # on remplit la grille avec les pions bleu
#             grille[x_cell][y_cell] = BLEU
#         elif (
#             key[0] + key[1] <= -taille_grille + 2
#         ):  # on remplit la grille avec les pions rouges
#             grille[x_cell][y_cell] = ROUGE
#         else:
#             grille[x_cell][y_cell] = EMPTY  # on remplit la grille avec les cases vides

#     liste_tmp = [tuple(grille[i]) for i in range(taille_array)]
#     grille_finale = tuple(liste_tmp)
#     return (
#         grille_finale,
#         dico_conversion,
#         {ROUGE: [(1, 0), (0, 1), (1, 1)], BLEU: [(-1, 0), (-1, -1), (0, -1)]},
#     )


#!test
# grille, dico_conversion, direction = init_grille_dodo_regle(3)
# aff.afficher_hex(grille, dico_conversion)
# grille, dico_conversion, direction = init_grille_dodo_corners()
# aff.afficher_hex(grille, dico_conversion)
# grille, dico_conversion, direction = init_grille_dodo_one_ligne()
# aff.afficher_hex(grille, dico_conversion)


def existe(dico_conversion: Dict, pos: Cell) -> bool:  #!OK
    """Renvoie True si la case existe et False sinon"""
    return pos in dico_conversion.keys()


def voisins(dico_conversion: Dict, pos: CellHex) -> List[CellHex]:
    """renvoie la liste des voisins d'une case donnée de grid_pos"""
    x_pos, y_pos = pos  # (x_pos, y_pos) = (0, 0) pour la case du milieu
    liste_absolue = [
        (x_pos, y_pos - 1),
        (x_pos, y_pos + 1),
        (x_pos + 1, y_pos),
        (x_pos - 1, y_pos),
        (x_pos + 1, y_pos + 1),
        (x_pos - 1, y_pos - 1),
    ]
    liste_voisins = []
    for coord in liste_absolue:
        # l'avantage est que si la case n'existe pas, on le sait car elle n'est pas dans le dico
        if existe(dico_conversion, coord):
            liste_voisins.append(coord)
    return liste_voisins


def est_legal(
    grille: Grid,
    dico_conversion: Dict,
    direction: DirectionJeu,
    action: ActionDodo,
    joueur: Player,
) -> bool:
    """Renvoie True si le coup est légal pour une grille donnée et False sinon"""
    cell_depart, cell_arrivee = action
    #! verifier que la cellule de depart et d'arrivee existent
    if not existe(dico_conversion, cell_depart) or not existe(
        dico_conversion, cell_arrivee
    ):
        return False
    #! verifier si la cell de depart appartient au joueur
    if (
        grille[dico_conversion[cell_depart][0]][dico_conversion[cell_depart][1]]
        != joueur
    ):
        return False
    #! verifier si la cell d'arrivee est vide
    if (
        grille[dico_conversion[cell_arrivee][0]][dico_conversion[cell_arrivee][1]]
        != EMPTY
    ):
        return False
    #! verifier si la cell de depart est adjacente à la cell d'arrivée et dans le bon sens :
    for dir_x, dir_y in direction[joueur]:
        # on s'est déplacé dans une direction autorisée
        if cell_arrivee == (cell_depart[0] + dir_x, cell_depart[1] + dir_y):
            return True
    return False




def liste_coup_legaux(
    grille: Grid, dico_conversion: Dict, direction: DirectionJeu, joueur: Player
) -> List[ActionDodo]:
    """Renvoie la liste des coups légaux pour un joueur donné"""
    liste_coups = []
    for cell_depart in dico_conversion.keys():
        for cell_arrivee in voisins(dico_conversion, cell_depart):
            if est_legal(
                grille, dico_conversion, direction, (cell_depart, cell_arrivee), joueur
            ):
                liste_coups.append((cell_depart, cell_arrivee))
    # print(direction[joueur])
    return liste_coups

# grille, dico_conversion, direction = init_grille_dodo_one_line(3)
# print(liste_coup_legaux(grille, dico_conversion, direction, ROUGE))
# print(liste_coup_legaux(grille, dico_conversion, direction, BLEU))
# aff.afficher_hex(grille, dico_conversion)



def play_action(
    grille: Grid, dico_conversion: Dict, action: ActionDodo, joueur: Player
) -> Grid:
    """Renvoie la grille après avoir joué un coup"""
    cell_depart, cell_arrivee = action
    grille_tmp = tuple_to_list(grille)
    grille_tmp[dico_conversion[cell_depart][0]][dico_conversion[cell_depart][1]] = EMPTY
    grille_tmp[dico_conversion[cell_arrivee][0]][
        dico_conversion[cell_arrivee][1]
    ] = joueur
    grille = liste_to_tuple(grille_tmp)
    return grille


def score(grille, dico_conversion, direction, joueur_max) -> Score:
    """Renvoie le score de la grille pour un joueur donné"""
    if joueur_max == ROUGE:
        return -len(liste_coup_legaux(grille, dico_conversion, direction, BLEU)) + len(
            liste_coup_legaux(grille, dico_conversion, direction, ROUGE)
        )
    return -len(liste_coup_legaux(grille, dico_conversion, direction, ROUGE)) + len(
        liste_coup_legaux(grille, dico_conversion, direction, BLEU)
    )


def final(grille, dico_conversion, direction) -> float:
    """Renvoie 1 si le joueur ROUGE a gagné, -1 si le joueur BLEU a gagné et 0 sinon"""
    if len(liste_coup_legaux(grille, dico_conversion, direction, ROUGE)) == 0:
        return 1
    if len(liste_coup_legaux(grille, dico_conversion, direction, BLEU)) == 0:
        return -1
    return 0


def rd_rd_dodo() -> float:
    """fait jouer deux randoms pour le joueur donné"""
    grille, dico_conversion, direction = init_grille_dodo_one_line(3)

    joueur = ROUGE
    while True:
        liste_coups = liste_coup_legaux(grille, dico_conversion, direction, joueur)
        coup = rd.choice(liste_coups)
        grille = play_action(grille, dico_conversion, coup, joueur)

        if final(grille, dico_conversion, direction):
            # aff.afficher_hex(grille, dico_conversion)
            break
        if joueur == ROUGE:
            joueur = BLEU
        else:
            joueur = ROUGE
    return final(grille, dico_conversion, direction)


def base64(
    nombre: int,
    alphabet="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,",
):
    """Conversion en base64."""
    b64 = ""
    if 0 <= nombre < len(alphabet):
        return alphabet[nombre]
    while nombre != 0:
        nombre, i = divmod(nombre, len(alphabet))
        b64 = alphabet[i] + b64
    return b64


def hashing(game_value_grid: Grid) -> str:
    """Fonction de hashage d'une grille"""
    hashage = ""
    for dimension in game_value_grid:
        for game_value in dimension:
            if game_value == ROUGE:  # 1
                hashage += "1"
            elif game_value == BLEU:  # 2
                hashage += "2"
            elif game_value == EMPTY:  # 0
                hashage += "0"
            else:  # cas NDEF
                continue
    return str(base64(int(hashage)))


def memoize(fonction):
    """Memoize decorator pour la fonction alpha_beta"""
    cache = {}  # closure
    print("Appel memoize")  #!test

    def g_func(
        grid: Grid, dico_conversion, direction, player_max: Player, depth, alpha, beta
    ):
        """fonction à décorer"""
        grille_hashed = hashing(grid)
        if grille_hashed in cache:
            # print("Appel memoize")
            return cache[grille_hashed]
        val = fonction(grid, dico_conversion, direction, player_max, depth, alpha, beta)
        if val[1] is not None:
            cache[grille_hashed] = val
        return val

    return g_func


def trier_actions(
    grid,
    dico_conversion,
    direction,
    liste_actions: List[ActionDodo],
    player_max: Player,
) -> List[ActionDodo]:
    """Trie les actions en fonction du joueur"""
    liste_values = []
    if player_max == ROUGE:
        for _, _ in enumerate(liste_actions):
            liste_values.append(score(grid, dico_conversion, direction, ROUGE))
    else:
        for _, _ in enumerate(liste_actions):
            liste_values.append(score(grid, dico_conversion, direction, BLEU))
    # print(liste_values,liste_actions)
    return [x for _, x in sorted(zip(liste_values, liste_actions))]


@memoize
def alpha_beta_dodo(
    grid: Grid, dico_conversion, direction, player_max: Player, depth, alpha, beta
) -> Tuple[Score, ActionDodo]:
    """Algorithme alpha-beta pour le jeu dodo"""
    # print("Appel alpha_beta_dodo", depth)  #!test
    if depth == 0 or final(grid, dico_conversion, direction):
        return final(grid, dico_conversion, direction), None

    if player_max == ROUGE:
        best_value = -INF
        best_action = None
        for action in trier_actions(
            grid,
            dico_conversion,
            direction,
            liste_coup_legaux(grid, dico_conversion, direction, ROUGE),
            player_max,
        ):
            new_grid = play_action(grid, dico_conversion, action, ROUGE)
            new_value, _ = alpha_beta_dodo(
                new_grid, dico_conversion, direction, BLEU, depth - 1, alpha, beta
            )
            # print("ROUGE",new_value)
            if new_value >= best_value:
                best_value = new_value
                best_action = action
            alpha = max(alpha, new_value)
            if beta <= alpha:
                break  # Coupe bêta
        return best_value, best_action
    best_value = INF
    best_action = None
    for action in trier_actions(
        grid,
        dico_conversion,
        direction,
        liste_coup_legaux(grid, dico_conversion, direction, BLEU),
        player_max,
    ):
        new_grid = play_action(grid, dico_conversion, action, BLEU)
        new_value, _ = alpha_beta_dodo(
            new_grid, dico_conversion, direction, ROUGE, depth - 1, alpha, beta
        )
        # print("BLEU",new_value)
        if new_value <= best_value:
            best_value = new_value
            best_action = action
        beta = min(beta, new_value)
        if beta <= alpha:
            break
    return best_value, best_action


def boucle_rd_alpha_beta(taille_grille: int, depth: int) -> float:
    """Boucle de jeu pour un joueur aléatoire et un joueur Alpha-Beta"""

    grille, dico_conversion, direction = init_grille_dodo_one_line(taille_grille)
    while True:
        # aff.afficher_hex(grille, dico_conversion) #!test
        liste_coups = liste_coup_legaux(grille, dico_conversion, direction, BLEU)
        coup = rd.choice(liste_coups)
        grille = play_action(grille, dico_conversion, coup, BLEU)
        if final(grille, dico_conversion, direction):
            break
        _, coup = alpha_beta_dodo(
            grille, dico_conversion, direction, ROUGE, depth, -INF, INF
        )
        if coup not in liste_coup_legaux(grille, dico_conversion, direction, ROUGE) : 
            print("ERREUR")
        grille = play_action(grille, dico_conversion, coup, ROUGE)
        if final(grille, dico_conversion, direction):
            break
    return final(grille, dico_conversion, direction)


# print(boucle_rd_alpha_beta(3, 3)) #!test
