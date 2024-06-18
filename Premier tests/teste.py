import tkinter as tk
import math

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

            # Créer un bouton à chaque hexagone
            button = tk.Button(canvas, text="", command=lambda q=q, r=r: button_click(q, r), width=10, height=2)
            button.place(x=x, y=y, anchor="center")  # Placer le bouton aux coordonnées de l'hexagone

    # Créer un bouton spécial pour la position q=0, r=0
    x_0_0 = center_x
    y_0_0 = center_y
    joueur = 1
    button_0_0 = tk.Button(canvas, text="", command=lambda q=0, r=0: button_click(q, r), width=10, height=2)
    button_0_0.place(x=x_0_0, y=y_0_0, anchor="center")  # Placer le bouton aux coordonnées de l'hexagone



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

# Fonction appelée lorsque le bouton de l'hexagone est cliqué

def button_click(q, r):
    position = (q, r, -q-r)  # Position de la case à colorier (ici, la case centrale)
    color_case(canvas, position, "blue", side_length, canvas_width, canvas_height, rayon)
    

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

# Lancer la boucle principale de l'application
root.mainloop()