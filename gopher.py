"""auteur : Bastien CUVILLIER,Colin MANYRI,
date : 19/06/2024, version : 1.4
fichier contenant les fonctions pour le jeu gopher"""
import random as rd
from math import inf
import copy
from typing import Union, List, Tuple, Dict, Optional
import numpy as np
from tqdm import tqdm
import affichage as aff



#! ---------------------- CONSTANTES ---------------------- !#
INF = +inf
EMPTY = 0
ROUGE = 1
BLEU = 2
NDEF = -1  # case non définie


#! ---------------------- TYPES ---------------------- !#
Player = int  # Joueur : donc ROUGE ou BLEU
GameValue = int  # valeur d'une case : donc NDEF, EMPTY, ROUGE, BLEU


Cell = Tuple[int, int]  # Coordonnées d'une case
CellMat = Cell  # Coordonnées d'une case dans la matrice
CellHex = Cell  # Coordonnées d'une case dans l'affichage hexagonal a fournir au serveur

GridTuple = Tuple[Tuple[GameValue,...],...]  
# La grille de jeu, est un tableau numpy 2D de GameValue
GridList = List[List[GameValue]]  
# La grille de jeu, est un tableau numpy 2D de GameValue


ActionGopher = CellHex  # Action du gopher
ActionDodo = Tuple[CellHex, CellHex]  # Action du dodo
Action = Union[ActionGopher, ActionDodo]  # Action du joueur

DictConv = Dict[CellMat, CellHex]  # Dictionnaire de conversion de coordonnées

DictLegalGopher = Dict[ActionGopher, bool]  # Dictionnaire des coups légaux
TupleLegalGopher = Tuple[Tuple[ActionGopher, bool]]  # Tuple des coups légaux


State = list[tuple[Cell, Player]]  # État du jeu pour la boucle de jeu
Score = float
Time = int

# //! ----------------------Fonction de conversions ---------------------- !#


def dict_to_tuple(dico: DictLegalGopher) -> TupleLegalGopher:
    """transforme un dictionnaire en tuple"""
    return tuple((key, value) for key, value in dico.items())


def tuple_to_dict(tup: TupleLegalGopher) -> DictLegalGopher:
    """transforme un tuple en dictionnaire"""
    return dict(tup)



def tuple_to_list(tup: GridTuple) -> GridList:
    """Transforme un tuple en liste"""
    liste_tmp = [tup[i] for i in range(len(tup))]
    for i, item in enumerate(liste_tmp):
        if isinstance(item, tuple):
            liste_tmp[i] = list(item)
    return liste_tmp


#!test
# print(tuple_to_list(((1,2), (3,4), (5,6))))


def liste_to_tuple(lis: GridList) -> GridTuple:
    """Transforme une liste en tuple"""
    liste_tmp = [tuple(lis[i]) for i in range(len(lis))]
    return tuple(liste_tmp)


#!test
# print(liste_to_tuple([[1,2], [3,4], [5,6]]))


#! ----------------------Fonctions d'initialisation ---------------------- !#


def init_grille_gopher(taille_grille: int) -> Tuple[GridTuple, DictConv]:  #!OK
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

    for (
        val
    ) in (
        dico_conversion.values()
    ):  # initialisation de la grille :
        #toutes les cases qui ne sont pas en clé du dico n'existent pas
        grille[val[0]][val[1]] = EMPTY

    grille_final = liste_to_tuple(grille)
    return grille_final, dico_conversion


#!test
# print(init_grille_gopher(2)[0])
# print(init_grille_gopher(2)[1])


#! ----------------------Fonctions lié a la grille ---------------------- !#


def existe(dico_conversion: DictConv, pos: CellHex) -> bool:  #!OK
    """Renvoie True si la case existe et False sinon"""
    return pos in dico_conversion.keys()


