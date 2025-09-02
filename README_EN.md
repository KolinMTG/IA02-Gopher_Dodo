# IA02 Project

## Introduction

This project was carried out as part of the Computer Engineering program at the University of Technology of Compiègne (UTC), and more specifically as part of the IA02 course: Logic and Problem Solving through Research.

The goal of this project is to code the games Gophr and Dodo created by Mark Steere, and then develop algorithms capable of playing these games.
The goal of this project was to code algorithms capable of playing Mark Steere's games Gopher and Dodo:
1. Mark Steere's website: https://www.marksteeregames.com
2. Dodo rules: https://www.marksteeregames.com/Dodo_rules.pdf
3. Gopher rules: https://www.marksteeregames.com/Gopher_hex_rules.pdf

Then, the different algorithms coded by the students competed in a tournament hosted via an online server. The different players also had a limited time to make their moves, so speed and optimization of the algorithms were essential.

## Overall Structure

This repository consists of six files:
2. The `gndclient.py` file, which implements the server's functionality
3. The `gndserver.exe` file, which must be run to launch the server
4. The `affichage.py` file, which implements a user-friendly game display
5. The `gopher.py` file, which implements our algorithm for Gopher
6. The `dodo.py` file, which implements our algorithm for Dodo
7. The `test_client.py` file, which allows you to play on the server with our algorithms

## Choice of Data Representation

