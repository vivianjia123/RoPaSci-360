"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part B: Playing the Game
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)

This module contain functions to defines core game structure and actions.
"""

import math
import random

def boarder_check(position):
    if (position[0] < -4) or (position[0] > 4):
        return False
    if position[0] == 4:
        if not(-4 <= position[1] <= 0):
            return False
    elif position[0] == 3:
        if not(-4 <= position[1] <= 1):
            return False
    elif position[0] == 2:
        if not(-4 <= position[1] <= 2):
            return False
    elif position[0] == 1:
        if not(-4 <= position[1] <= 3):
            return False
    elif position[0] == 0:
        if not(-4 <= position[1] <= 4):
            return False
    elif position[0] == -1:
        if not(-3 <= position[1] <= 4):
            return False
    elif position[0] == -2:
        if not(-2 <= position[1] <= 4):
            return False
    elif position[0] == -3:
        if not(-1 <= position[1] <= 4):
            return False
    elif position[0] == -4:
        if not(0 <= position[1] <= 4):
            return False
    return True

def vertical_movement(token_position, direction):
    if direction == "up":
        return (token_position[0]+1,token_position[1])
    elif direction == "down":
        return (token_position[0]-1,token_position[1])

def horizontal_movement(token_position, direction):
    if direction == "left":
        return (token_position[0],token_position[1]-1)
    elif direction == "right":
        return (token_position[0],token_position[1]+1)

def diagonal_movement(token_position, direction):
    if direction == "up":
        return (token_position[0]+1,token_position[1]-1)
    elif direction == "down":
        return (token_position[0]-1,token_position[1]+1)

def calculate_distance(start, goal):
    distance = math.sqrt((start[0]-goal[0])**2+(start[1]-goal[1])**2+(start[0]-goal[0])*(start[1]-goal[1]))
    return distance

def gen_next_all_potential_moves(token_position):
    potential_movements = []
    potential_movements.append(vertical_movement(token_position, "up"))
    potential_movements.append(vertical_movement(token_position, "down"))
    potential_movements.append(horizontal_movement(token_position, "left"))
    potential_movements.append(horizontal_movement(token_position, "right"))
    potential_movements.append(diagonal_movement(token_position, "up"))
    potential_movements.append(diagonal_movement(token_position, "down"))
    potential_movements_in_range = potential_movements.copy()
    for move in potential_movements:
        if boarder_check(move) is False:
            potential_movements_in_range.remove(move)   
    return potential_movements_in_range

def get_token_adjacency(token_position, my_token_array):
    adjacent_token_pos_list = []
    for token in my_token_array:
        if calculate_distance(token_position, token[1]) == 1.0:
            adjacent_token_pos_list.append(token[1])
    return adjacent_token_pos_list

def check_hex_occupancy(destination_hex, my_token_list, my_token_array):
    temp = my_token_array.copy()
    temp.remove(my_token_list)
    for token in my_token_array:
        if token[1] == destination_hex:
            if token[0] == my_token_list[0]:
                pass
            return False
    return True

def gen_all_potential_swing_moves(token_position, adjacent_token_list):
    potential_swing_movements = []
    if len(adjacent_token_list) == 0:
        return potential_swing_movements
    for adjacent_token in adjacent_token_list:
        potential_swing_movements.extend(gen_next_all_potential_moves(adjacent_token))
    for move in potential_swing_movements:
        if move == token_position:
            potential_swing_movements.remove(move)
    return potential_swing_movements

def gen_sorted_dist_for_possible_moves(possible_move_list, goal):
    possible_move_list_with_dist = []
    for i in range(len(possible_move_list)):
        possible_move_list_with_dist.append([possible_move_list[i],calculate_distance(possible_move_list[i], goal)])
    sorted_lst = sorted(possible_move_list_with_dist,key=lambda x: x[1])
    pos_only_lst = []
    for move in sorted_lst:
        pos_only_lst.append(move[0])
    return pos_only_lst

def gen_closest_goal(token_position, goal_list):
    if not goal_list:
        return 
    closest = goal_list[0]
    closest_dist = calculate_distance(token_position, goal_list[0])
    for goal in goal_list:
        distance = calculate_distance(token_position, goal)
        if distance < closest_dist:
            closest = goal 
    return closest

def explore_next_point(destination, explored_pos_lst):
    if destination not in explored_pos_lst:
        explored_pos_lst.append(destination)

def pop_move_history_stack(move_history, branch_pos, origin):
    if len(move_history) == 0:
        pass
    else:
        if branch_pos != origin:
            while branch_pos in move_history: 
                if len(move_history) != 0:
                    move_history.pop()
                else:
                    break
            move_history.append(branch_pos)
        elif branch_pos == origin:
            while len(move_history) != 1:
                move_history.pop()

def gen_possible_moves(token_position, token_type, opponent_token_array, adjacent_token_list, my_token_array, explored_pos_lst, show_text=False):
    potential_movements = gen_next_all_potential_moves(token_position)
    truly_adjacent = adjacent_token_list.copy()
    if show_text == True:
        print("**Originally has move", potential_movements)
        print("**Iterating over adjacency list", truly_adjacent)
    if len(adjacent_token_list) != 0:
        for adjacent_pos in adjacent_token_list:
            if calculate_distance(token_position, adjacent_pos) != 1.0:
                truly_adjacent.remove(adjacent_pos)
    if len(truly_adjacent) != 0:    
        potential_swing_moves = gen_all_potential_swing_moves(token_position, truly_adjacent)
        in_swing = set(potential_swing_moves)
        in_move = set(potential_movements)
        in_swing_but_not_in_move = in_swing - in_move
        potential_movements = potential_movements + list(in_swing_but_not_in_move)
        if show_text == True:
            print("**Current potential moves", potential_movements)
        for move in potential_movements:
            if move in truly_adjacent:
                for my_token in my_token_array:
                    if (move == my_token[1]) and (move in potential_movements):
                        if show_text == True:
                            print("**2：Removed adjacent node for not possible overlapping", move)
                        potential_movements.remove(move)
    if show_text == True:
        print("**Here are all the potential moves:",potential_movements)
    filtered_move = potential_movements.copy()
    for move in potential_movements:
        if move in explored_pos_lst:
            filtered_move.remove(move)
        else:
            for my_token in my_token_array:
                if not check_hex_occupancy(move, my_token,my_token_array):
                    if show_text == True:
                        print("**Validated as false")
                        print("**3：Removed adjacent node for not possible overlapping", move)
                    filtered_move.remove(move)
                    if show_text == True:
                        print("** Now the filtered moves are", filtered_move)
                    break
                else:
                    if show_text == True:
                        print("**Validated as True")
    for token in opponent_token_array:
        for move in potential_movements:
            if (token[0] == 'r') and (token_type == 's'):
                if (token[1] == move) and (move in filtered_move):
                    filtered_move.remove(move)
            elif (token[0] == 's') and (token_type == 'p'):
                if (token[1] == move) and (move in filtered_move):
                    filtered_move.remove(move)
            elif (token[0] == 'p') and (token_type == 'r'):
                if (token[1] == move) and (move in filtered_move):
                    filtered_move.remove(move)
    if show_text == True:
        print("The final possible moves are",filtered_move)
    return filtered_move

def gen_move_failure(token_position,token_type, opponent_token_array, adjacent_token_list, my_token_array, explored_pos_lst):
    potential_movements = gen_next_all_potential_moves(token_position)
    truly_adjacent = adjacent_token_list.copy()
    if len(adjacent_token_list) != 0:
        for adjacent_pos in adjacent_token_list:
            if calculate_distance(token_position, adjacent_pos) != 1.0:
                truly_adjacent.remove(adjacent_pos)
    if len(truly_adjacent) != 0:    
        potential_swing_moves = gen_all_potential_swing_moves(token_position, truly_adjacent)
        in_swing = set(potential_swing_moves)
        in_move = set(potential_movements)
        in_swing_but_not_in_move = in_swing - in_move
        potential_movements = potential_movements + list(in_swing_but_not_in_move)
        for move in potential_movements:
            if move in truly_adjacent:
                for my_token in my_token_array:
                    if move == my_token[1] and my_token[3]==False:
                        potential_movements.remove(move)
    filtered_move = potential_movements.copy()
    for move in potential_movements:
        if move in explored_pos_lst:
            filtered_move.remove(move)
    for token in opponent_token_array:
        for move in potential_movements:
            if (token[0] == 'r') and (token_type == 's'):
                if (token[1] == move) and (move in filtered_move):
                    filtered_move.remove(move)
            elif (token[0] == 's') and (token_type == 'p'):
                if (token[1] == move) and (move in filtered_move):
                    filtered_move.remove(move)
            elif (token[0] == 'p') and (token_type == 'r'):
                if (token[1] == move) and (move in filtered_move):
                    filtered_move.remove(move)
    if not filtered_move:
        return False
    else:
        return filtered_move

def recursive_DFS_path_finding(token_position, goal, token_type, opponent_token_array, prev_position, adjacent_token_list, my_token_array,explored_pos_lst,hist_stack, path_found, origin):
    raw_possible_move_list = gen_possible_moves(token_position, token_type, opponent_token_array, adjacent_token_list, my_token_array, explored_pos_lst)
    possible_move_list = gen_sorted_dist_for_possible_moves(raw_possible_move_list, goal)
    if not possible_move_list:
        reserve_option = gen_move_failure(token_position, token_type, opponent_token_array, adjacent_token_list, my_token_array, explored_pos_lst)
        if reserve_option:
            raw_possible_move_list = reserve_option
            possible_move_list = gen_sorted_dist_for_possible_moves(raw_possible_move_list, goal)
        else:
            return
    #print("**Debugging: For position", token_position,"should have moves",possible_move_list) 
    for next_move in possible_move_list:
        if next_move not in explored_pos_lst:
            explore_next_point(next_move, explored_pos_lst)  
            if next_move == goal:
                hist_stack.append(goal)
                #print("**Reached goal")
                #print("**Explore history", hist_stack)
                for move in hist_stack:
                    path_found.append(move)
                return True
    for next_move_1 in possible_move_list:
        #print("**Debugging: This is the next move:", next_move_1,"from",possible_move_list) 
        hist_stack.append(next_move_1)
        prev_position = token_position
        #print("*Debugging-1:",hist_stack)
        recursive_DFS_path_finding(next_move_1, goal, token_type, opponent_token_array, prev_position, adjacent_token_list, my_token_array,explored_pos_lst,hist_stack, path_found, origin)
        pop_move_history_stack(hist_stack, prev_position, origin)
        #print("*Debugging-2:",hist_stack)

def offense_route_opt(my_token_list, goal, prev_pos, my_token_array, opponent_token_array, adjacent_token_list):
    explored_pos_lst = [my_token_list[1]]
    if not goal:
        return    
    temp = [my_token_list[1]]
    hist_stack = []
    recursive_DFS_path_finding(my_token_list[1], goal, my_token_list[0], opponent_token_array, prev_pos, adjacent_token_list, my_token_array ,explored_pos_lst, temp, hist_stack, my_token_list[1])
    return hist_stack

def check_destination_covered(destination, my_token_list, my_token_array):
    token_type = my_token_list[0]
    potential_cover_lst = []
    if token_type == "r":
        for my_token in my_token_array:
            if my_token[0] == "s":
                potential_cover_lst.append(my_token[1])
        for cover in potential_cover_lst:
            if calculate_distance(destination, cover) == 1:
                return True
    elif token_type == "s":
        for my_token in my_token_array:
            if my_token[0] == "p":
                potential_cover_lst.append(my_token[1])
        for cover in potential_cover_lst:
            if calculate_distance(destination, cover) == 1:
                return True
    elif token_type == "p":
        for my_token in my_token_array:
            if my_token[0] == "r":
                potential_cover_lst.append(my_token[1])
        for cover in potential_cover_lst:
            if calculate_distance(destination, cover) == 1:
                return True
    return False

def defense_opt(my_token_list, opponent_token_array, adjacent_token_list, my_token_array): # threat_list is the list of all threats while threat_token_list is the info of a single threat
    explored_pos_lst = explored_pos_lst = [my_token_list[1]]
    token_pos = my_token_list[1]
    token_type = my_token_list[0]
    threat_list = my_token_list[3]
    escape_opts = gen_possible_moves(token_pos, token_type, opponent_token_array, adjacent_token_list, my_token_array, explored_pos_lst, show_text=False)
    escape_opts.append(token_pos) #include staying still
    dist_from_escape_opt = [[]for i in range(len(escape_opts))]
    escape_opts_is_covered = [[]for i in range(len(escape_opts))]
    covered_move_lst = []
    covered_move_dist = []
    safest_move = escape_opts[-1]
    longest_move_cost = 0
    shortest_move_cost = 10000
    for escape_move in escape_opts:
        for threat in threat_list:
            for opponent in opponent_token_array:
                if threat == opponent[1]:
                    threat_token_list = opponent
                    break
            adjacency_list = get_token_adjacency(threat, opponent_token_array)
            offense_route = offense_route_opt(threat_token_list, escape_move, threat, opponent_token_array, my_token_array, adjacency_list)
            if (len(offense_route) < shortest_move_cost):
                shortest_move_cost = len(offense_route)
                dist_from_escape_opt[escape_opts.index(escape_move)] = len(offense_route)
        shortest_move_cost = 10000
    for escape_move in escape_opts:
        if check_destination_covered(escape_move, my_token_list, my_token_array):
            escape_opts_is_covered[escape_opts.index(escape_move)] = True
        else:
            escape_opts_is_covered[escape_opts.index(escape_move)] = False
    if not any (escape_opts_is_covered):
        if not run_for_cover(my_token_list, opponent_token_array, adjacent_token_list, my_token_array):
            best_escape_move = escape_opts[dist_from_escape_opt.index(max(dist_from_escape_opt))]
        else:
            potential_move = run_for_cover(my_token_list, opponent_token_array, adjacent_token_list, my_token_array)
            if (calculate_distance(potential_move, gen_closest_goal(potential_move, threat_list)) <  calculate_distance(token_pos, gen_closest_goal(token_pos, threat_list))) or (calculate_distance(potential_move, gen_closest_goal(potential_move, threat_list)) == 1):
                best_escape_move = escape_opts[dist_from_escape_opt.index(max(dist_from_escape_opt))]
            else:
                best_escape_move = run_for_cover(my_token_list, opponent_token_array, adjacent_token_list, my_token_array)
    else:
        for move in escape_opts:
            if escape_opts_is_covered[escape_opts.index(move)] == True:
                covered_move_lst.append(move)
                covered_move_dist.append(dist_from_escape_opt[escape_opts.index(move)])
        best_escape_move = covered_move_lst[covered_move_dist.index(max(covered_move_dist))]
            
    return best_escape_move

def run_for_cover(my_token_list, opponent_token_array, adjacent_token_list, my_token_array):
    token_type = my_token_list[0]
    token_position = my_token_list[1]
    potential_cover_lst = []
    dist_to_cover = []
    if token_type == "r":
        for my_token in my_token_array:
            if my_token[0] == "s":
                cover_type = my_token[0]
                potential_cover_lst.append(my_token[1])
    elif token_type == "s":
        for my_token in my_token_array:
            if my_token[0] == "p":
                cover_type = my_token[0]
                potential_cover_lst.append(my_token[1])
    elif token_type == "p":
        for my_token in my_token_array:
            if my_token[0] == "r":
                cover_type = my_token[0]
                potential_cover_lst.append(my_token[1])
    if not potential_cover_lst:
        return False
    else:
        for cover in potential_cover_lst:
            dist_to_cover.append(calculate_distance(token_position, cover))
        closest_cover = potential_cover_lst[dist_to_cover.index(min(dist_to_cover))]
        potential_contacts = gen_next_all_potential_moves(closest_cover)
        available_contacts = potential_contacts.copy()
        for contact in potential_contacts:
            for token in my_token_array:
                if token[1] == contact:
                    if token[0] == token_type:
                        pass
                    else:
                        if contact in available_contacts:
                            available_contacts.remove(contact)
            for token in opponent_token_array:
                if token[1] == contact:
                    if contact in available_contacts:
                        available_contacts.remove(contact)
        closest_contact_dist = 10000
        for contact in available_contacts:
            if calculate_distance(contact, token_position) < closest_contact_dist:
                closest_contact_dist = calculate_distance(contact, token_position)
                closest_contact_point = contact
        escape_route = offense_route_opt(my_token_list, closest_contact_point, token_position, opponent_token_array, my_token_array, adjacent_token_list)
        return escape_route[1]

def counter_type(token_type):
    if token_type == "r":
        return "p"
    elif token_type == "p":
        return "s"
    elif token_type == "s":
        return "r"

def protective_type(token_type):
    if token_type == "r":
        return "s"
    elif token_type == "p":
        return "r"
    elif token_type == "s":
        return "p"
    
def throw_action(throw_range, player, throws_left, opponent_token_array, my_token_array):
    '''
    Generate a list of player's throw actions.

    :param throw_range: a range of throw
    :param player: the current player
    :param throws_left: the number of throws the player left
    :param opponent_token_array: the opponent tokens list
    :param my_token_array: the player's tokens list
    :return: a list contain all throw options of the player
    '''
    if player == "upper":
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
    #print("allowed coordinates are", allowed_coordinates) 
    #print("**Allowed throw r range is:", allowed_r_coord)
    #print("**Allowed throw r coordinates are:", allowed_coordinates)
    if throws_left <= 0: # No throws left
        return False
    else:
        if (len(my_token_array) == 0) and (len(opponent_token_array) == 0): # No friendly or hostile tokens on board yet
            type_choice = ["r","s","p"]
            return (random.choice(type_choice), random.choice(allowed_coordinates))

        elif (len(my_token_array) != 0) and (len(opponent_token_array) != 0): # Exists some friendly and hostile tokens
            throw_choices = [[],[],[]]
            for enemy in opponent_token_array:
                counter_token_type= counter_type(enemy[0])
                if enemy[1] in allowed_coordinates:
                    throw_choices[0].append((counter_token_type, enemy[1])) # Add immediate kill throw option for consideration
                else:
                    potential_throw_contacts = gen_next_all_potential_moves(enemy[1])
                    available_throw_contacts = potential_throw_contacts.copy()
                    for throw_dest in potential_throw_contacts:
                        for token in my_token_array:
                            if token[1] == throw_dest:
                                if token[0] == counter_token_type:
                                    pass
                                else:
                                    available_throw_contacts.remove(throw_dest)
                        for token in opponent_token_array:
                            if token[1] == throw_dest:
                                if token[0] == counter_token_type:
                                    pass
                                elif (token[0] == counter_type(counter_token_type)) and (throw_dest in available_throw_contacts):
                                    available_throw_contacts.remove(throw_dest)
                    for throw_opt in available_throw_contacts:
                        if throw_opt in allowed_coordinates:
                            throw_choices[1].append((counter_token_type, throw_opt)) # Add kill in next round throw option for consideration

            num_of_s = 0 
            num_of_p = 0
            num_of_r = 0
        
            for friendly in my_token_array:
                if friendly[0] == "r":
                    num_of_r += 1
                elif friendly[0] == "s":
                    num_of_s += 1
                elif friendly[0] == "p":
                    num_of_p += 1
            type_choice = []
            if num_of_s < 1:
                type_choice.append("s")

            if num_of_p < 1:
                type_choice.append("p")

            if num_of_r < 1:
                type_choice.append("r")

            if type_choice: # Perform a protective throw if number of tokens < than 1p 1r 1s
                #print("** Protective throw")
                for choice in type_choice: 
                    for my_token in my_token_array:
                        if choice == protective_type(my_token[0]):
                            counter_token_type = choice
                            temp = gen_next_all_potential_moves(my_token[1])
                            thow_pos = temp.copy()
                            for throw in temp:
                                if not check_hex_occupancy(throw, my_token, my_token_array):
                                    thow_pos.remove(throw)
                            break
                #print("** Protective throw opt are:", thow_pos)
                for throw_opt in thow_pos:
                    if throw_opt in  allowed_coordinates:
                        throw_choices[2].append((counter_token_type, throw_opt))

        elif (len(my_token_array) == 0) and (len(opponent_token_array) != 0):
            throw_choices = [[],[],[]]
            for enemy in opponent_token_array:
                counter_token_type= counter_type(enemy[0])
                if enemy[1] in allowed_coordinates:
                    throw_choices[0].append((counter_token_type, enemy[1])) # Add immediate kill throw option for consideration
                else:
                    potential_throw_contacts = gen_next_all_potential_moves(enemy[1])
                    available_throw_contacts = potential_throw_contacts.copy()
                    for throw_dest in potential_throw_contacts:
                        for token in my_token_array:
                            if token[1] == throw_dest:
                                if token[0] == counter_token_type:
                                    pass
                                else:
                                    available_throw_contacts.remove(throw_dest)
                        for token in opponent_token_array:
                            if token[1] == throw_dest:
                                if token[0] == counter_token_type:
                                    pass
                                elif token[0] == counter_type(counter_token_type):
                                    available_throw_contacts.remove(throw_dest)
                    for throw_opt in available_throw_contacts:
                        if throw_opt in allowed_coordinates:
                            throw_choices[1].append((counter_token_type, throw_opt)) # Add kill in next round throw option for consideration

            if (not throw_choices[0]) and (not throw_choices[1]):
                type_choice = ["r","s","p"]
                return (random.choice(type_choice), random.choice(allowed_coordinates))
        #print("**Throw choices are:", throw_choices)
        return throw_choices

            
                
                