def voisins(dico_conversion: DictConv, pos: CellHex) -> List[CellHex]:  #!OK
    """renvoie la liste des voisins d'une case donnée de grid_pos,
    attention au types de coordonnées"""
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
        if existe(
            dico_conversion, coord
        ):  # l'avantage est que si la case n'existe pas, on le sait car elle n'est pas dans le dico
            liste_voisins.append(coord)
    return liste_voisins


#! ----------------------Fonctions lié aux actions legales ---------------------- !#


def init_dico_legaux_gopher(
    dico_conversion: DictConv,
) -> Tuple[TupleLegalGopher, TupleLegalGopher]:
    """Initialise le dictionnaire des coups légaux pour le gopher"""
    dico_legaux = {ROUGE: {}, BLEU: {}}
    for joueur, _ in dico_legaux.items():
        for action in dico_conversion:
            dico_legaux[joueur][action] = False
    tuple_dico_legaux = (
        dict_to_tuple(dico_legaux[ROUGE]),
        dict_to_tuple(dico_legaux[BLEU]),
    )
    return tuple_dico_legaux

#!test
# print(init_dico_legaux_gopher(init_grille_gopher(2)[1]))


def play_action(
    grille: GridTuple,
    dico_conversion: DictConv,
    action: ActionGopher,
    joueur: Player,
    dict_legaux: Tuple[TupleLegalGopher, TupleLegalGopher],
) -> Tuple[GridTuple, Tuple[TupleLegalGopher, TupleLegalGopher]]:
    """Joue un coup pour un joueur donné,
    verifier que l'action est légale,
    l'action est de type Cell_hex"""

    grille_tmp = tuple_to_list(grille)  # maintenant c'ets une liste

    cell_mat = dico_conversion[action]
    grille_tmp[cell_mat[0]][cell_mat[1]] = joueur  # on place le pion du joueur
    grille_final = liste_to_tuple(grille_tmp)

    dict_legaux = update_dico_legaux(dict_legaux, grille_final, dico_conversion, action)

    return grille_final, dict_legaux


def est_legal(
    grid: GridTuple, dico_conversion: Dict, action: ActionGopher, joueur: Player
) -> bool:
    """Renvoie True si le coup est légal pour une grille donnée et False sinon"""
    grille = tuple_to_list(grid)

    if not (
        existe(dico_conversion, action)
    ):  # si la case n'existe pas alors le coup n'est pas légal
        # print("case n'existe pas")
        return False

    cell_cible = dico_conversion[action]  # cell est une CellMat
    if (
        grille[cell_cible[0]][cell_cible[1]] != EMPTY
    ):  # si la case n'est pas vide alors le coup n'est pas légal
        # print("case non vide")
        return False
    nb_voisin = 0
    # print(action)
    # print("voisins : ", voisins(dico_conversion, action))
    for cell_voisin in voisins(
        dico_conversion, action
    ):  # on regarde les cases voisines
        if (
            grille[dico_conversion[cell_voisin][0]][dico_conversion[cell_voisin][1]]
            == joueur
        ):
            # print("deja une case du joueur sur une case voisine")
            return False

        if (
            grille[dico_conversion[cell_voisin][0]][dico_conversion[cell_voisin][1]]
            != EMPTY
        ):
            nb_voisin += 1  # on a trouvé une case adeverse
            if (
                nb_voisin == 2
            ):  # si on a trouvé plus d'une case adverse alors le coup n'est pas légal
                # print("au moins deux cases adverse trouvées")
                return False

    return (
        nb_voisin == 1
    )  # si on a trouvé une case adverse exactement alors le coup est légal


def update_dico_legaux(
    dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher],
    grille: GridTuple,
    dico_conversion: DictConv,
    action: ActionGopher,
) -> Tuple[TupleLegalGopher, TupleLegalGopher]:
    """Met à jour le dictionnaire des coups légaux pour un joueur donné"""
    new_dico_legaux = {
        ROUGE: tuple_to_dict(dico_legaux[0]),
        BLEU: tuple_to_dict(dico_legaux[1]),
    }

    for joueur in new_dico_legaux.keys():

        new_dico_legaux[joueur][
            action
        ] = False  # on ne peut pas rejouer la case jouée en action
        for cell in voisins(
            dico_conversion, action
        ):  # update des cases voisines de la case jouée
            if est_legal(grille, dico_conversion, cell, joueur):
                new_dico_legaux[joueur][cell] = True
            else:
                new_dico_legaux[joueur][cell] = False
    dico_legaux_final = (
        dict_to_tuple(new_dico_legaux[ROUGE]),
        dict_to_tuple(new_dico_legaux[BLEU]),
    )
    return dico_legaux_final


