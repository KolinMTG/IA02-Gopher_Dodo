#! ---------------------- IMPORTS ---------------------- !#
import numpy as np
from typing import Union, List, Tuple, Dict
from numpy.typing import NDArray
import random as rd
import multiprocessing as mp
from math import *
import itertools as it
import copy
from tqdm import tqdm

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
# print(grille, dico_conversion)
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

def play_action(grille:Grid, dico_conversion:DictConv, action:ActionGopher, joueur:Player, dict_legaux : DictLegauxGopher) -> Tuple[Grid, DictLegauxGopher]: 
    """Joue un coup pour un joueur donné, /!\ verifier que l'action est légale, l'action est de type Cell_hex"""
    cell_mat = dico_conversion[action]
    grille[cell_mat[0]][cell_mat[1]] = joueur
    dict_legaux = update_dico_legaux(dict_legaux, grille, dico_conversion, action)
    return grille, dict_legaux

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
    # print(action)
    # print("voisins : ", voisins(dico_conversion, action))
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



def boucle_rd_rd(taille_grille : int) -> int: # ! boucle de jeu OK
    """Boucle de jeu pour deux joueurs aléatoires"""

    grille, dico_conversion = init_grille_gopher(taille_grille)
    dico_legaux = init_dico_legaux_gopher(grille, dico_conversion)
    actions_possible = list(dico_conversion.keys())
    joueur = ROUGE
    action_debut = rd.choice(actions_possible)
    # print("Joueur de debut : ", joueur)
    # print("Action de debut : ", action_debut)
    grille, dico_legaux = play_action(grille, dico_conversion, action_debut, joueur, dico_legaux)

    # print("DicoLegaux: ", dico_legaux)
    # print("DicoLegaux UPDATE : ", dico_legaux)
    joueur = ROUGE if joueur == BLEU else BLEU
    while True:
        # print("Joueur : ", joueur)
        actions_legales = liste_coup_legaux(dico_legaux, joueur)
        # print("Liste coup legaux : ", liste_coup_legaux(dico_legaux, joueur))
        action = rd.choice(actions_legales)
        # print("Action : ", action)
        grille, dico_legaux = play_action(grille, dico_conversion, action, joueur, dico_legaux)
        joueur = ROUGE if joueur == BLEU else BLEU #changement de joueur
        if score_final(dico_legaux) != 0:
            break
    #aff.draw_hex_grid(grille)
    return score_final(dico_legaux)

#!test
# boucle = 0
# for _ in tqdm(range(10000)):
#     boucle += boucle_rd_rd(6)
# print(boucle) #normalement autours de 0



### Fonctions de hashage et de déhashage ###


