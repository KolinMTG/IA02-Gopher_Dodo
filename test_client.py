#!/usr/bin/python3

import ast
import argparse
import dodo
import gopher as goph #importation des elements du jeu 
from typing import Dict,List, Any, Tuple, Union
from gndclient import start, Action, Score, Player, State, Time, DODO_STR, GOPHER_STR
import affichage as aff

Environment = Dict[str, Any] #contients les elements necessaire a notre fonction min max. 
# Player = int #Joueur : donc ROUGE ou BLEU
GameValue = int #valeur d'une case : donc NDEF, EMPTY, ROUGE, BLEU


Cell = Tuple[int, int] #Coordonnées d'une case
CellMat = Cell  #Coordonnées d'une case dans la matrice
CellHex = Cell #Coordonnées d'une case dans l'affichage hexagonal a fournir au serveur

GridTuple = Tuple[Tuple[GameValue]] #La grille de jeu, est un tableau numpy 2D de GameValue
GridList = List[List[GameValue]] #La grille de jeu, est un tableau numpy 2D de GameValue
# ActionGopher = Cell
# ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
# Action = Union[ActionGopher, ActionDodo]

#Grid = Union[GridGopher, GridDodo]
#Environement = Dict[grille : Grid, dico_conversion : Dict_Conv, dico_legaux : ]


EMPTY = 0
ROUGE = 1
BLEU = 2
NDEF = -1 #case non définie

#! //////// structure des environement selon le jeu : \\\\\\\\
#? DODO : 
# environement = {
#     "game" : "dodo"(const),
#     "grille" : GridDodo,
#     "dico_conversion" : Dict_Conv,
#     "direction" : DirectionJeu,
#     "joueur" : Player,
#     "depth" : int
# }

#? GOPHER :
# environement = {
#     "game" : "gopher"(const),
#     "grille" : GridGopher,
#     "dico_conversion" : Dict_Conv,
#     "dico_legaux" : Dict_Legaux,
#     "joueur" : Player,
#     "is_odd" : bool,
#     "depth" : int
# }
print("Client started")


def initialize(game: str, state: State, player: Player, hex_size: int, total_time: Time) -> Environment:
    print(game)
    """initialise l'environement en fonction du jeu choisi"""
    print("Initialisation de l'environement")
    environement = {} #environement est un dictionnaire qui contient les elements necessaire à notre programme pour bien jouer au jeu.

    #! DODO
    if game == "dodo" or game == "Dodo" or game == "DODO":
        print("Initialisation pour le jeu Dodo")
        print("Nous somme le joueur ", player)
        #initialisation de l'environement pour dodo
        environement["game"] = "dodo"
        environement["joueur"] = ROUGE
        environement["depth"] = 6
        environement["player_we_are"] = player
        environement["premier_coup"] = True

        compteur_one_ligne = 0
        compteur_corner = 0

        #parcour du state pour savoir dans quel mode on est
        for element in state :
            case = element[0]
            value = element[1]
            if case[0] + case [1] == hex_size -2 or case[0] + case[1] == -hex_size +2:
                if value == ROUGE or value == BLEU:
                    compteur_one_ligne +=1
                elif value == EMPTY :
                    compteur_corner +=1

        #initialisation de la grille
        if compteur_one_ligne <= 1: #cas d'un jeu corner
            environement["grille"], environement["dico_conversion"], environement["direction"]= dodo.init_grille_dodo_corners(hex_size-1)
        else : #cas d'un jeu one line
            environement["grille"], environement["dico_conversion"], environement["direction"]= dodo.init_grille_dodo_one_line(hex_size-1)
        return environement


    #! GOPHER
    if game == "gopher" or game == "Gopher" or game == "GOPHER":
        #initialisation de l'environement pour gopher
        environement["game"] = "gopher"
        environement["grille"], environement["dico_conversion"] = goph.init_grille_gopher(hex_size-1)
        environement["dico_legaux"] = goph.init_dico_legaux_gopher(environement["dico_conversion"])
        environement["joueur"] = ROUGE #on sait d'après les règles que c'est tjr ROUGE qui commence
        environement["player_we_are"] = player
        environement["premier_coup"] = True
        environement["is_odd"] = True if hex_size % 2 == 1  and hex_size >= 5 else False #booleen qui determine si la taille de la grille est pair ou impaire
        environement["depth"] = 7
        #pour l'implementation des differentes strategies du jeu en fonction de la taille de la grille
        print("Initialisation terminé pour le jeu Gopher de taille ", hex_size)
        print("Environement actuel : ", environement)
        return environement

    print("Erreur: Le jeu n'existe pas")
    return {}

premier_coup = True