def liste_coup_legaux(
    dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher], joueur: Player
) -> List[ActionGopher]:  #! OK
    """Renvoie la liste des coups légaux pour un joueur donné"""
    dico_legaux = {
        ROUGE: tuple_to_dict(dico_legaux[0]),
        BLEU: tuple_to_dict(dico_legaux[1]),
    }
    return [
        action
        for action in dico_legaux[joueur].keys()
        if dico_legaux[joueur][action] is True
    ]


def final(
    player: Player, dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher]
) -> bool:  #!OK
    """Renvoie True si le joueur a gagné et False sinon"""
    return liste_coup_legaux(dico_legaux, player) == []


def score_final(dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher]) -> Score:  #!OK
    """Renvoie le score final, renvoie 0 si la partie n'est pas fini,
    1 si le joueur ROUGE a gagné, -1 si le joueur BLEU a gagné"""
    if liste_coup_legaux(dico_legaux, ROUGE) == []:
        return -INF
    if liste_coup_legaux(dico_legaux, BLEU) == []:
        return INF
    return 0


#! ---------------------- Boucle de jeu RD_RD ---------------------- !#


def boucle_rd_rd(taille_grille: int) -> float:  # ! boucle de jeu OK
    """Boucle de jeu pour deux joueurs aléatoires"""

    grille, dico_conversion = init_grille_gopher(taille_grille)
    dico_legaux = init_dico_legaux_gopher(dico_conversion)
    actions_possible = list(dico_conversion.keys())
    joueur = ROUGE
    action_debut = rd.choice(actions_possible)

    grille, dico_legaux = play_action(
        grille, dico_conversion, action_debut, joueur, dico_legaux
    )

    joueur = ROUGE if joueur == BLEU else BLEU
    while True:
        # print("Joueur : ", joueur)
        actions_legales = liste_coup_legaux(dico_legaux, joueur)
        # print("Liste coup legaux : ", liste_coup_legaux(dico_legaux, joueur))
        action = rd.choice(actions_legales)
        # print("Action : ", action)
        grille, dico_legaux = play_action(
            grille, dico_conversion, action, joueur, dico_legaux
        )
        joueur = ROUGE if joueur == BLEU else BLEU  # changement de joueur

        if final(joueur, dico_legaux):
            break
    aff.afficher_hex(grille, dico_conversion=dico_conversion)
    return score_final(dico_legaux)


#!test
# print(boucle_rd_rd(5))


#! ---------------------- Fonctions d'évaluation ---------------------- !#


def evaluation(dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher]) -> Score:
    """Evalue le score d'une action"""

    score = score_final(dico_legaux)

    if score == -INF:
        return -1000
    if score == INF:
        return 1000

    dico_legaux = {
        ROUGE: tuple_to_dict(dico_legaux[0]),
        BLEU: tuple_to_dict(dico_legaux[1]),
    }
    return len(
        [key for key in dico_legaux[ROUGE].keys() if dico_legaux[ROUGE][key]]
    ) - len([key for key in dico_legaux[BLEU].keys() if dico_legaux[BLEU][key]])


def base64(
    nombre: int,
    alphabet="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,",
):
    """Conversion en base64."""
    base64_result = ""
    if 0 <= nombre < len(alphabet):
        return alphabet[nombre]
    while nombre != 0:
        nombre, i = divmod(nombre, len(alphabet))
        base64_result = alphabet[i] + base64_result
    return base64_result