- Coordinates:
![Coordinate system shown for a grid of size 7](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/grid_hex.png)
- Matrix Representation:
![Grid representation of size 7 in the form of a 2D matrix](https://moodle.utc.fr/pluginfile.php/335042/mod_label/intro/matrix_hex.png)

## Choice of the algorithm used

For our project, we developed an algorithm aimed at **maximizing performance** while maintaining **high execution speed**, essential to meet the time constraints of the competition against other players. We chose to implement the `alpha-beta` algorithm, which we significantly optimized. The flexibility offered by the ability to adjust the algorithm's depth allows us to obtain an efficient and sufficiently fast solution by adjusting this depth as needed.

In our effort to improve the algorithm's performance, we implemented several optimizations detailed below:
- Localized calculation of legal moves for Gopher to save computation time.
- Use of a memoization function for the alpha-beta algorithm.
- Sorting of the alpha-beta tree nodes to optimize alpha and beta cuts, inspired by the practices described in the German version of the Wikipedia article on alpha-beta: [Alpha-Beta-Suche](https://de.wikipedia.org/wiki/Alpha-Beta-Suche).
- Implementation of a hash function for Gopher and Dodo grids, saving memory space by keeping the grids memorized.

### Local calculation of legal moves for Gopher

We noticed that the moves made by players in the Gopher case only influence the following legal moves on a small part of the grid. We used this information to recalculate only the legal moves of the different players locally, i.e., to recalculate the legal moves only around the move made.

When a player plays in position `(0,0)`, the potentially changed legal moves are the moves that involve the squares adjacent to the filled square.
We therefore simply need to test the legality of the six neighboring squares: `(1, 1), (1, 0), (0, -1), (-1, -1), (-1, 0), (0, 1)`.

We then chose to store the list of legal moves in a Python dictionary `dico_legaux` of type `Dict[Case, bool]`, where legal moves are represented by `True`. This system allows us to quickly check for the existence of a move in the grid, which can vary in size.

In `Gopher.py`, the `init_dico_legaux_gopher()` function initializes the dictionaries of legal moves (all moves are initialized to `False` at the beginning of the game). Then, the `update_dico_legaux()` function updates these dictionaries after a move has been made by a player. This function is called from the `play_action()` function, which manages the execution of an action for a given player and returns the modified environment (i.e., all the information needed for the game).

**Our method for determining legal moves offers a significant gain in terms of computation time. By restricting the test to at most six neighbors of the last action played, the complexity of this step is reduced from `O(N^2)`, where N is the size of the grid, to a constant `O(1)` complexity for this part of the computation.**

#### Why not use the same technique for Dodo?
Dodo is a more complex game where tokens can be moved from one square to another, not just placed on them. Storing the complete list of all possible moves as a dictionary would therefore be very expensive in terms of memory. Furthermore, the complexity of updating this dictionary would not justify the time savings compared to directly calculating the legality of moves for all squares.

### Sorting the Alpha-Beta Nodes

While exploring possible improvements to the alpha-beta algorithm, we discovered that it was beneficial to sort the nodes (i.e., the tested moves) of the alpha-beta. This sorting allows us to perform alpha or beta cuts more quickly, by testing the most promising branches first. According to the Wikipedia article mentioned above, this optimization can significantly reduce computation time:

Here's what the article states: Algorithm Ratings Cutoffs Before Cutoffs Rechenzeit in Sekunden

See the article on [Wikipedia](https://de.wikipedia.org/wiki/Alpha-Beta-Suche).

| Algorithm | Ratings | Cutoffs | % Cutoffs | Computation Time |
|--------------------------------|--------------|-----------|---------------|----------------|
| **Minimax** | 28,018,531 | 0 | 0.00% | 134.87 s (Minimax Algorithm) |
| **AlphaBeta** | 2,005,246 | 136,478 | 91.50% | 9.88 s (Alpha-Beta Algorithm) |
| **AlphaBeta + Node Sorting** | 128,307 | 27,025 | 99.28% | 0.99 s (Alpha-Beta Algorithm with Node Sorting) |

### Implementation of memoization for players

When searching for possible moves for a player, it is possible to encounter game states that have already been encountered.

To avoid recalculating possible moves using our improved alphabeta algorithm, we implemented a memoization function that stores the best move for a previously encountered game state.

### Grid hash function

To best represent the game state, whether on dodo or gopher, we chose to use a hash function that stores the game state as a string. This string is then used as a key in a dictionary that stores the possible moves for a given game state.

How do we get this string?

We use the `hashing()` function, which takes the current grid *GameValues* as a parameter. It will iterate through the grid and, for each square encountered, will add the number 0, 1, or 2 to the output string.
- 0 if the square is unoccupied (`EMPTY`)
- 1 if the square is occupied by the red player (`RED`)
- 2 if the square is occupied by the blue player (`BLUE`)

We then obtain a large number representing the state of the grid at a given time. This number is then converted from base 10 to base 64 (`base64()` function) to obtain a shorter string. This takes up less memory space.

`hashing()` then returns the string previously converted to base 64.

We tested this hash function on completely filled grids of size 6 (worst case).
- The raw number without conversion was the same size as the grid, i.e., 3*6*(6-1)+1 = 91 characters.
- The number converted to base 16 was 76 characters long.
- The number converted to base 64 was 51 characters long.

**This results in a 40% improvement in the size of the string and, by extension, in the amount of memory used.**

### Symmetry Management

A hexagonal grid has many axes of symmetry (6 in total), so it is useful to implement a calculation of these symmetries. We chose to implement the calculation of symmetries in our memoization. Thus, each time a position is memoized, the other 5 positions, symmetrical and therefore strictly equivalent, are also added to the cache.
The `reflexion()` function calculates all symmetries for a given grid.

### Memoization Function

The `memoize()` function is then used as a decorator for the `alpha_beta()` function. It allows each move calculated (or not) by the function to store the newly calculated move in a dictionary of the form `Dict[str, Tuple[int, int]]` (for gopher) or `Dict[str, Tuple[Tuple[int, int],Tuple[int, int]]]` (for dodo). The key to this dictionary is the string obtained by the `hashing()` function, and the associated value is the best move calculated for this game state.

The gopher case is special because the game board contains a large number of symmetries. With each new move calculated, we store, if this has not already been done, the 6 reflections and the 6 rotations from These reflections are cached. So, each time we play, we potentially store 36 game states in the cache.

## Using our program:

### Locally

To start a game of dodo or gopher with our own game loop, simply go to the `dodo.py` or `gopher.py` file and run the corresponding functions for the game loops against a random player, namely:
- `loop_rd_alpha_beta(grid_size: int, depth: int) -> float` for dodo.
- `loop_rd_ai(grid_size: int, depth: int) -> float:` for gopher.

To display the game state, simply uncomment the line(s) `aff.display_hex(grid, dictionary_conversion)`.

These two functions then return the score of the game played.

### Via the server

*From the readme provided in the server repository*

***__START__***
The server runs from the command line (terminal on Linux and macOS, PowerShell on Windows)

1. Copy the correct executable into your working directory. We then assume that the executable is called `gndserver`.
2. Add execution rights (if necessary under Linux and MacOS): `chmod a+x gndserver`.
3. Check operation and view options: `./gndserver`.

```bash
# all options
./gndserver -h
```

```bash
# start a dodo server against a random player
./gndserver -game dodo -random
```

```bash
# start a gopher server against a random player
./gndserver -game gopher -random
```

```bash
# start a gopher server against a random gopher player, which will be the blue player
./gndserver -game gopher -rcolor blue -random
```

```bash
# reset everything
rm config.json server.json
```
***__FINISH__***

First, you need to launch a terminal and navigate to the directory where the server is located. Launch the server there with the desired options.

Go to a terminal again after launching the server. Make sure you have:

1. Copied the `gndclient.py` file to your working directory
2. Copied the `test_client.py` file to your working directory

Finally, in this same terminal, run the following command:

```bash
# launch the client
python test_client.py 12 toto totovelo
```

With `12` being the group number, `toto` being the player's name, and `totovelo` being the player's password.

A game should then launch and play before your eyes.

## Outlook and areas for improvement.

### Using Multicore

We considered using multicore to execute all alpha-betas during a game round. After implementation, our program was no faster, and in some cases, even slower. We therefore abandoned this optimization avenue.

### Legal Moves via the API.

Despite the fact that our program runs smoothly locally, we encountered problems using the server during the tournament. It appears that our program was returning illegal moves, even though this problem had never occurred locally, either via our in-house game loop or via the server game loop.
We were unable to find the source of the problem.

## Troubleshooting

All code runs normally without bugs. If you have any problems, please contact us at the following email addresses:
- colin.manyri@etu.utc.fr
- bastien.cuvillier@etu.utc.fr

## Authors

- Bastien Cuvillier (https://github.com/Voln1x)
- Colin Manyri (https://github.com/KolinMTG)
