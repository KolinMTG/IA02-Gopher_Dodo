import tkinter as tk

def toggle_visibility():
    # Fonction pour basculer la visibilité du bouton, changer sa couleur et incrémenter le compteur
    global compteur
    compteur += 1
    label_compteur.config(text="Nombre de clics : " + str(compteur))

    if bouton_invisible["bg"] == "white":
        bouton_invisible.config(bg="red")

    else:
        bouton_invisible.config(bg="white")


# Créer une fenêtre Tkinter
fenetre = tk.Tk()
fenetre.title("Bouton Invisible")

# Initialiser le compteur
compteur = 0

# Créer un bouton invisible
bouton_invisible = tk.Button(fenetre, text="", command=toggle_visibility, relief="flat")
bouton_invisible.pack()

# Créer un label pour afficher le nombre de clics
label_compteur = tk.Label(fenetre, text="Nombre de clics : 0")
label_compteur.pack()

# Lancer la boucle principale Tkinter
fenetre.mainloop()

# Lancer la boucle principale Tkinter
fenetre.mainloop()