"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part B: Playing the Game
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)

This module contain functions of our searching strategy to make decisions for player's next action based on evaluation function.
"""

import math

from admin.pathfinding import *

def gen_potential_actions(my_token_array, opponent_token_array, throw_range, my_throws_left, player_faction):

    potential_actions = []

    if player_faction == "upper":
        allowed_r_coord = [i for i in range(4 - throw_range, 5)]
    else:
        allowed_r_coord = [i for i in range(-4 , -3 + throw_range)]
        
    allowed_q_coordinate = [i for i in range(-4 , 5)]

    raw_coordinates = []
    for r in allowed_r_coord:
        for q in allowed_q_coordinate:
            raw_coordinates.append((r,q))
    allowed_coordinates = raw_coordinates.copy()
    for coordinate in raw_coordinates:
        if not boarder_check(coordinate):
            allowed_coordinates.remove(coordinate)

    for friendly in my_token_array:
        if friendly[1] in allowed_coordinates:
            allowed_coordinates.remove(friendly[1])

    if my_throws_left > 0:
        throw_type_list = ["r", "s","p"]
        for type_throw in throw_type_list:
            for coordinate in allowed_coordinates:
                potential_actions.append(("THROW", type_throw, coordinate))
    
    for friendly in my_token_array:
        explored_pos_lst = [friendly[1]]
        adjacency_list = get_token_adjacency(friendly[1], my_token_array)
        possible_moves = gen_possible_moves(friendly[1], friendly[0], opponent_token_array, adjacency_list, my_token_array, explored_pos_lst)
        for move in possible_moves:
            potential_actions.append(("Move", friendly[1], move))
    return potential_actions

def filter_action_list(potential_actions, my_token_array):
    filtered_action = []
    for move in potential_actions:
        if move[0] == "THROW":
            filtered_action.append(move)
        else:
            for token in my_token_array:
                if move[1] == token[1]:
                    filtered_action.append(move)
    return filtered_action
           
def make_decision(potential_actions):
    '''
    Randomly generate our player's next action.
    '''
    return random.choice(potential_actions)

