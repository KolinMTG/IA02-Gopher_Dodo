import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np

def axial_to_cubic(q, r):
    y = r
    x = q - r
    z = -q
    return [x, y, z]

def convert_to_3axes_hex(dico_conversion):
    return [axial_to_cubic(key[0], key[1]) for key in dico_conversion.keys()]

def create_color_list(grid, dico_conversion):
    colors = []
    for cell in dico_conversion.keys():
        value = grid[dico_conversion[cell][0]][dico_conversion[cell][1]]
        if  value == 0:
            colors.append(['White'])
        elif value == 1:
            colors.append(['Red'])
        elif value == 2:
            colors.append(['Blue'])
    return colors

def create_label_list(dico_conversion):

    return [[str(key)] for key in dico_conversion.keys()]



def show_hex(coord, colors, labels):
    # Horizontal cartesian coords
    hcoord = [c[0] for c in coord]

    # Vertical cartesian coords
    vcoord = [2. * np.sin(np.radians(60)) * (c[1] - c[2]) / 3. for c in coord]

    fig, ax = plt.subplots(1)
    ax.set_aspect('equal')

    # Add some coloured hexagons
    for x, y, c, l in zip(hcoord, vcoord, colors, labels):
        color = c[0].lower()  # matplotlib understands lower case words for colours
        hex = RegularPolygon((x, y), numVertices=6, radius=2. / 3., 
                             orientation=np.radians(30), 
                             facecolor=color, alpha=0.2, edgecolor='k')
        ax.add_patch(hex)
        # Also add a text label with reduced size
        ax.text(x, y + 0.2, l[0], ha='center', va='center', size = 6)

    # Also add scatter points in hexagon centres
    ax.scatter(hcoord, vcoord, c=[c[0].lower() for c in colors], alpha=0.5)

    plt.show()


def afficher_hex(grid, dico_conversion):
    coord = convert_to_3axes_hex(dico_conversion)
    colors = create_color_list(grid, dico_conversion)
    labels = create_label_list(dico_conversion)
    show_hex(coord, colors, labels)

    