def hashing(game_val_grid: GridTuple) -> str:
    """Fonction de hashage d'une grille"""
    hashage = ""
    for dimension in game_val_grid:
        for game_val in dimension:
            if game_val == ROUGE:  # 1
                hashage += "1"
            elif game_val == BLEU:  # 2
                hashage += "2"
            elif game_val == EMPTY:  # 0
                hashage += "0"
            else:  # cas NDEF
                continue
    # print(len(hashage))
    # print(len(str(hex(int(hashage)))[2:]))
    # print(len(str(base64(int(hashage)))))
    return str(base64(int(hashage)))


#! ---------------------- Reflexions et rotations ---------------------- !#


def rotation(grille: GridTuple, dico_conversion: DictConv) -> List[GridTuple]:  #! OK
    """effectue une rotation de 60° de la grille hexagonale, utile pour les symétries"""
    taille_grille = len(grille) // 2
    rot_1 = tuple_to_list(init_grille_gopher(taille_grille)[0])
    rot_2 = copy.deepcopy(rot_1)
    rot_3 = copy.deepcopy(rot_1)
    rot_4 = copy.deepcopy(rot_1)
    rot_5 = copy.deepcopy(rot_1)

    #!rotation 60°
    for cell in dico_conversion.keys():  # enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1] - cell[0])
        rot_1[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

    #!rotation 120°
    for cell in dico_conversion.keys():  # enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1] - cell[0])
        rot_2[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_1[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

    #!rotation 180°
    for cell in dico_conversion.keys():  # enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1] - cell[0])
        rot_3[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_2[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

    #!rotation 240°
    for cell in dico_conversion.keys():  # enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1] - cell[0])
        rot_4[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_3[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

    #!rotation 300°
    for cell in dico_conversion.keys():  # enumeration de tout les element de la matrice
        new_cell = (cell[1], cell[1] - cell[0])
        rot_5[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = rot_4[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

    return [
        grille,
        liste_to_tuple(rot_1),
        liste_to_tuple(rot_2),
        liste_to_tuple(rot_3),
        liste_to_tuple(rot_4),
        liste_to_tuple(rot_5),
    ]


def reflexion(grille: GridTuple, dico_conversion: DictConv) -> List[GridTuple]:  #! OK
    """effectue les 6 reflexions possible d'une grille donnée, utile pour les symétries"""
    new_grille = tuple_to_list(grille)
    taille_grille = len(new_grille) // 2
    ref_1 = tuple_to_list(init_grille_gopher(taille_grille)[0])
    ref_2 = copy.deepcopy(ref_1)
    ref_3 = copy.deepcopy(ref_1)
    ref_4 = copy.deepcopy(ref_1)
    ref_5 = copy.deepcopy(ref_1)
    ref_6 = copy.deepcopy(ref_1)

    for cell in dico_conversion.keys():  # enumeration de tout les element de la matrice
        #! symetrie axiale verticale
        new_cell = (cell[1], cell[0])
        ref_1[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

        #! symetrie axiale horizontale
        new_cell = (-cell[1], -cell[0])
        ref_2[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

        #! symetrie axe bleu
        new_cell = (-cell[0], cell[1] - cell[0])
        ref_3[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

        #! symetrie axe rouge
        new_cell = (cell[0] - cell[1], -cell[1])
        ref_4[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

        #! autre axe
        new_cell = (cell[0], cell[0] - cell[1])
        ref_5[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

        #! autre axe
        new_cell = (cell[1] - cell[0], cell[1])
        ref_6[dico_conversion[new_cell][0]][dico_conversion[new_cell][1]] = grille[
            dico_conversion[cell][0]
        ][dico_conversion[cell][1]]

    return [
        liste_to_tuple(ref_1),
        liste_to_tuple(ref_2),
        liste_to_tuple(ref_3),
        liste_to_tuple(ref_4),
        liste_to_tuple(ref_5),
        liste_to_tuple(ref_6),
    ]


def memoize(fonction):
    """Memoize decorator pour la fonction alpha_beta"""
    cache = {}  # closure

    def g_memo(
        grille: GridTuple,
        dico_conversion: DictConv,
        player: Player,
        dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher],
        depth,
        alpha,
        beta,
    ):
        grille_hashed = hashing(grille)
        if grille_hashed in cache:
            return cache[grille_hashed]

        val = fonction(
            grille, dico_conversion, player, dico_legaux, depth, alpha, beta
        )  #! c'est bien grille et non grille_hashed
        if val[1] is not None:
            # print(val)
            cache[grille_hashed] = val
            ref = reflexion(grille, dico_conversion)
            for grille_ref in ref:  #! on fait 6 reflexions de la grille de depart
                refhash = hashing(grille_ref)
                if refhash not in cache:
                    cache[
                        refhash
                    ] = val  #! on fini par append le hash des 36 grilles dans le cache
        return val

    return g_memo


def trier_actions(
    grid: GridTuple,
    dico_conversion: DictConv,
    liste_actions: List[ActionGopher],
    dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher],
    player_max: Player,
) -> List[ActionGopher]:
    """Trie les actions en fonction du joueur"""
    liste_values = []

    if player_max == ROUGE:
        for action in liste_actions:
            _, dico_legaux = play_action(
                grid, dico_conversion, action, BLEU, dico_legaux
            )
            liste_values.append(evaluation(dico_legaux))
    else:
        for action in liste_actions:
            _, dico_legaux = play_action(
                grid, dico_conversion, action, ROUGE, dico_legaux
            )
            liste_values.append(evaluation(dico_legaux))

    return [x for _, x in sorted(zip(liste_values, liste_actions))]


@memoize
def alpha_beta(
    grid: GridTuple,
    dico_conversion: DictConv,
    player_max: Player,
    dico_legaux: Tuple[TupleLegalGopher, TupleLegalGopher],
    depth,
    alpha,
    beta,
) -> Tuple[Score, Optional[ActionGopher]]:
    """fonction alpha beta pour le jeu gopher"""

    if depth == 0 or final(player_max, dico_legaux):
        return evaluation(dico_legaux), None

    if player_max == ROUGE:
        best_value = -INF
        best_action = None
        for action in trier_actions(
            grid,
            dico_conversion,
            liste_coup_legaux(dico_legaux, ROUGE),
            dico_legaux,
            player_max,
        ):  #! pas d'erreur dans trier_actions

            grid, dico_legaux = play_action(
                grid, dico_conversion, action, ROUGE, dico_legaux
            )

            new_value, _ = alpha_beta(
                grid, dico_conversion, BLEU, dico_legaux, depth - 1, alpha, beta
            )
            # print("ROUGE",best_value)
            if new_value >= best_value:
                best_value = new_value
                best_action = action
            alpha = max(alpha, new_value)
            if beta <= alpha:
                break  # Coupe bêta
        return best_value, best_action

    min_value = INF
    best_action = None
    for action in trier_actions(
        grid,
        dico_conversion,
        liste_coup_legaux(dico_legaux, BLEU),
        dico_legaux,
        player_max,
    ):
        grid, dico_legaux = play_action(
            grid, dico_conversion, action, BLEU, dico_legaux
        )

        new_value, _ = alpha_beta(
            grid, dico_conversion, ROUGE, dico_legaux, depth - 1, alpha, beta
        )
        # print("BLEU",best_value)
        if new_value <= min_value:
            min_value = new_value
            best_action = action
        beta = min(beta, new_value)
        if beta <= alpha:
            break  # Coupe alpha
    return min_value, best_action


def boucle_rd_ai(taille_grille: int, depth: int) -> float:  # ! boucle de jeu OK
    """Boucle de jeu pour un joueur aléatoire et un joueur alpha beta"""
    grille, dico_conversion = init_grille_gopher(taille_grille)
    dico_legaux = init_dico_legaux_gopher(dico_conversion)
    joueur = BLEU
    grille, dico_legaux = play_action(
        grille,
        dico_conversion,
        rd.choice(list(dico_conversion.keys())),
        joueur,
        dico_legaux,
    )

    while True:
        if joueur == ROUGE:
            joueur = BLEU
        else:
            joueur = ROUGE  # changment de joueur

        # print("Rouge", liste_coup_legaux(dico_legaux, ROUGE))
        # print("Bleu", liste_coup_legaux(dico_legaux, BLEU))

        if joueur == ROUGE:
            if final(ROUGE, dico_legaux):
                break
            # print("Rouge joue")
            _, action = alpha_beta(
                grille, dico_conversion, joueur, dico_legaux, depth, -INF, INF
            )
            # print("Action : ", action)
            # print("Evaluation : ", evaluation)
            # print("Dico :", liste_coup_legaux(dico_legaux, joueur))
            grille, dico_legaux = play_action(
                grille, dico_conversion, action, joueur, dico_legaux
            )

        else:
            if final(
                BLEU, dico_legaux
            ):  # verifie si le joueur BLEU a encore des coups légaux
                break
            # print("Bleu joue")
            action = rd.choice(liste_coup_legaux(dico_legaux, joueur))
            grille, dico_legaux = play_action(
                grille, dico_conversion, action, joueur, dico_legaux
            )

    # aff.afficher_hex(grille, dico_conversion= dico_conversion)
    return score_final(dico_legaux)


#!test
# boucle = 0
# for i in tqdm(range(1)):
#     if boucle_rd_ai(6, 5) == INF: #6/3 3.59 sec/it, 6/5 17.8 sec/it
#         boucle +=1
# print(boucle)


def strategie_impaire(
    coup_bleu: ActionGopher, grille: GridTuple, dico_conversion: DictConv
) -> ActionGopher:
    """renvoie les meilleurs coup pour win les tailles impaire superieurs à 5"""

    voisins_trouve = voisins(dico_conversion, coup_bleu)
    for coup in voisins_trouve:
        if grille[dico_conversion[coup][0]][dico_conversion[coup][1]] == ROUGE:
            vector = (coup_bleu[0] - coup[0], coup_bleu[1] - coup[1])
            return (coup_bleu[0] + vector[0], coup_bleu[1] + vector[1])
    raise ValueError("strategie_impaire : pas de coup trouvé")


def boucle_rd_strategie_impaire(taille_grille: int) -> float:
    """Boucle de jeu pour un joueur aléatoire et un joueur alpha beta"""
    assert taille_grille % 2 == 1, "La taille de la grille doit être impaire"
    grille, dico_conversion = init_grille_gopher(taille_grille - 1)
    dico_legaux = init_dico_legaux_gopher(dico_conversion)
    joueur = ROUGE
    grille, dico_legaux = play_action(
        grille, dico_conversion, (0, 0), joueur, dico_legaux
    )
    action_bleu = (0, 0)
    while True:

        if joueur == ROUGE:
            joueur = BLEU
        else:
            joueur = ROUGE  # changment de joueur

        # print("Rouge", liste_coup_legaux(dico_legaux, ROUGE))
        # print("Bleu", liste_coup_legaux(dico_legaux, BLEU))

        if joueur == ROUGE:
            if final(ROUGE, dico_legaux):
                break

            action_rouge = strategie_impaire(action_bleu, grille, dico_conversion)
            grille, dico_legaux = play_action(
                grille, dico_conversion, action_rouge, joueur, dico_legaux
            )

        else:
            if final(
                BLEU, dico_legaux
            ):  # verifie si le joueur BLEU a encore des coups légaux
                break
            # print("Bleu joue")
            action_bleu = rd.choice(liste_coup_legaux(dico_legaux, joueur))
            grille, dico_legaux = play_action(
                grille, dico_conversion, action_bleu, joueur, dico_legaux
            )

    # aff.afficher_hex(grille, dico_conversion= dico_conversion)
    return score_final(dico_legaux)


#!test
# compteur = 0
# for i in tqdm(range(1000)):
#     if boucle_rd_strategie_impaire(7) == -INF:
#         compteur +=1
# print(compteur)
