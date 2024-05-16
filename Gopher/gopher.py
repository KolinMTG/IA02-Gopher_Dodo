#Une case du plateau de jeu sera representé par un tuple (i,j,k) ou i,j,k sont 3 axes du tableau. les coordonnées au milieu du plateau



from typing import List, Tuple
import math as m
import tkinter as tk
import itertools as itr
import matplotlib.pyplot as plt
import random as rd




Value = int
Position = Tuple[int, int, int]
Case = Tuple[Position, Value]
Grid = List[Case]
Joueur = int #1 ou 2
Coup = Tuple[Position, Joueur]

Rouge = 1
Bleu = 2


def position(s:int, q:int,r:int) -> Position:
    return (s,q,r)

def case(s: int,q:int,r:int, valeur:int) -> Case:
    """renvoie la case de valeur valeur, et de positition i,j,k"""
    pos = position(s,q,r)
    return (pos, valeur)

def get_coord(c : Case) -> Position:
    return c[0]

def get_value(c : Case) -> Value:
    return c[1]

def generer_grid_vide(taille : int) -> Grid :
    """cree une grille de jeu, initialisé avec uniquement des cases à 0, et de taille, la taille de la grille represente le "rayon" de la grille"""
    assert taille > 0
    grille = []
    for q in range(-taille+1,taille):
        for r in range(max(-taille+1, -q-taille+1), min(taille, -q+taille)):
            s=-q-r
            grille.append(case(q,r,s, 0))
    return grille

#!teste
# print(generer_grid_vide(4))


def voisins(grille : Grid, pos:Position) -> List[Case]:
     #recuperation de la position de la case
    liste_position_voisins=[]
    liste_position_voisins.append((pos[0]+1, pos[1]-1, pos[2]))
    liste_position_voisins.append((pos[0]-1, pos[1]+1, pos[2]))
    liste_position_voisins.append((pos[0], pos[1]+1, pos[2]-1))
    liste_position_voisins.append((pos[0], pos[1]-1, pos[2]+1))
    liste_position_voisins.append((pos[0]+1, pos[1], pos[2]-1))
    liste_position_voisins.append((pos[0]-1, pos[1], pos[2]+1))

    liste_voisins = []

    for element_case in grille:
        position_case = get_coord(element_case)
        for position_voisin in liste_position_voisins:
            if position_case == position_voisin:
                liste_voisins.append(element_case)
    return liste_voisins

#!teste
# grille = generer_grid_vide(4)
# print(voisins(grille, (0,0,0)))

def est_legal(grille: Grid, coup : Coup) -> bool:
    """Renvoie true si le coup est legal pour une grille donnée et false sinon"""
    pos = coup[0]
    joueur = coup[1]
    compteur = 0 #va servir a compter le nombre de case adverses voisines
    assert joueur == Bleu or joueur == Rouge #verifier que c'est soit le joueur 1 soit le joueur 2
    liste_voisin = voisins(grille, coup[0])

    for element_case in grille:
        if pos == get_coord(element_case) and get_value(element_case) != 0:
            return False #si la case est deja joué

    for element_case in liste_voisin:
        
        if (get_value(element_case) == 2 and joueur == 1) or (get_value(element_case) == 1 and joueur == 2) :
            compteur +=1 #on a trouvé une case adverse adjacente à notre case
        if get_value(element_case) == joueur : 
            return False #si la case est adjacente à une case deja joué par nous
        if compteur == 2 :
            return False #si la case est adjacente à au moins 2 case deja joué par l'adversère
    if compteur == 0 :
        return False #si la case n'est adajcente à aucune case
    return True


def jouer_coup(grille: Grid, coup : Coup) -> Grid :
    """Renvoie la grille apres que le coup ai été effectué"""

    nouvelle_grille = [element_case for element_case in grille if get_coord(element_case) != coup[0]] #toute les case, sauf celle qu'on joue, qu'on va rajouter apres
    nouvelle_grille.append((coup[0], coup[1]))
    return nouvelle_grille


def liste_coup_legaux(grille:Grid, joueur:Joueur) -> List[Coup]:
    """renvoie la liste de tout les coups possibles"""
    liste_coup=[]
    for element_case in grille:
        pos = get_coord(element_case)
        coup = (pos,joueur)
        if est_legal(grille, coup):
            liste_coup.append(coup)
    return liste_coup

def jouer_random(grille: Grid, joueur: Joueur, premier_coup : bool) -> Grid:
    """joue un coup aleatoire pour un joueur donné"""
    if not(premier_coup):
        liste_coup = liste_coup_legaux(grille, joueur)
        coup = rd.choice(liste_coup)
        return jouer_coup(grille, coup)
    else:
        coup = (0,0,0), joueur
        return jouer_coup(grille, coup)

