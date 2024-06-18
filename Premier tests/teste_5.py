import numpy as np

# Créer un tableau NumPy multidimensionnel
tableau = np.array([[(1,2) (2, 3)], [(4, 5), (6, 7)]])

# Utiliser nditer pour parcourir et afficher chaque élément
for element in np.nditer(tableau):
    print(element)