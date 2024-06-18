#!/usr/bin/python3

import ast
import argparse
import dodo
import gopher as goph #importation des elements du jeu 
from typing import Dict, Any
from gndclient import start, Action, Score, Player, State, Time, DODO_STR, GOPHER_STR

Environment = Dict[str, Any] #contients les elements necessaire a notre fonction min max. 

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


def initialize(game: str, state: State, player: Player, hex_size: int, total_time: Time):
    """initialise l'environement en fonction du jeu choisi"""

    environement = {} #environement est un dictionnaire qui contient les elements necessaire à notre programme pour bien jouer au jeu.
    if game == "dodo" or game == "Dodo" or game == "DODO":
        #initialisation de l'environement pour dodo
        environement["game"] = "dodo"
        environement["grille"], environement["dico_conversion"] = dodo.init_grille_dodo(hex_size-1)
        environement["joueur"] = player
        environement["depth"] = 3
        return environement

    if game == "gopher" or game == "Gopher" or game == "GOPHER":
        #initialisation de l'environement pour gopher
        environement["game"] = "gopher"
        environement["grille"], environement["dico_conversion"] = goph.init_grille_gopher(hex_size-1)
        environement["dico_legaux"] = goph.init_dico_legaux_gopher(environement["dico_conversion"])
        environement["joueur"] = player
        environement["is_odd"] = True if hex_size % 2 == 1 else False #booleen qui determine si la taille de la grille est pair ou impaire
        environement["depth"] = 3 
        #pour l'implementation des differentes strategies du jeu en fonction de la taille de la grille
        return environement

    print("Erreur: Le jeu n'existe pas")
    return {}



def update_env(env: Environment, state:State) -> Environment:
    """fonction permettant de recuperer le coup joué par l'adversaire et de le jouer afin de mettre a jour la grille
    et les dico legaux"""

    #! DODO
    if env["game"] == "dodo":
        #mise a jour de l'environement pour dodo
        depart = (0,0)
        arrivee = (0,0)
        for element in state : 
            case = element[0]
            value = element[1]
            if value != env["grille"][env["dico_conversion"][case][0]][env["dico_conversion"][case][1]]:
                if value == EMPTY: #si la case qui a changé est vide, c'est que c'est la case de depart de l'aderseaire
                    depart = env["dico_conversion"][case]
                else: #sinon elle contient la valeur du joueur adverse et c'est la case d'arrivée
                    arrivee = env["dico_conversion"][case]
        #mise a jour de l'environement
        env["grille"] = dodo.play_action(env["grille"],env["dico_conversion"] ,(depart, arrivee), env["joueur"])
        env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU #changer de joueur
        return env

    #! GOPHER
    if env["game"] == "gopher":
        for element in state:
            case = element[0]
            value = element[1]
            if value != env["grille"][env["dico_conversion"][case][0]][env["dico_conversion"][case][1]]: #si la valeur est differente de celle de la grille 
                #c'est que c'est une valeur qui a changé, donc la valeur que l'adversaire a joué. 
                action_adverse = case
        #mise a jours de l'environement
        env["grille"], env["dico_legaux"] = goph.play_action(env["grille"], env["dico_conversion"],action_adverse, env["joueur"], env["dico_legaux"])
        env["joueur"] = ROUGE if env["joueur"] == BLEU else BLEU
        return env, action_adverse

    print("Erreur: Le jeu n'existe pas")
    return {}


def strategy_brain(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    
    env = update_env(env, state) #update l'environement avec le coup joué par l'aderseaire
    if env["game"] == "dodo":
        #strategie dodo
        

        action = dodo.alpha_beta_dodo(env["grille"], env["dico_legaux"], env["joueur"], env["depth"], -dodo.INF, dodo.INF)
        

        
    elif env["game"] == "gopher":
        if env["is_odd"]:
            #strategie gopher pour les grilles impaire >= 5
            coup_bleu =
            action = goph.strategie_impaire(coup_bleu,env["grille"], env["dico_conversion"])


        else:
            #strategie gopher pour les grilles paire ou les grilles de taille < 5
            action = goph.alpha_beta_gopher(env["grille"], env["dico_legaux"], env["joueur"], env["depth"], -goph.INF, goph.INF)
            env["grille"], env["dico_legaux"] = goph.play_gopher(env["grille"], action, env["dico_legaux"], env["joueur"])
            return env, action


    else:
        print("Erreur: Le jeu n'existe pas")
        return (env, None)
    
    return (env, t) #! renvoiyer ici l'environemenet et l'action a effectuer

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