def base64(nombre:int, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,'):
    """Conversion en base64."""
    base64 = ''
    if 0 <= nombre < len(alphabet):
        return alphabet[nombre]
    while nombre != 0:
        nombre, i = divmod(nombre, len(alphabet))
        base64 = alphabet[i] + base64
    return base64


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
                continue
    print(len(hashage))
    print(len(str(hex(int(hashage)))[2:]))
    print(len(str(base64(int(hashage)))))
    return (str(base64(int(hashage))))

#! ---------------------- Hashage et dehashage ---------------------- !#

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

def test_hashage(taille:int):
    """Teste la fonction de hashage"""
    grille=state_generator(taille)
    hashage=hashing(grille)
    print(hashage)
    bool_test=(grille==grille2)
    for elt in bool_test:
        for booleen in elt:
            if not(booleen):
                return False
    return True

# !test
# print(test_hashage_dehashage(15))
#print(len("e21c48d847acb65ad1dde0a9acb97f27b6c14cff79c878c2eba8daeabd1ddf49cc037afbe3dc41856c908ff3c4165c012216d6d08036023a54230389c058d110b410e7003615"))



#! ---------------------- Reflexions et rotations ---------------------- !#

def rotation(grille : Grid, dico_conversion : Dict) -> List[Grid]: #! OK
    """effectue une rotation de 60° de la grille hexagonale, utile pour les symétries"""
    taille_grille = len(grille)//2
    rot_1 = init_grille_gopher(taille_grille)[0]
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
# for rot in rotation(init_grille_dodo(6)[0], init_grille_dodo(6)[1]):
#     print("******************************ROT******************************")
#     print(rot)
#     aff.draw_hex_grid(rot)


def reflexion(grille : Grid, dico_conversion : Dict) -> List[Grid]: #! OK
    """effectue les 6 reflexions possible d'une grille donnée, utile pour les symétries"""
    taille_grille = len(grille)//2 
    ref_1 = init_grille_gopher(taille_grille)[0]
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


#!---------------------- Alpha Beta ----------------------!#

#cette section contient les fonctions nécessaires pour l'implémentation de l'algorithme alpha beta
#TODO : implementer un alpha-beta, utilisant : 
#TODO : -memoization avec hashage
#TODO : -gestion des symetries, reflexions et rotations avec hashage
#TODO : -une certaines profondeur de recherche
#TODO : -un tri des noeuds en fonction des coupures alpha et beta
#TODO ; multiprocess


# def eval_grille_finale(dico_legaux: DictLegauxGopher, player_max:Player) -> int:
#     if player_max == ROUGE:
#         return score_final(dico_legaux)
#     else:
#         return -score_final(dico_legaux)



def memoize(fonction):
    """Memoize decorator pour la fonction alpha_beta"""
    cache = {} # closure
    def g(grille: Grid,dico_conversion:DictConv, player: Player):
        grille_hashed = hashing(grille)
        if grille_hashed in cache: 
            # print("Appel memoize")
            return cache[grille_hashed]

        val = fonction(grille, player) #! c'est bien grille et non grille_hashed
        cache[grille_hashed] = val
        ref = reflexion(grille, dico_conversion)
        for grille_ref in ref: #! on fait 6 reflexions de la grille de depart
            grille_rot = rotation(grille_ref, dico_conversion) #! sur chacunes des relfexions on fait 6 rotations
            for grille_ref_rot in grille_rot:
                cache[hashing(grille_ref_rot)] = val #! on fini par append le hash des 36 grilles dans le cache
        return val
    return g

def trier_actions(grid, dico_conversion, liste_actions:List[ActionGopher],dico_legaux: DictLegauxGopher, player_max:Player) -> List[ActionGopher]:
    """Trie les actions en fonction du joueur"""
    liste_values = []
    if player_max == ROUGE:
        for action in liste_actions:
            _, dico_legaux = play_action(grid, dico_conversion, action, BLEU, dico_legaux)
            liste_values.append(score_final(dico_legaux))
    else :
        for action in liste_actions:
            _, dico_legaux = play_action(grid, dico_conversion, action, ROUGE, dico_legaux)
            liste_values.append(score_final(dico_legaux))
    return [x for y, x in sorted(zip(liste_values, liste_actions), key=lambda y:y[0])]




@memoize
def alpha_beta(grid : Grid,dico_conversion : DictConv, player_max : Player, dico_legaux : DictLegauxGopher, depth, alpha, beta) -> Tuple[Score, ActionGopher]:
    if depth == 0 or score_final(dico_legaux) != 0:
        return score_final(dico_legaux), None

    if player_max == ROUGE:
        best_value = -INF
        best_action = None
        for action in trier_actions(liste_coup_legaux(dico_legaux, ROUGE), player_max):
            new_element = play_action(grid, dico_conversion, action, ROUGE, dico_legaux)
            new_value, _ = alpha_beta(new_element[0],dico_conversion, BLEU, new_element[1], depth - 1, alpha, beta)
            if new_value > best_value:
                best_value = new_value
                best_action = action
            alpha = max(alpha, new_value)
            if beta <= alpha:
                break  # Coupe bêta
        return best_value, best_action
    else:
        min_value = INF
        best_action = None
        for action in trier_actions(liste_coup_legaux(dico_legaux, BLEU), player_max):
            new_value, _ = alpha_beta(new_element[0],dico_conversion, ROUGE, new_element[1], depth - 1, alpha, beta)
            if new_value < min_value:
                min_value = new_value
                best_action = action
            beta = min(beta, new_value)
            if beta <= alpha:
                break  # Coupe alpha
        return min_value, best_action
