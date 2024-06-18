
import math as m
import tkinter as tk
import itertools as itr
from typing import List, Tuple, Union
import random as rd 
import math

Value = int
Position = Tuple[int, int, int]
Case = Tuple[Position, Value]
Grid = List[Case]
Joueur = int #1 ou 2
Coup = Tuple[Position, Joueur]


# Fonction pour dessiner un hexagone aux coordonnées spécifiées avec une rotation
def draw_hexagon(canvas, x_center, y_center, side_length, rotation_angle):
    angle_rad = math.radians(rotation_angle)
    points = []
    for i in range(6):
        angle = angle_rad + math.radians(60 * i)
        x = x_center + side_length * math.cos(angle)
        y = y_center + side_length * math.sin(angle)
        points.append((x, y))
    canvas.create_polygon(points, outline="black", fill="", width=2)

# Fonction pour créer la grille hexagonale avec une rotation individuelle pour chaque hexagone
def create_hexagonal_grid(canvas, radius, side_length, canvas_width, canvas_height):
    # Calculer les coordonnées du centre de la grille
    center_x = canvas_width / 2
    center_y = canvas_height / 2

    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)
        for r in range(r1, r2 + 1):
            # Calculer les coordonnées de l'hexagone en fonction de sa position dans la grille
            x = center_x + side_length * math.sqrt(3) * (q + r / 2)
            y = center_y + side_length * (3 / 2) * r

            # Dessiner l'hexagone avec une rotation individuelle pour chaque hexagone
            draw_hexagon(canvas, x, y, side_length, 30)

def color_case(canvas, position, color, side_length, canvas_width, canvas_height, radius):
    # Calculer les coordonnées du point central de la grille
    center_x = canvas_width / 2
    center_y = canvas_height / 2
    q, r, s = position
    # Vérifier si la position est valide dans la grille
    if abs(q) <= radius and abs(r) <= radius and abs(s) <= radius and q + r + s == 0:
        # Calculer les coordonnées de l'hexagone en fonction de sa position dans la grille
        x_center = center_x + side_length * math.sqrt(3) * (q + r / 2)
        y_center = center_y + side_length * (3 / 2) * r
        # Calculer les points de l'hexagone
        angle_rad = math.radians(30)
        points = []
        for i in range(6):
            angle = angle_rad + math.radians(60 * i)
            x = x_center + side_length * math.cos(angle)
            y = y_center + side_length * math.sin(angle)
            points.append(x)
            points.append(y)

        # Dessiner l'hexagone en couleur
        canvas.create_polygon(points, outline="black", fill=color, width=2)
    else:
        print("Position invalide dans la grille hexagonale.")

# Créer la fenêtre principale
root = tk.Tk()
root.title("Grille hexagonale avec boutons")

# Créer un canevas pour afficher la grille hexagonale
canvas_width = 800
canvas_height = 600
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Paramètres de la grille
rayon = 3
side_length = 50

# Afficher la grille hexagonale avec une rotation individuelle pour chaque hexagone
create_hexagonal_grid(canvas, rayon, side_length, canvas_width, canvas_height)


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
    assert joueur == 1 or joueur == 2 #verifier que c'est soit le joueur 1 soit le joueur 2
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
    if joueur == 1 : 
        liste_coup = liste_coup_legaux(grille, 2)
        if liste_coup == []:
            return True
        return False
    
    if joueur == 2 : 
        liste_coup = liste_coup_legaux(grille, 1)
        if liste_coup == []:
            return True
        return False
    


def jouer_random_random(taille_grille:int = 4) -> Joueur:
    """fonction qui permet de jouer une partie de gopher, et qui renvoie le joueur gagnant"""
    grille = generer_grid_vide(taille_grille)
    joueur = 2
    premier_coup=True
    while True : 
        if a_gagne(grille, joueur) and premier_coup == False: 
            print("Felicitation, le joueur," ,joueur, "A gagné")
            break
        #changer de joueur

        if joueur == 1 : 
            joueur = 2
        else:
            joueur = 1 

        # print(liste_coup_legaux(grille, joueur))

        #colorer l'interface graphique
        grille = jouer_random(grille, joueur, premier_coup)
        if joueur == 1:
            color_case(canvas, get_coord(grille[-1]), "blue", side_length, canvas_width, canvas_height, rayon)
        else : 
            color_case(canvas, get_coord(grille[-1]), "red", side_length, canvas_width, canvas_height, rayon)
        premier_coup = False
        # print("Joueur", joueur, "a joué")
    return joueur

jouer_random_random()
# Lancer la boucle principale de l'application
root.mainloop()