"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part B: Playing the Game
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)

This module contain functions of our searching strategy to make decisions for player's next action based on evaluation function.
"""

import math
from copy import deepcopy

from admin.pathfinding import *

INITIAL_WEIGHT = 5

def eval_board(my_token_array, opponent_token_array, enemy_throws_left, my_throw_range, op_throw_range, num_of_my_defeated_throws, enemies_defeated, player_faction, my_throws_left):
    '''
    Evaluate the board based on our evaluation function.
    '''
    sum_score = 0 
    if player_faction == "upper":
        allowed_r_coord = [i for i in range(4 - my_throw_range, 5)]
        allowed_r_coord_opp = [i for i in range(-4 , -3 + op_throw_range)]
    else:
        allowed_r_coord = [i for i in range(-4 , -3 + my_throw_range)]
        allowed_r_coord_opp = [i for i in range(4 - op_throw_range, 5)]
    allowed_q_coordinate = [i for i in range(-4 , 5)]


    overlap_adjust_coef = 1
    for i in range(len(my_token_array)):
        for j in range(len(my_token_array)):
            if i != j:
                if (my_token_array[i][1] == my_token_array[j][1]) and (my_token_array[i][0] == my_token_array[j][0]):
                    overlap_adjust_coef = overlap_adjust_coef/10

    raw_coordinates = []
    raw_coordinates_opp = []
    for r in allowed_r_coord:
        for q in allowed_q_coordinate:
            raw_coordinates.append((r,q))
    for r in allowed_r_coord_opp:
        for q in allowed_q_coordinate:
            raw_coordinates_opp.append((r,q))
    allowed_coordinates = raw_coordinates.copy()
    allowed_coordinates_opp = raw_coordinates_opp.copy()
    for coordinate in raw_coordinates:
        if not boarder_check(coordinate):
            allowed_coordinates.remove(coordinate)
    for coordinate in raw_coordinates_opp:
        if not boarder_check(coordinate):
            allowed_coordinates_opp.remove(coordinate)


    exposed_to_throw = 1
    for my_token in my_token_array:
        exposed_to_enemy_num = 0.5
        weight_coef = INITIAL_WEIGHT
        if my_token[2]:
            closest_goal = gen_closest_goal(my_token[1], my_token[2])
            closest_dist_goal = calculate_distance(my_token[1], closest_goal)
            if closest_dist_goal == 1.0:
                weight_coef *= 5
            weight_coef -= 1
        else:
            closest_dist_goal = 0
            weight_coef += 1

        if my_token[3]:
            closest_threat = gen_closest_goal(my_token[1], my_token[3])
            closest_dist_threat = calculate_distance(my_token[1], closest_threat)
            for threat in my_token[3]:
                if calculate_distance(my_token[1], threat) == 1:
                    exposed_to_enemy_num += 1
            weight_coef -= 1
        else:
            closest_dist_threat = 1000
        
        if player_faction == "upper":
            if ((my_token[1][0] - max(allowed_r_coord_opp)) < closest_dist_threat) and ((my_token[1][0] - max(allowed_r_coord_opp)) > 0):
                closest_dist_threat = my_token[1][0] - max(allowed_r_coord_opp)
                if closest_dist_threat == 1.0:
                    weight_coef /= 10
            elif (my_token[1][0] - max(allowed_r_coord_opp)) <= 0 :
                exposed_to_throw += 1
                exposed_to_enemy_num += 0.5
                closest_dist_threat = 0.1
        else:
            if (-(my_token[1][0] - min(allowed_r_coord_opp)) < closest_dist_threat) and (-(my_token[1][0] - min(allowed_r_coord_opp)) > 0):
                closest_dist_threat = -(my_token[1][0] - min(allowed_r_coord_opp))
                if closest_dist_threat == 1.0:
                    weight_coef /= 10
            elif (-(my_token[1][0] - min(allowed_r_coord_opp))) <= 0 :
                exposed_to_throw += 1
                exposed_to_enemy_num += 0.5
                closest_dist_threat = 0.1

        cover = 0
        for friendly in my_token_array:
            if friendly[0] == protective_type(my_token[0]):
                adjancent_tokens = get_token_adjacency(friendly[1],my_token_array)
                potential_movements = gen_next_all_potential_moves(friendly[1])
                truly_adjacent = adjancent_tokens.copy()
                if len(adjancent_tokens) != 0:
                    for adjacent_pos in adjancent_tokens:
                        if calculate_distance(friendly[1], adjacent_pos) != 1.0:
                            truly_adjacent.remove(adjacent_pos)
                if len(truly_adjacent) != 0:    
                    potential_swing_moves = gen_all_potential_swing_moves(friendly[1], truly_adjacent)
                    in_swing = set(potential_swing_moves)
                    in_move = set(potential_movements)
                    in_swing_but_not_in_move = in_swing - in_move
                    potential_movements = potential_movements + list(in_swing_but_not_in_move)
                    for move in potential_movements:
                        if move == my_token[1]:
                            cover = 1
        weight_coef += cover

        enemy_covered = 0
        if my_token[2]:
            for enemy in opponent_token_array:
                if enemy[1] == closest_goal:
                    target_info = enemy
                    break
            for enemy in opponent_token_array:
                if enemy[0] == protective_type(target_info[0]):
                    adjancent_tokens = get_token_adjacency(enemy[1],opponent_token_array)
                    potential_movements = gen_next_all_potential_moves(enemy[1])
                    truly_adjacent = adjancent_tokens.copy()
                    if len(adjancent_tokens) != 0:
                        for adjacent_pos in adjancent_tokens:
                            if calculate_distance(enemy[1], adjacent_pos) != 1.0:
                                truly_adjacent.remove(adjacent_pos)
                    if len(truly_adjacent) != 0:    
                        potential_swing_moves = gen_all_potential_swing_moves(enemy[1], truly_adjacent)
                        in_swing = set(potential_swing_moves)
                        in_move = set(potential_movements)
                        in_swing_but_not_in_move = in_swing - in_move
                        potential_movements = potential_movements + list(in_swing_but_not_in_move)
                        for move in potential_movements:
                            if move == target_info[1]:
                                enemy_covered = -1

        weight_coef += enemy_covered

        covering_friendly = 0

        adjancent_tokens = get_token_adjacency(my_token[1],my_token_array)
        potential_movements = gen_next_all_potential_moves(my_token[1])
        truly_adjacent = adjancent_tokens.copy()
        if len(adjancent_tokens) != 0:
            for adjacent_pos in adjancent_tokens:
                if calculate_distance(my_token[1], adjacent_pos) != 1.0:
                    truly_adjacent.remove(adjacent_pos)
        if len(truly_adjacent) != 0:    
            potential_swing_moves = gen_all_potential_swing_moves(my_token[1], truly_adjacent)
            in_swing = set(potential_swing_moves)
            in_move = set(potential_movements)
            in_swing_but_not_in_move = in_swing - in_move
            potential_movements = potential_movements + list(in_swing_but_not_in_move)
        for friendly in my_token_array:
            if friendly[1] in potential_movements:
                if friendly[0] == protective_type(my_token[0]):
                    covering_friendly = +1

        weight_coef += covering_friendly

        if (my_token[1] in allowed_coordinates_opp) and (enemy_throws_left > 0) :
            weight_coef -= 1
        else:
            weight_coef += 1

        sum_score = sum_score + weight_coef * ((((enemy_throws_left + len(opponent_token_array) + 1)/(enemy_throws_left + 1)) / exposed_to_throw) * closest_dist_threat / (exposed_to_enemy_num * 2) - closest_dist_goal * exposed_to_enemy_num)
        
    penal_coef = 1
    my_token_type = []
    op_token_type = []
    for my_token in my_token_array:
        my_token_type.append(my_token[0])
    for opponent_token in opponent_token_array:
        op_token_type.append(opponent_token[0])
    for opponent_token in opponent_token_array:
        if counter_type(opponent_token[0]) not in my_token_type:
            penal_coef = penal_coef/4
    
    winning_coef = 1

    if ("s" in my_token_type) and ("p" not in op_token_type):
        winning_coef += 1
    if ("p" in my_token_type) and ("s" not in op_token_type):
        winning_coef += 1
    if ("r" in my_token_type) and ("p" not in op_token_type):
        winning_coef += 1

    num_of_s = 0
    num_of_p = 0
    num_of_r = 0
    for types in my_token_type:
        if types == "s":
            num_of_s += 1
        elif types == "p":
            num_of_p += 1
        elif types == "r":
            num_of_r += 1

    if num_of_s > 1:
        winning_coef /= num_of_s
    if num_of_p > 1:
        winning_coef /= num_of_p
    if num_of_r > 1:
        winning_coef /= num_of_r

    if enemy_throws_left < my_throws_left:
        winning_coef *= (my_throws_left - enemy_throws_left + 1)
    elif enemy_throws_left > my_throws_left:   
        winning_coef /= (enemy_throws_left - my_throws_left + 1)

    sum_score =  sum_score - enemies_defeated + num_of_my_defeated_throws - my_throws_left
    sum_score = sum_score * overlap_adjust_coef * penal_coef * winning_coef
    return sum_score

def if_score(player_action, opponent_action, my_token_array, opponent_token_array, enemy_throws_left, my_throw_range, op_throw_range, num_of_my_defeated_throws, enemies_defeated, player_faction, my_throws_left):
    penal_coef = 1
    enemy_throws_left_if = enemy_throws_left
    my_throws_left_if = my_throws_left
    token_types =[]
    my_throw_range_if = my_throw_range
    op_throw_range_if = op_throw_range
    for token in my_token_array:
        token_types.append(token[0])
    if player_action == None:
        return 0

    if player_action[0] == "THROW":
        if enemy_throws_left_if == 0:
            penal_coef *= 2
        else:
            penal_coef =  penal_coef/8
        if (len(my_token_array) > 3) and (player_action[1] in token_types):
            penal_coef /= 100
    else:
        if player_action[1] == player_action[2]:
            penal_coef = 0
    my_token_array_if = deepcopy(my_token_array)
    opponent_token_array_if = deepcopy(opponent_token_array)
    
    num_of_my_defeated_throws_if = num_of_my_defeated_throws
    enemies_defeated_if = enemies_defeated
    
    if player_action[0] == "THROW":
        my_throw_range_if += 1
        my_throws_left_if -= 1
        my_token_array_if.append([player_action[1], (player_action[2][0],player_action[2][1]),[],[]])
    else:
        for position in my_token_array_if:
            if position[1] == player_action[1]:
                position[1] = player_action[2]
    if opponent_action:
        if opponent_action[0] == "THROW":
            op_throw_range_if += 1
            enemy_throws_left_if -= 1
            opponent_token_array_if.append([opponent_action[1],(opponent_action[2][0],opponent_action[2][1]),[],[]]) # a list ['token_type',(r,q),[list_of_goal_pos],[list_of_threat_pos]]
        else:
            for position in opponent_token_array_if:
                if position[1] == opponent_action[1]:
                    position[1] = opponent_action[2]

    # Check for s-p-r dies together situation
    my_token_array_if_copy = my_token_array_if.copy()
    opponent_token_array_if_copy = opponent_token_array_if.copy()
    for i in range(len(my_token_array_if_copy)):
        for j in range(len(opponent_token_array_if_copy)):
            for k in range(len(my_token_array_if_copy)):
                if i != k:
                    if my_token_array_if_copy[i][1] == my_token_array_if_copy[k][1] == opponent_token_array_if_copy[j][1]:
                        if (my_token_array_if_copy[i][0] != opponent_token_array_if_copy[j][0]) and (my_token_array_if_copy[k][0] != opponent_token_array_if_copy[j][0]) and (my_token_array_if_copy[i][0] != my_token_array_if_copy[k][0]):
                            if my_token_array_if_copy[i] in my_token_array_if:
                                num_of_my_defeated_throws_if += 1
                                my_token_array_if.remove(my_token_array_if_copy[i])
                            if my_token_array_if_copy[k] in my_token_array_if:
                                num_of_my_defeated_throws_if += 1
                                my_token_array_if.remove(my_token_array_if_copy[k])
                            if opponent_token_array_if_copy[j] in opponent_token_array_if:
                                enemies_defeated_if += 1
                                opponent_token_array_if.remove(opponent_token_array_if_copy[j])

    my_token_array_if_copy = my_token_array_if.copy()
    opponent_token_array_if_copy = opponent_token_array_if.copy()
    for i in range(len(opponent_token_array_if_copy)):
        for j in range(len(my_token_array_if_copy)):
            for k in range(len(opponent_token_array_if_copy)):
                if i != k:
                    if opponent_token_array_if_copy[i][1] == opponent_token_array_if_copy[k][1] == my_token_array_if_copy[j][1]:
                        if (opponent_token_array_if_copy[i][0] != my_token_array_if_copy[j][0]) and (opponent_token_array_if_copy[k][0] != my_token_array_if_copy[j][0]) and (opponent_token_array_if_copy[i][0] != opponent_token_array_if_copy[k][0]):
                            if opponent_token_array_if_copy[i] in opponent_token_array_if:
                                enemies_defeated_if += 1
                                opponent_token_array_if.remove(opponent_token_array_if_copy[i])
                            if opponent_token_array_if_copy[k] in opponent_token_array_if:
                                enemies_defeated_if += 1
                                opponent_token_array_if.remove(opponent_token_array_if_copy[k])
                            if my_token_array_if_copy[j] in my_token_array_if:
                                num_of_my_defeated_throws_if += 1
                                my_token_array_if.remove(my_token_array_if_copy[j])

    my_token_array_if_copy = my_token_array_if.copy()
    opponent_token_array_if_copy = opponent_token_array_if.copy()

    for my_token in my_token_array_if_copy:
        my_token_type = my_token[0]
        my_token_pos = my_token[1]
        for enemy_token in opponent_token_array_if_copy:
            enemy_token_type = enemy_token[0]
            enemy_token_pos = enemy_token[1]
            if my_token_pos == enemy_token_pos:
                if (enemy_token_type == "r") and (my_token_type == "s"):
                    if my_token in my_token_array_if:
                        my_token_array_if.remove(my_token)
                    penal_coef =  penal_coef/3
                    num_of_my_defeated_throws_if += 1
                    break
                elif (enemy_token_type == "s") and (my_token_type == "p"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if my_token in my_token_array_if:
                        my_token_array_if.remove(my_token)
                    break
                elif (enemy_token_type == "p") and (my_token_type == "r"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if my_token in my_token_array_if:
                        my_token_array_if.remove(my_token)
                    break
                elif (enemy_token_type ==  "s") and (my_token_type == "r"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 5
                    if enemy_token in opponent_token_array_if:
                        opponent_token_array_if.remove(enemy_token)
                    break
                elif (enemy_token_type ==  "p") and (my_token_type == "s"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 5
                    if enemy_token in opponent_token_array_if:
                        opponent_token_array_if.remove(enemy_token)
                    break
                elif (enemy_token_type ==  "r") and (my_token_type == "p"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 5
                    if enemy_token in opponent_token_array_if:
                        opponent_token_array_if.remove(enemy_token)
                    break

    my_token_array_if_copy = my_token_array_if.copy()

    for token_1 in my_token_array_if_copy:
        token_1_type = token_1[0]
        token_1_pos = token_1[1]
        for token_2 in my_token_array_if_copy:
            token_2_type = token_2[0]
            token_2_pos = token_2[1]
            if token_1_pos == token_2_pos:
                if (token_1_type == "r") and (token_2_type == "s"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if token_2 in my_token_array_if:
                        my_token_array_if.remove(token_2)
                    break
                elif (token_1_type == "s") and (token_2_type == "p"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if token_2 in my_token_array_if:
                        my_token_array_if.remove(token_2)
                    break
                elif (token_1_type == "p") and (token_2_type == "r"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if token_2 in my_token_array_if:
                        my_token_array_if.remove(token_2)
                    break
                elif (token_1_type ==  "s") and (token_2_type == "r"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if token_1 in my_token_array_if:
                        my_token_array_if.remove(token_1)
                    break
                elif (token_1_type ==  "p") and (token_2_type == "s"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if token_1 in my_token_array_if:
                        my_token_array_if.remove(token_1)
                    break
                elif (token_1_type ==  "r") and (token_2_type == "p"):
                    num_of_my_defeated_throws_if += 1
                    penal_coef =  penal_coef/3
                    if token_1 in my_token_array_if:
                        my_token_array_if.remove(token_1)
                    break
    
    # Check for enemy's overlapping pawns and remove them by rules (if any)
    opponent_token_array_if_copy = opponent_token_array_if.copy()   
    
    for token_1 in opponent_token_array_if_copy:
        token_1_type = token_1[0]
        token_1_pos = token_1[1]
        for token_2 in opponent_token_array_if_copy:
            token_2_type = token_2[0]
            token_2_pos = token_2[1]
            if token_1_pos == token_2_pos:
                if (token_1_type == "r") and (token_2_type == "s"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 4
                    if token_2 in opponent_token_array_if:
                        opponent_token_array_if.remove(token_2)
                    break
                elif (token_1_type == "s") and (token_2_type == "p"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 4
                    if token_2 in opponent_token_array_if:
                        opponent_token_array_if.remove(token_2)
                    break
                elif (token_1_type == "p") and (token_2_type == "r"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 4
                    if token_2 in opponent_token_array_if:
                        opponent_token_array_if.remove(token_2)
                    break
                elif (token_1_type ==  "s") and (token_2_type == "r"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 4
                    if token_1 in opponent_token_array_if:
                        opponent_token_array_if.remove(token_1)
                    break
                elif (token_1_type ==  "p") and (token_2_type == "s"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 4
                    if token_1 in opponent_token_array_if:
                        opponent_token_array_if.remove(token_1)
                    break
                elif (token_1_type ==  "r") and (token_2_type == "p"):
                    enemies_defeated_if += 1
                    penal_coef =  penal_coef * 4
                    if token_1 in opponent_token_array_if:
                        opponent_token_array_if.remove(token_1)
                    break

    # Update friendly token's goal and threat
    for token in my_token_array_if:
        token[2] = []
        token[3] = []
        my_token_type = token[0]
        for target in opponent_token_array_if:
            enemy_token_type = target[0]
            enemy_token_pos = target[1]
            if (enemy_token_type ==  "s") and (my_token_type == "r"):
                token[2].append(enemy_token_pos)
            elif (enemy_token_type ==  "p") and (my_token_type == "s"):
                token[2].append(enemy_token_pos)
            elif (enemy_token_type ==  "r") and (my_token_type == "p"):
                token[2].append(enemy_token_pos)
            if (enemy_token_type == "r") and (my_token_type == "s"):
                token[3].append(enemy_token_pos)
            elif (enemy_token_type == "s") and (my_token_type == "p"):
                token[3].append(enemy_token_pos)
            elif (enemy_token_type == "p") and (my_token_type == "r"):
                token[3].append(enemy_token_pos)

        # Update enemy token's goal and threat 
    for token in opponent_token_array_if:
        token[2] = []
        token[3] = []
        my_token_type = token[0]
        for target in my_token_array_if:
            enemy_token_type = target[0]
            enemy_token_pos = target[1]
            if (enemy_token_type ==  "s") and (my_token_type == "r"):
                token[2].append(enemy_token_pos)
            elif (enemy_token_type ==  "p") and (my_token_type == "s"):
                token[2].append(enemy_token_pos)
            elif (enemy_token_type ==  "r") and (my_token_type == "p"):
                token[2].append(enemy_token_pos)
            if (enemy_token_type == "r") and (my_token_type == "s"):
                token[3].append(enemy_token_pos)
            elif (enemy_token_type == "s") and (my_token_type == "p"):
                token[3].append(enemy_token_pos)
            elif (enemy_token_type == "p") and (my_token_type == "r"):
                token[3].append(enemy_token_pos)
    
    return eval_board(my_token_array_if, opponent_token_array_if, enemy_throws_left_if, my_throw_range_if, op_throw_range_if, num_of_my_defeated_throws_if, enemies_defeated_if, player_faction, my_throws_left_if) * penal_coef

def filter_action_list(best_actions):
    if not best_actions:
        return
    for action in best_actions:
        if action:
            if action[1] == action[2]:
                best_actions.remove(action)
    best_actions_filtered = []
    [best_actions_filtered.append(x) for x in best_actions if x not in best_actions_filtered]
    return best_actions_filtered

def gen_my_potential_actions(my_token_array,opponent_token_array,throw_range, my_throws_left,player_faction):
    num_of_tokens = len(my_token_array)
    current_iterator = 0

    adjacency_list =[[] for i in range(num_of_tokens)]
    for i in range(num_of_tokens):
        adjacency_list[i] = get_token_adjacency(my_token_array[i][1], my_token_array)

    best_actions = []
    throw_opt = throw_action(throw_range, player_faction, my_throws_left, opponent_token_array, my_token_array)
    if isinstance(throw_opt, tuple):
        best_actions.append(("THROW", throw_opt[0], throw_opt[1]))
    elif throw_opt == False:
        pass
    else:
        #print("**DEBUG:", throw_opt)
        for throw in throw_opt:
            if throw:
                for single_throw in throw:
                    best_actions.append(("THROW", single_throw[0], single_throw[1]))
    while (current_iterator < num_of_tokens):
        my_token = my_token_array[current_iterator]
        current_adjacent_tokens = adjacency_list[current_iterator]
        closest_goal =  gen_closest_goal(my_token[1],my_token[2])
        cur_pos = my_token[1]        
        route = offense_route_opt(my_token, closest_goal, cur_pos, my_token_array, opponent_token_array, current_adjacent_tokens)
        if route:
            temp = route.copy()
            for step in temp:
                threat_list = my_token[3]
                for threat in threat_list:
                    if calculate_distance(step, threat) == 1.0:
                        route = []
        if route:
            best_actions.append(("Move", cur_pos ,route[1]))
        if (len(my_token[3]) != 0):
            closest_threat = gen_closest_goal(my_token[1], my_token[3])
            closest_threat_dist = calculate_distance(my_token[1], closest_threat)
            if (closest_threat_dist == 1) and (len(my_token[2]) != 0):
                #print("**DEBUG evasive_attack", evasive_attack(my_token, opponent_token_array, current_adjacent_tokens, my_token_array))
                best_actions.append(evasive_attack(my_token, opponent_token_array, current_adjacent_tokens, my_token_array))
            else:
                if defense_opt(my_token, opponent_token_array, current_adjacent_tokens, my_token_array):
                    best_actions.append(("Move", cur_pos, defense_opt(my_token, opponent_token_array, current_adjacent_tokens, my_token_array)))
        current_iterator += 1
    best_actions_filtered = filter_action_list(best_actions)
    return best_actions_filtered

def gen_enemy_potential_actions(my_token_array, opponent_token_array, throw_range, opponent_throws_left, player_faction):

    potential_actions = []

    if player_faction == "upper":
        allowed_r_coord = [i for i in range(-4 , -3 + throw_range)]
    else:
        allowed_r_coord = [i for i in range(4 - throw_range, 5)]
        
    allowed_q_coordinate = [i for i in range(-4 , 5)]

    raw_coordinates = []
    for r in allowed_r_coord:
        for q in allowed_q_coordinate:
            raw_coordinates.append((r,q))
    allowed_coordinates = raw_coordinates.copy()
    for coordinate in raw_coordinates:
        if not boarder_check(coordinate):
            allowed_coordinates.remove(coordinate)
    """
    for enemy in opponent_token_array:
        if enemy[1] in allowed_coordinates:
            allowed_coordinates.remove(enemy[1])
    """
    if opponent_throws_left > 0:
        throw_type_list = ["r", "s","p"]
        for type_throw in throw_type_list:
            for coordinate in allowed_coordinates:
                potential_actions.append(("THROW", type_throw, coordinate))
    
    for enemy in opponent_token_array:
        explored_pos_lst = [enemy[1]]
        adjacency_list = get_token_adjacency(enemy[1], opponent_token_array)
        possible_moves = gen_possible_moves(enemy[1], enemy[0], my_token_array, adjacency_list, opponent_token_array, explored_pos_lst)
        for move in possible_moves:
            potential_actions.append(("Move", enemy[1], move))
    return potential_actions

def solve_payoff(best_actions, opponent_actions, player_pos, opponent_pos, opponent_throws_left, my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player ,my_throws_left):
    '''
    Generate the payoff matrix (M*N) based on player's potential actions (M) and enemy's potential actions (N), the solving the payoff matrix based on our evaluation function.
    '''
    #print("**DEBUG PAYOFF: Best_actions:", best_actions)
    payoff = []
    payoff_list = []
    #if player == "upper":
        #print("**1.DEBUG PAYOFF:", player_pos)
    if best_actions == None:
        return
    for action in best_actions:
        #if player == "upper":
            #print("**2. Generating ifscore for action:", action)
            #print("**2. DEBUG PAYOFF:", player_pos)
        temp = []
        play_pos_if = player_pos.copy()
        opponent_pos_if = opponent_pos.copy()
        if opponent_actions:
            #print("**DEBUG1")
            for opponent_action in opponent_actions:
            
            #if player == "upper":
                #print("**3.1 DEBUG PAYOFF:", player_pos)
                score = if_score(action, opponent_action, play_pos_if, opponent_pos_if, opponent_throws_left, my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player, my_throws_left)
            #if player == "upper":
                #print("**3.2 DEBUG PAYOFF:", player_pos)
                temp = [score, action, opponent_action]
                payoff.append(temp)
        #if player == "upper":
            #print("**4. DEBUG PAYOFF:", player_pos)
        else:
            #print("**DEBUG2")
            score = if_score(action, None, play_pos_if, opponent_pos_if, opponent_throws_left, my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player, my_throws_left)
            temp = [score, action, None]
            payoff.append(temp)

        sorted_payoff = sorted(payoff,key=lambda t:t[0])
        payoff_list.append(sorted_payoff[0])
    #if player == "upper":
    #print("**DEBUG PAYOFF: payoff_list", payoff_list)
    #print("")
    return payoff_list

def make_decision(player_pos, opponent_pos, opponent_throws_left, my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player, my_throws_left):
    '''
    Generate our player's next action based on the solving payoff matrix.
    '''
    if opponent_pos:
        if (opponent_throws_left <= 0) and (my_throws_left > 0):
            action_candidate = offensive_throw(opponent_pos, player, my_throw_range)
            opponent_actions = None
            best_candidates = solve_payoff(action_candidate, opponent_actions, player_pos, opponent_pos, opponent_throws_left,  my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player ,my_throws_left)
            min_score = best_candidates[0][0]
            decision = best_candidates[0][1]
            for candidate in best_candidates:
                if candidate[0] < min_score:
                    min_score = candidate[0]
                    decision = candidate[1]
            return decision

        elif (opponent_throws_left <= 0) and (my_throws_left <= 0):
            if player_pos:
                action_candidate = []
                num_of_tokens = len(player_pos)
                current_iterator = 0
                adjacency_list =[[] for i in range(num_of_tokens)]
                for i in range(num_of_tokens):
                    adjacency_list[i] = get_token_adjacency(player_pos[i][1], player_pos)
                while (current_iterator < num_of_tokens):
                    my_token = player_pos[current_iterator]
                    current_adjacent_tokens = adjacency_list[current_iterator]
                    closest_goal =  gen_closest_goal(my_token[1],my_token[2])
                    cur_pos = my_token[1]        
                    route = offense_route_opt(my_token, closest_goal, cur_pos, player_pos, opponent_pos, current_adjacent_tokens)
                    current_iterator += 1
                    if route:
                        action_candidate.append(("Move", cur_pos ,route[1]))
                opponent_actions = None
                best_candidates = solve_payoff(action_candidate, opponent_actions, player_pos, opponent_pos, opponent_throws_left,  my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player ,my_throws_left)
                min_score = best_candidates[0][0]
                decision = best_candidates[0][1]
                for candidate in best_candidates:
                    if candidate[0] < min_score:
                        min_score = candidate[0]
                        decision = candidate[1]
                return decision

    if len(player_pos) == 0:
        throw_moves = throw_action(my_throw_range, player, my_throws_left, opponent_pos, player_pos)
        if isinstance(throw_moves, tuple):
            return ("THROW", throw_moves[0], throw_moves[1])
        elif throw_moves == False:
            action_candidate = gen_my_potential_actions(player_pos, opponent_pos, my_throw_range, my_throws_left, player)

        else:
            action_candidate = []
            for candidate in throw_moves:
                for x in candidate:
                    if x:
                        action_candidate.append(("THROW", x[0], x[1]))
            if not action_candidate:
                action_candidate = gen_my_potential_actions(player_pos, opponent_pos, my_throw_range, my_throws_left, player)

    else:
        action_candidate = gen_my_potential_actions(player_pos, opponent_pos, my_throw_range, my_throws_left, player)

    if player_pos:
        if opponent_pos:
            protective_move = covering_move(player_pos)
            protective_throw = covering_throw(player_pos, opponent_pos, player, my_throw_range, my_throws_left, op_throw_range, opponent_throws_left)
            if protective_move:
                for move in protective_move:
                    action_candidate.append(move)
            if protective_throw:
                for move in protective_throw:
                    action_candidate.append(move)
    
    opponent_actions = gen_enemy_potential_actions(player_pos, opponent_pos, op_throw_range, opponent_throws_left, player)
    best_candidates = solve_payoff(action_candidate, opponent_actions, player_pos, opponent_pos, opponent_throws_left,  my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player ,my_throws_left)
    if best_candidates:
        min_score = best_candidates[0][0]
        decision = best_candidates[0][1]
        for candidate in best_candidates:
            if candidate[0] < min_score:
                min_score = candidate[0]
                decision = candidate[1]
    else:
        if player == "upper":
            action_candidate = gen_enemy_potential_actions(opponent_pos, player_pos, my_throw_range, opponent_throws_left, "lower")
        elif player == "lower":
            action_candidate = gen_enemy_potential_actions(opponent_pos, player_pos, my_throw_range, opponent_throws_left, "upper")
        best_candidates = solve_payoff(action_candidate, opponent_actions, player_pos, opponent_pos, opponent_throws_left,  my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player ,my_throws_left)
        min_score = best_candidates[0][0]
        decision = best_candidates[0][1]
        for candidate in best_candidates:
            if candidate[0] < min_score:
                min_score = candidate[0]
                decision = candidate[1]
    if (len(player_pos) <= 3) and (my_throws_left == 0):
        action_candidate_2 = []
        num_r = 0
        num_s = 0
        num_p = 0
        e_num_r = 0
        e_num_p = 0
        e_num_s = 0
        for friendly in player_pos:
            if friendly[0] == "r":
                num_r += 1
            if friendly[0] == "s":
                num_s += 1 
            if friendly[0] == "p":
                num_p += 1
        for opp in opponent_pos:
            if opp[0] == "r":
                e_num_r += 1
            if opp[0] == "s":
                e_num_s += 1 
            if opp[0] == "p":
                e_num_p += 1
        if  e_num_s != 0:
            if  num_r != 0:
                for friendly in player_pos:
                    if friendly[0] == "r":
                        if friendly[3]:
                            closest_threat = gen_closest_goal(friendly[1], friendly[3])
                            if calculate_distance(friendly[1], closest_threat) == 1:
                                adjacency_list = get_token_adjacency(friendly[1], player_pos)
                                if friendly[2]:
                                    action_candidate_2.append(evasive_attack(friendly, opponent_pos, adjacency_list, player_pos)) 
                                else:
                                    if defense_opt(friendly, opponent_pos, adjacency_list, player_pos):
                                        action_candidate_2.append(defense_opt(friendly, opponent_pos,adjacency_list, player_pos))
        if  e_num_r != 0:
            if  num_p != 0:
                for friendly in player_pos:
                    if friendly[0] == "p":
                        if friendly[3]:
                            closest_threat = gen_closest_goal(friendly[1], friendly[3])
                            if calculate_distance(friendly[1], closest_threat) == 1:
                                adjacency_list = get_token_adjacency(friendly[1], player_pos)
                                if friendly[2]:
                                    action_candidate_2.append(evasive_attack(friendly, opponent_pos, adjacency_list, player_pos)) 
                                else:
                                    if defense_opt(friendly, opponent_pos, adjacency_list, player_pos):
                                        action_candidate_2.append(defense_opt(friendly, opponent_pos,adjacency_list, player_pos))
        if  e_num_p != 0:
            if  num_s != 0:
                for friendly in player_pos:
                    if friendly[0] == "s":
                        if friendly[3]:
                            closest_threat = gen_closest_goal(friendly[1], friendly[3])
                            if calculate_distance(friendly[1], closest_threat) == 1:
                                adjacency_list = get_token_adjacency(friendly[1], player_pos)
                                if friendly[2]:
                                    action_candidate_2.append(evasive_attack(friendly, opponent_pos, adjacency_list, player_pos)) 
                                else:
                                    if defense_opt(friendly, opponent_pos, adjacency_list, player_pos):
                                        action_candidate_2.append(defense_opt(friendly, opponent_pos,adjacency_list, player_pos))
        if len(action_candidate_2) != 0:
            best_candidates = solve_payoff(action_candidate_2, opponent_actions, player_pos, opponent_pos, opponent_throws_left, my_throw_range, op_throw_range, my_defeated_token_num, enemies_defeated, player ,my_throws_left)
            min_score = best_candidates[0][0]
            decision = best_candidates[0][1]
            for candidate in best_candidates:
                if candidate[0] < min_score:
                    min_score = candidate[0]
                    decision = candidate[1]
    return decision
