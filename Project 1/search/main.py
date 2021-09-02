"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:

from search.util import print_board, print_slide, print_swing

from search.preprocess import visual_data_preprocess, gen_my_tokens, gen_goal_for_token, gen_opponent_tokens, gen_blocks

from search.board import calculate_distance, reset_movement_status, check_win_condition, update_opponent_tokens, synchronize_goal

from search.board import get_token_adjacency, gen_closest_goal, make_move_recursive, token_battle

# TODO:
# Find and print a solution to the board configuration described
# by `data`.
# Why not start by trying to print this configuration out using the
# `print_board` helper function? (See the `util.py` source code for
# usage information).


def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    print("--------------loading successful-----------------")
    print("--------------current state----------------------")

    # generate and analysis the input data
    current_config = visual_data_preprocess(data)
    print_board(current_config)
    my_current_config = gen_my_tokens(data)
    config_with_goals = gen_goal_for_token(data,my_current_config)
    blocks = gen_blocks(data)
    opponent_tokens = gen_opponent_tokens(data)

    # a counter to count the number of turns taken to end the game
    turn = 0

    # list to hold the coordinates that each token comes from
    prev_pos = [[] for i in range(0,len(config_with_goals))]

    # list to hold action sequence of all tokens
    move_hist_array = [[] for i in range(len(config_with_goals))]

    # path finding begins
    print("# Search begin!")
    print("")
    while check_win_condition(config_with_goals,opponent_tokens) is False:
        num_of_tokens = len(config_with_goals)
        current_iterator = 0
        turn += 1

        # list to hold all adjacent coordinates of tokens
        adjacency_list = [[] for i in range(len(config_with_goals))]
        # update adjacency list every turn
        for i in range(len(config_with_goals)):
            adjacency_list[i] = get_token_adjacency(config_with_goals[i][1], config_with_goals)

        # within the same turn each token begins its action
        while (current_iterator < num_of_tokens):
            my_token = config_with_goals[current_iterator]
            current_adjacent_tokens = adjacency_list[current_iterator]
            closest_goal = gen_closest_goal(my_token[1],my_token[2])

            # stack to store token's moving route
            move_hist = move_hist_array[current_iterator]
            cur_pos = my_token[1]

            # implement A* search recursively to update token's moving route stack to get the optimal path, and make the movement by following the path
            make_move_recursive(my_token, closest_goal, prev_pos[current_iterator], config_with_goals, blocks, opponent_tokens, current_adjacent_tokens, move_hist, move_hist_array)
            next_pos = my_token[1]

            # print token's action result
            if calculate_distance(cur_pos,next_pos) == 1.0:
                print_slide(turn,cur_pos[0],cur_pos[1],next_pos[0],next_pos[1])
            else:
                print_swing(turn,cur_pos[0],cur_pos[1],next_pos[0],next_pos[1])

            # update token's goal list if current goal is eliminated
            for goal in my_token[2]:
                if my_token[1] == goal:
                    #print("eliminated goal", goal)
                    update_opponent_tokens(goal, opponent_tokens)
                    synchronize_goal(config_with_goals, goal, move_hist_array)
                    #print("Synchronizing complete")
            prev_pos[current_iterator] = cur_pos
            current_iterator += 1

        # at the end of each turn, resolve battles between tokens in the same hex
        token_battle(config_with_goals)
        # update token's moving status
        reset_movement_status(config_with_goals)
        print("")

    if turn <= 360:
        print("# Search complete! Number of actions:", turn)
    else:
        print("# Search complete! Declare a draw!")
