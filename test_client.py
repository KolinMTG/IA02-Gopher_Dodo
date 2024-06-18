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



def initialize(game: str, state: State, player: Player, hex_size: int, total_time: Time):
    """initialise l'environement en fonction du jeu choisi"""

    environement = {} #environement est un dictionnaire qui contient les elements necessaire à notre programme pour bien jouer au jeu.
    if game == "dodo" or game == "Dodo" or game == "DODO":
        #initialisation de l'environement pour dodo
        environement["grille"], environement["dico_conversion"] = dodo.init_grille_dodo(hex_size-1)
        environement["dico_legaux"] = dodo.init_legal_moves(environement["grille"], player)
        environement["joueur"] = player
        return environement

    if game == "gopher" or game == "Gopher" or game == "GOPHER":
        #initialisation de l'environement pour gopher
        environement["grille"], environement["dico_conversion"] = goph.init_grille_gopher(hex_size-1)
        environement["dico_legaux"] = goph.init_legal_moves(environement["grille"], player)
        environement["joueur"] = player
        return environement

    print("Erreur: Le jeu n'existe pas")
    return {}



# def initialize(
#     game: str, state: State, player: Player, hex_size: int, total_time: Time
# ) -> Environment:
#     print("Init")
#     print(
#         f"{game} playing {player} on a grid of size {hex_size}. Time remaining: {total_time}"
#     )
#     return {}


def strategy_brain(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    print("New state ", state)
    print("Time remaining ", time_left)
    print("What's your play ? ", end="")
    s = input()
    
    t = ast.literal_eval(s) 
    env = {"info": 1}
    print(env, t)
    return (env, t) #! renvoiyer ici l'environemenet et l'action a effectuer 


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