def jouer_humain(grille: Grid, joueur: Joueur, premier_coup : bool) -> Grid:
    #demander graphiquement au joueur1 de donner une position 
    while True:
        print("Joueur", joueur, "Choisisez la coordonnée de la case a remplir")
                
        q = int(input("q"))
        r = int(input("r"))
        s = int(input("s"))
        coup : Coup = ((q,r,s), joueur)
        print(coup)
        if est_legal(grille, coup) or premier_coup:
            grille = jouer_coup(grille, coup)
            premier_coup = False
            break
        print("Erreur, votre coup n'est pas legal, jouer un coup legal")
        print(liste_coup_legaux(grille, joueur))
    return jouer_coup(grille, coup)



def a_gagne(grille:Grid, joueur:Joueur) -> bool:
    if joueur == Rouge : 
        liste_coup = liste_coup_legaux(grille, Bleu)
        if liste_coup == []:
            return True
        return False

    if joueur == Bleu : 
        liste_coup = liste_coup_legaux(grille, Rouge)
        if liste_coup == []:
            return True
        return False
    
def sous_hexagone(grille: Grid, taille_grille:int, num:int) -> Grid:
    """renvoie la grille de taille num extraite de la grille initiale"""
    assert taille_grille >= 3 and num >= 2 and num < taille_grille
    
    sous_grille = []
    for element_case in grille :
        pos = get_coord(element_case)
        if abs(pos[0]) <= num and abs(pos[1]) <= num and abs(pos[2]) <= num:
            sous_grille.append(element_case)
    # print("Num", num)
    # print("Grille", sous_grille)
    return sous_grille


def jouer_random_random(taille_grille:int = 4) -> Joueur:
    """fonction qui permet de jouer une partie de gopher, et qui renvoie le joueur gagnant"""
    grille = generer_grid_vide(taille_grille)
    joueur = Bleu
    score = {Rouge:0, Bleu:0}
    premier_coup=True
    while True : 
        if a_gagne(grille, joueur) and premier_coup == False: 
            print("Felicitation, le joueur," ,joueur, "A gagné")
            print("Score final : ", score)
            break
        #changer de joueur

        if joueur == Rouge : 
            joueur = Bleu
        else:
            joueur = Rouge 

        # print(liste_coup_legaux(grille, joueur))
        grille = jouer_random(grille, joueur, premier_coup)
        premier_coup = False
        for num in range(2, taille_grille):
            if a_gagne(sous_hexagone(grille, taille_grille, num), joueur):
                score[joueur] += 1
        # print("Joueur", joueur, "a joué")
    return joueur, score



def test(N, taille):
    compteur = 0
    for i in range(N):
        joueur_gagnant, score = jouer_random_random(taille)
        if joueur_gagnant == Rouge:
            if score[Rouge] > score[Bleu]:
                compteur += 1
        if joueur_gagnant == Bleu:
            if score[Bleu] > score[Rouge]:
                compteur += 1
    return compteur/N

X, Y = [], []
for i in range(3, 5):
    X.append(i)
    Y.append(test(200, i))
plt.plot(X, Y)
plt.show()






# ? MINMAX ALGORITHM
# def minmax(node, depth, maximizingPlayer) -> float:
#    if depth = 0 or node is a terminal node:
#        return the evaluation value of node
#    if maximizingPlayer:
#          bestValue = −∞
#          for each child of node:
#              v = minmax(child, depth − 1, False)
#              bestValue = max(bestValue, v)
#          return bestValue
#    else: # minimizing player
#          bestValue = +∞
#          for each child of node:
#              v = minmax(child, depth − 1, True)
#              bestValue = min(bestValue, v)
#          return bestValue

def minmax(grid:Grid, joueur : Joueur, maxi_player:bool=True) -> int:


    if a_gagne(grid, joueur):
        return 1
    elif a_gagne(grid,joueur):
        return -1
    else:
        if maxi_player:
            meilleur_val = m.inf
            for coup in liste_coup_legaux(grid, joueur):
                grid = jouer_coup(grid, coup)
                val = minmax(grid, joueur, False)
                meilleur_val = max(meilleur_val, val)
            return meilleur_val
        else:
            meilleur_val = -m.inf
            for coup in liste_coup_legaux(grid, joueur):
                grid = jouer_coup(grid, coup)
                val = minmax(grid, joueur, True)
                meilleur_val = min(meilleur_val, val)
            return meilleur_val



# grid = generer_grid_vide(4)
# grid = jouer_coup(grid, ((0,0,0),1))
# print(minmax(grid, Rouge, False))
























    






    