def update_env(env: Environment, state:State) -> Tuple[Environment, Action]:
    """fonction permettant de recuperer le coup joué par l'adversaire et de le jouer afin de mettre a jour la grille
    et les dico legaux"""
    #! DODO
    if env["game"] == "dodo":
        #mise a jour de l'environement pour dodo
        depart = None
        arrivee = None
        print("grille avant coup adverse")

        for element in state : 
            case = element[0]
            value = element[1]
            
            if value != env["grille"][env["dico_conversion"][case][0]][env["dico_conversion"][case][1]]:

                if value == EMPTY: #si la case qui a changé est vide, c'est que c'est la case de depart de l'adverseaire
                    depart = case
                elif value == env["joueur"]: #sinon elle contient la valeur du joueur adverse et c'est la case d'arrivée
                    arrivee = case

        #mise a jour de l'environement
        env["grille"] = dodo.play_action(env["grille"], env["dico_conversion"], (depart, arrivee), env["joueur"])
        print("grille apres coup adverse")
        print("action jouée", (depart, arrivee))
        env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU #changer de joueur
        return env, (depart, arrivee)

    #! GOPHER
    if env["game"] == "gopher": #!semble ok pour la partie Gopher, problème pour Dodo
        for element in state:
            case = element[0]
            value = element[1]
            if value != env["grille"][env["dico_conversion"][case][0]][env["dico_conversion"][case][1]]: #si la valeur est differente de celle de la grille 
                #c'est que c'est une valeur qui a changé, donc la valeur que l'adversaire a joué. 
                action_adverse = case
                break #il n'y a qu'une seul action qui est joué par l'adversaire de toute façon
        #mise a jours de l'environement
        env["grille"], env["dico_legaux"] = goph.play_action(env["grille"], env["dico_conversion"],action_adverse, env["joueur"], env["dico_legaux"])
        env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU #changer de joueur
        return env, action_adverse

    print("Erreur: Le jeu n'existe pas")
    return {}, (0,0)



def strategy_brain(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    """fonction qui permet de jouer en fonction du jeu choisi"""


    #! PREMIER COUP 
    #cette action n'est repeté que une seule fois, c'est le premier coup du jeu
    if env["player_we_are"] == ROUGE and env["premier_coup"] is True: #! SI ON EST ROUGE ET ON COMMENCE !!!
        #ca veut dire qu'on commence, il faut donc jouer un coup en premier
        # le premier coup est toujours le meme
        env["premier_coup"] = False #on a joué le premier coup
        if env["game"] == "dodo": 
            action = ((-1, -1), (0,0))
            env["grille"] = dodo.play_action(env["grille"], env["dico_conversion"], action, env["joueur"])
            env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU
            return env, action

        if env["game"] == "gopher":
            action = (0,0)
            env["grille"], env["dico_legaux"] = goph.play_action(env["grille"], env["dico_conversion"], action, env["joueur"], env["dico_legaux"])
            env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU
            return env, action


    #! SUITE DU JEU DANS TOUT LES CAS
    env, action_adverse = update_env(env, state)

    #! DODO
    if env["game"] == "dodo":

        _,action = dodo.alpha_beta_dodo(env["grille"], env["dico_conversion"],env["direction"], env["joueur"], env["depth"], -dodo.INF, dodo.INF) #appel de la fonction alpha beta pour jouer
        print("action choisit pour nous", action)
        env["grille"] = dodo.play_action(env["grille"], env["dico_conversion"], action, env["joueur"]) #mise a jour de la grille avec notre coup
        print("grille après notre coup")
        env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU #changer de joueur, on a fini de jouer c'est au tour de l'adversaire


    #! GOPHER
    if env["game"] == "gopher":

        print("strategy_brain::On joue a GOPHER")
        if env["is_odd"]:
            #strategie gopher pour les grilles impaire >= 5 et joueur = rouge
            action = goph.strategie_impaire(action_adverse,env["grille"], env["dico_conversion"])
            env["grille"], _ = goph.play_action(env["grille"], env["dico_conversion"], action, env["joueur"], env["dico_legaux"])
            env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU #changement de joueur, on a fini de jouer c'est au tour de l'adversaire

        else:

            print("la grille est de taille pair, ou inferieur à 5")
            _,action = goph.alpha_beta(env["grille"],env["dico_conversion"], env["joueur"],env["dico_legaux"], env["depth"], -goph.INF, goph.INF)
            if action == None:
                action = (0,0)
            env["grille"], env["dico_legaux"] = goph.play_action(env["grille"], env["dico_conversion"], action, env["joueur"], env["dico_legaux"])
            env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU #changement de joueur, on a fini de jouer c'est au tour de l'adversaire

    return env, action



#TODO Gopher joueur BLEU OK
#TODO Dodo joueur BLEU OK
#TODO Gopher joueur ROUGE A tester
#TODO Dodo joueur ROUGE A tester


# def strategy_brain(
#     env: Environment, state: State, player: Player, time_left: Time
# ) -> tuple[Environment, Action]:
#     print("New state ", state)
#     print("Time remaining ", time_left)
#     print("What's your play ? ", end="")
#     s = input()
    
#     t = ast.literal_eval(s) 
#     env = {"info": 1}
#     print(env, t)
#     return (env, t) #! renvoiyer ici l'environemenet et l'action a effectuer 


def final_result(state: State, score: Score, player: Player):
    
    print(f"Ending: {player} wins with a score of {score}") 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ClientTesting", description="Test the IA02 python client"
    )

    parser.add_argument("group_id")
    parser.add_argument("members")
    parser.add_argument("password")
    parser.add_argument("-s", "--server-url", default="http://localhost:8080/")
    parser.add_argument("-d", "--disable-dodo", action="store_true")
    parser.add_argument("-g", "--disable-gopher", action="store_true")
    args = parser.parse_args()

    available_games = [DODO_STR, GOPHER_STR]
    if args.disable_dodo:
        available_games.remove(DODO_STR)
    if args.disable_gopher:
        available_games.remove(GOPHER_STR)

    start(
        args.server_url,
        args.group_id,
        args.members,
        args.password,
        available_games,
        initialize,
        strategy_brain,
        final_result,
        gui=True,
    )
