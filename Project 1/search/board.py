'''
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)

This module contain functions to defines core game structure, actions and searching algorithms
'''

import math


############################ BASIC ACTION #########################


def token_battle(my_token_array):
    '''
    Resolved the battle between tokens that occupy the same hex, remove the defeated token from the token list.

    :param my_token_array: the upper tokens list
    '''
    token_array_a = my_token_array.copy()
    token_array_b = my_token_array.copy()
    for a_token in token_array_a:
        for b_token in token_array_b:
            if a_token[1] == b_token[1] and a_token != b_token:
                if a_token[0] == 'r':
                    if b_token[0] == 'p':
                        if a_token in my_token_array:
                            my_token_array.remove(a_token)
                            break
                    elif b_token[0] == 's':
                        if b_token in my_token_array:
                            my_token_array.remove(b_token)
                            break
                elif a_token[0] == 'p':
                    if b_token[0] == 's':
                        if a_token in my_token_array:
                            my_token_array.remove(a_token)
                            break
                    elif b_token[0] == 'r':
                        if b_token in my_token_array:
                            my_token_array.remove(b_token)
                            break
                elif a_token[0] == 's':
                    if b_token[0] == 'r':
                        if a_token in my_token_array:
                            my_token_array.remove(a_token)
                            break
                    elif b_token[0] == 'p':
                        if b_token in my_token_array:
                            my_token_array.remove(b_token)
                            break
            else:
                pass


def gen_possible_moves(token_position,
                       token_type,
                       block_array,
                       opponent_token_array,
                       prev_position,
                       adjacent_token_list,
                       my_token_array,
                       explored_pos_lst,
                       show_text=False):
    '''
    Generate and return a list contains all possible moves of the current token based on the current board state and the game rule.

    :param token_position: the coordinate (r, q) of current token
    :param token_type: the type of token ('r', 's', or 'p')
    :param block_array: the list contains all blocks' coordinates
    :param opponent_token_array: the lower tokens list
    :param prev_position: the coordinate that current token comes from
    :param adjacent_token_list: the list contains all adjacent tokens
    :param my_token_array: the upper tokens list
    :param explored_pos_lst: the list contains all positions the current token have explored when searching the board
    :param show_text: a flag to indicate whether to display the text
    return: a list that contains all coordinates of possible moves after filtering out all the impossible moves according to the rules of the game
    '''
    # list to store all the potential moves of current token
    potential_movements = gen_next_all_potential_moves(token_position)
    # list to keep updating adjacent tokens of current token
    truly_adjacent = adjacent_token_list.copy()
    if show_text is True:
        print("**Originally has move", potential_movements)
        print("**Iterating over adjacency list", truly_adjacent)
    # if the token in original adjacent_token_list is no longer adjacent to the current token position, update the truly_adjacent list by remove the token from it
    if len(adjacent_token_list) != 0:
        for adjacent_pos in adjacent_token_list:
            if calculate_distance(token_position, adjacent_pos) != 1.0:
                truly_adjacent.remove(adjacent_pos)

    # check if the updated truly_adjacent list is empty
    if len(truly_adjacent) != 0:
        # if not, add all potential swing moves to the potential movement list.
        potential_swing_moves = gen_all_potential_swing_moves(
            token_position, truly_adjacent)
        in_swing = set(potential_swing_moves)
        in_move = set(potential_movements)
        in_swing_but_not_in_move = in_swing - in_move
        potential_movements = potential_movements + list(
            in_swing_but_not_in_move)
        if show_text is True:
            print("**Current potential moves", potential_movements)
        # check overlapping condition
        for move in potential_movements:
            if move in truly_adjacent:
                for my_token in my_token_array:
                    # if there is a token in adjacent move position after the token make movement, do nothing.
                    if move == my_token[1] and my_token[3] is True:
                        pass
                    # if there is a token in adjacent move position before the token make movement
                    elif move == my_token[1] and my_token[3] is False:
                        if show_text is True:
                            print(
                                "**2：Removed adjacent node for not possible overlapping",
                                move)
                        # remove the position from the potential movement list
                        potential_movements.remove(move)
    if show_text is True:
        print("**Here are all the potential moves:", potential_movements)
        print("**The previous position is", prev_position)

    # copy the potential movements list to a new list, use the new list to further filter potential moves according to the rules of the game
    filtered_move = potential_movements.copy()
    # 1. delete the potential move that has been explored by the current token already
    for move in potential_movements:
        if move in explored_pos_lst:
            filtered_move.remove(move)
        else:
            for my_token in my_token_array:
                # check if the position has been occupied by upper tokens and can not be overlapped
                if not check_hex_occupancy(move, my_token, my_token_array):
                    filtered_move.remove(move)
                    break
    # 2. delete the potential move that has been occupied by block
    for block in block_array:
        for move in potential_movements:
            if block == move:
                filtered_move.remove(move)
    # 3. delete the potential move that has been occupied by any lower token that current upper token can neither overlap nor eliminate
    for token in opponent_token_array:
        for move in potential_movements:
            if (token[0] == 'r') and (token_type == 's'):
                if token[1] == move:
                    filtered_move.remove(move)
            elif (token[0] == 's') and (token_type == 'p'):
                if token[1] == move:
                    filtered_move.remove(move)
            elif (token[0] == 'p') and (token_type == 'r'):
                if token[1] == move:
                    print("Debug move:",move)
                    filtered_move.remove(move)
    if show_text is True:
        print("The possible moves are", potential_movements)

    # Then the new filtered_move list contains all positions that current token is able to move within current turn based on the game rules.
    return filtered_move


def gen_move_failure(token_position, token_type, block_array,
                     opponent_token_array, prev_position, adjacent_token_list,
                     my_token_array, explored_pos_lst):
    '''
    This function has the same logic with "gen_possible_moves" function except the return value is a little bit different. Generate and return a list contains all possible moves of the current token based on the current board state and the game rule. If the list is empty, return False.

    :param token_position: the coordinate (r, q) of current token
    :param token_type: the type of token ('r', 's', or 'p')
    :param block_array: the list contains all blocks' coordinates
    :param opponent_token_array: the lower tokens list
    :param prev_position: the coordinate that current token comes from
    :param adjacent_token_list: the list contains all adjacent tokens
    :param my_token_array: the upper tokens list
    :param explored_pos_lst: the list contains all positions the current token have explored when searching the board
    :return: False if the list of all coordinates of possible moves after filtering out all the impossible moves according to the rules of the game is empty, otherwise return the list
    '''
    potential_movements = gen_next_all_potential_moves(token_position)
    truly_adjacent = adjacent_token_list.copy()
    if len(adjacent_token_list) != 0:
        for adjacent_pos in adjacent_token_list:
            if calculate_distance(token_position, adjacent_pos) != 1.0:
                truly_adjacent.remove(adjacent_pos)
    if len(truly_adjacent) != 0:
        potential_swing_moves = gen_all_potential_swing_moves(
            token_position, truly_adjacent)
        in_swing = set(potential_swing_moves)
        in_move = set(potential_movements)
        in_swing_but_not_in_move = in_swing - in_move
        potential_movements = potential_movements + list(
            in_swing_but_not_in_move)
        for move in potential_movements:
            if move in truly_adjacent:
                for my_token in my_token_array:
                    if move == my_token[1] and my_token[3] is True:
                        pass
                    elif move == my_token[1] and my_token[3] is False:
                        potential_movements.remove(move)
    filtered_move = potential_movements.copy()
    for move in potential_movements:
        if move in explored_pos_lst:
            filtered_move.remove(move)
    for block in block_array:
        for move in potential_movements:
            if block == move:
                filtered_move.remove(move)
    for token in opponent_token_array:
        for move in potential_movements:
            if (token[0] == 'r') and (token_type == 's'):
                if token[1] == move:
                    filtered_move.remove(move)
            elif (token[0] == 's') and (token_type == 'p'):
                if token[1] == move:
                    filtered_move.remove(move)
            elif (token[0] == 'p') and (token_type == 'r'):
                if token[1] == move:
                    filtered_move.remove(move)
    if not filtered_move:
        return False
    else:
        return filtered_move


########################## RECURSIVE DFS #########################


def recursive_DFS_path_finding(token_position, goal, token_type, block_array,
                               opponent_token_array, prev_position,
                               adjacent_token_list, my_token_array,
                               explored_pos_lst, hist_stack, path_found,
                               origin):
    '''
    Construct a recursive A* search in a DFS search manner to find the path towards the nearest goal from the token's current position.

    :param token_position: the coordinate (r, q) of current token
    :param goal: the coordinate (r, q) of closest goal
    :param token_type: the type of token ('r', 's', or 'p')
    :param block_array: the list contains all blocks' coordinates
    :param opponent_token_array: the lower tokens list
    :param prev_position: the coordinate that current token comes from
    :param adjacent_token_list: the list contains all adjacent tokens
    :param my_token_array: the upper tokens list
    :param explored_pos_lst: the list contains all positions the current token have explored when searching the board
    :param hist_stack: stack that contains token's moving route
    :param path_found: a list to store the result path
    :param origin: the original coordinate (r, q) of current token
    :return: True if , or return None if there is no possible moves for current token
    '''
    # Generate a list contains all coordinates of possible moves from the current token's position that is sorted by the closest distance.
    raw_possible_move_list = gen_possible_moves(
        token_position, token_type, block_array, opponent_token_array,
        prev_position, adjacent_token_list, my_token_array, explored_pos_lst)
    possible_move_list = gen_sorted_dist_for_possible_moves(
        raw_possible_move_list, goal)
    # If the list is empty, use reserve function "gen_move_failure" to generate the possible move list again.
    if not possible_move_list:
        reserve_option = gen_move_failure(token_position, token_type,
                                          block_array, opponent_token_array,
                                          prev_position, adjacent_token_list,
                                          my_token_array, explored_pos_lst)
        # If the reserved list is not empty, sort all coordinates in the list according to the distance to the target, and save it for the further path finding.
        if reserve_option:
            raw_possible_move_list = reserve_option
            possible_move_list = gen_sorted_dist_for_possible_moves(
                raw_possible_move_list, goal)
        # Otherwise, meaning there is no movement availiable for the current token, returns None.
        else:
            return
    #print("**Debugging: For position", token_position,"should have moves",possible_move_list)

    # To explore the sorted possible move, add each exploration move position to the explored_pos_lst and also the hist_stack.
    for next_move in possible_move_list:
        if next_move not in explored_pos_lst:
            explore_next_point(next_move, explored_pos_lst)
            # If the token can reach the goal at next exploration move, the search path is complete. Add goal hex to the token's hist_stack, store each historical position into the path_found list，then returns True.
            if next_move == goal:
                hist_stack.append(goal)
                for move in hist_stack:
                    path_found.append(move)
                return True
    # If the token can not reach the goal at next exploration move, assign current token position to the previous position, and then call the dfs search function for the next move position recursively until reach the goal. Pop the previous position from the hist_stack every recursive time.
    for next_move_1 in possible_move_list:
        #print("**Debugging: This is the next move:", next_move_1,"from",possible_move_list)
        hist_stack.append(next_move_1)
        prev_position = token_position
        #print("*Debugging-1:",hist_stack)
        recursive_DFS_path_finding(next_move_1, goal, token_type, block_array,
                                   opponent_token_array, prev_position,
                                   adjacent_token_list, my_token_array,
                                   explored_pos_lst, hist_stack, path_found,
                                   origin)
        pop_move_history_stack(hist_stack, prev_position, origin)
        #print("*Debugging-2:",hist_stack)


############################ MOVEMENT #############################


def make_move_recursive(my_token_list, goal, prev_pos, my_token_array,
                        block_array, opponent_token_array, adjacent_token_list,
                        last_hist_stack, move_hist_array):
    '''
    Update current token's moving route stack by applying DFS and make the optimal move for the token.

    :param my_token_list: the list of current token's information
    :param goal: the coordinate (r, q) of closest goal
    :param prev_pos: the coordinate that current token comes from
    :param my_token_array: the upper tokens list
    :param block_array: the list contains all blocks' coordinates
    :param opponent_token_array: the lower tokens list
    :param adjacent_token_list: the list contains all adjacent tokens
    :param last_hist_stack: the stack that contains token's last moving route
    :param move_hist_array: the list to hold action sequence of all tokens
    '''
    # Create a list to store the exploration positions when searching the path
    explored_pos_lst = [my_token_list[1]]
    # If the current token does not have a goal, generate all possible movement for its current position and make an idle move.
    if not goal:
        temp_move = gen_possible_moves(my_token_list[1], my_token_list[0],
                                       block_array, opponent_token_array,
                                       prev_pos, adjacent_token_list,
                                       my_token_array, explored_pos_lst)
        if temp_move:
            # Idle move option 1
            any_move_list = []
            for any_move in temp_move:
                if check_hex_occupancy(any_move, my_token_list,
                                       my_token_array):
                    any_move_list.append(any_move)
            if not any_move_list:
                any_move_list.append(temp_move[0])
            my_token_list[1] = any_move_list[0]
            my_token_list[3] = False
            return
        else:
            # Idle move option 2
            temp_move = gen_move_failure(my_token_list[1], my_token_list[0],
                                         block_array, opponent_token_array,
                                         prev_pos, adjacent_token_list,
                                         my_token_array, explored_pos_lst)
            my_token_list[1] = temp_move[0]
            my_token_list[3] = False
            return

    # If the current token has goals, use DFS path finding function to find the path towards the goal, and store the path to the hist_stack.
    temp = [my_token_list[1]]
    hist_stack = []
    recursive_DFS_path_finding(my_token_list[1], goal, my_token_list[0],
                               block_array, opponent_token_array, prev_pos,
                               adjacent_token_list, my_token_array,
                               explored_pos_lst, temp, hist_stack,
                               my_token_list[1])

    # Option 1. If there is no old path, use the newly found path as the optimal option, and make the movement for current turn.
    if not last_hist_stack:
        my_token_list[1] = hist_stack[1]
        my_token_list[3] = False
        hist_stack.pop(0)
        for move in hist_stack:
            last_hist_stack.append(move)
    # Option 2. If there is an old path exist, compare to the newly found path.
    else:
        # 2.1 If new path is same as the old path, keep using the old path as the optimal option, and make the movement for current turn.
        if hist_stack == last_hist_stack:
            my_token_list[1] = last_hist_stack[1]
            my_token_list[3] = False
            last_hist_stack.pop(0)
        # 2.2 If new path is not same as the old path.
        else:
            # 2.2.1. if the path availability of the old path is true
            if check_path_availablility(my_token_list, last_hist_stack,
                                        my_token_array, move_hist_array):
                # 2.2.1.1 Compare the length of both old path and new path, if the old path is shorter than new, select the old path to make a move.
                if (len(last_hist_stack) <= len(hist_stack)):
                    #print("-----option 2.211")
                    my_token_list[1] = last_hist_stack[1]
                    my_token_list[3] = False
                    last_hist_stack.pop(0)
                # 2.2.1.2 if the new path is shorter than old, select the new path to make a move, and copy the new path to the old one.
                else:
                    my_token_list[1] = hist_stack[1]
                    my_token_list[3] = False
                    hist_stack.pop(0)
                    last_hist_stack = hist_stack.copy()
            # 2.2.2 if the old path is not availiable, select the new path to make a move, and copy the new path to the old one.
            else:
                my_token_list[1] = hist_stack[1]
                my_token_list[3] = False
                hist_stack.pop(0)
                last_hist_stack = hist_stack.copy()


############################ CHECK FUNCTIONS ############################


def check_win_condition(my_token_array, opponent_token_array, show_text=False):
    '''
    Check if the upper player win the game by eliminating all of the lower tokens.

    :param my_token_array: the upper tokens list
    :param opponent_token_array: the lower tokens list
    :param show_text: a flag to indicate whether to display the text
    :return: true if upper player win the game
    '''
    if not opponent_token_array:
        if show_text is True:
            print("All opponent's tokens eliminated")
        return True
    for token in my_token_array:
        if token[2]:
            if show_text is True:
                print("Not win yet")
            return False
    if show_text is True:
        print("All opponent's tokens eliminated")
    return True


def check_path_availablility(my_token_list, hist_stack, my_token_array,
                             move_hist_array):
    '''
    Check if the given path is availiable for the token based on the game rule (i.e, blocked by any token that may lead to elimination of tokens).

    :param my_token_list: the list of current token's information
    :param hist_stack: stack that contains token's moving route
    :param my_token_array: the upper tokens list
    :param move_hist_array: the list to hold action sequence of all tokens
    :return: false if the path is not available; True if the path is availiable
    '''
    # use a temp list to store all tokens on the boars excluding self
    temp = my_token_array.copy()
    temp.remove(my_token_list)
    token_type = my_token_list[0]

    # For all the tokens on the board excluding self, checking if every move in the move stack is not colliding with the tokens on the board.
    for token in temp:
        for move in hist_stack:
            # Indicating a potential collision on the route
            if move == token[1]:
                # The blocking token has been moved within this round and this is its final position
                if token[3] is False:
                    # But can still stack with the blocking token
                    if token[0] == token_type:
                        # Route is still avaibable
                        pass
                    # If not possible to stack and may result in one of the tokens being eliminated, route is not available
                    else:
                        return False
                # Possibility of not colliding exists
                elif token[3] is True:
                    # If can stack with the blocking token
                    if token[0] == token_type:
                        # Route is still available
                        pass
                    # If not possible to stack and may result in one of the tokens being eliminated again
                    else:
                        # index of the blocking token
                        block_index = my_token_array.index(token)
                        # Immediate collision
                        if move_hist_array[block_index][1] == hist_stack[1]:
                            # Route is not available
                            return False
                        else:
                            # Ignore when no immediate collision
                            pass
            # If this move will not be blocked by any token, route is available
            else:
                pass
    return True


def check_hex_occupancy(destination_hex, my_token_list, my_token_array):
    '''
    Check if the destination hex has been occupied by any upper token or not

    :param destination_hex: the coordinate of destination hex
    :param my_token_list: the list of current token's information
    :param my_token_array: the upper tokens list
    :return: false if the destination hex has been occupied by any upper token
    '''
    temp = my_token_array.copy()
    temp.remove(my_token_list)
    for token in my_token_array:
        if token[1] == destination_hex:
            if token[3] is True:
                pass
            elif token[3] is False:
                if token[0] == my_token_list[0]:
                    pass
            return False
    return True


def boarder_check(position):
    '''
    check if the position is in the board space.

    :param position: the coordinate (r, q) of the checking position
    :return: True if the position is in the board space, otherwise False
    '''
    if (position[0] < -4) or (position[0] > 4):
        return False
    if position[0] == 4:
        if not (-4 <= position[1] <= 0):
            return False
    elif position[0] == 3:
        if not (-4 <= position[1] <= 1):
            return False
    elif position[0] == 2:
        if not (-4 <= position[1] <= 2):
            return False
    elif position[0] == 1:
        if not (-4 <= position[1] <= 3):
            return False
    elif position[0] == 0:
        if not (-4 <= position[1] <= 4):
            return False
    elif position[0] == -1:
        if not (-3 <= position[1] <= 4):
            return False
    elif position[0] == -2:
        if not (-2 <= position[1] <= 4):
            return False
    elif position[0] == -3:
        if not (-1 <= position[1] <= 4):
            return False
    elif position[0] == -4:
        if not (0 <= position[1] <= 4):
            return False
    return True



############################ UPDATE FUNCTIONS ############################


def update_opponent_tokens(eliminated_token_pos, opponent_token_array):
    '''
    Update the lower tokens list by removing the eliminated lower token from the list.

    :param eliminated_token_pos: the coordinate of eliminated lower token
    :param opponent_token_array: the lower tokens list
    '''
    for token in opponent_token_array:
        if eliminated_token_pos == token[1]:
            opponent_token_array.remove(token)


def synchronize_goal(my_token_array, eliminated_token_pos, move_hist_array):
    '''
    Update the upper tokens list by removing the coordinate of eliminated lower token from the upper token's goal list, and also from the list of action sequence of all tokens.

    :param my_token_array: the upper tokens list
    :param eliminated_token_pos: the coordinate of eliminated lower token
    :param move_hist_array: the list of action sequence of all tokens
    '''
    for token in my_token_array:
        if eliminated_token_pos in token[2]:
            token[2].remove(eliminated_token_pos)
            move_hist_array[my_token_array.index(token)] = []


def reset_movement_status(my_token_array):
    '''
    Reset the movement status of each upper token to be true, so that tokens are allowed to move.

    :param my_token_array: the upper tokens list
    '''
    for token in my_token_array:
        token[3] = [True]


############################ HELPER FUNCTIONS ############################


def vertical_movement(token_position, direction):
    '''
    Move the token to the appropriate position vertically according to the direction of action.

    :param token_position: the coordinate of the token
    :param direction: string to represent moving direction
    :return: the new coordinate of the token
    '''
    if direction == "up":
        return (token_position[0] + 1, token_position[1])
    elif direction == "down":
        return (token_position[0] - 1, token_position[1])


def horizontal_movement(token_position, direction):
    '''
    Move the token to the appropriate position horizontally according to the direction of action.

    :param token_position: the coordinate of the token
    :param direction: string to represent moving direction
    :return: the new coordinate of the token
    '''
    if direction == "left":
        return (token_position[0], token_position[1] - 1)
    elif direction == "right":
        return (token_position[0], token_position[1] + 1)


def diagonal_movement(token_position, direction):
    '''
    Move the token to the appropriate position diagonally according to the direction of action.

    :param token_position: the coordinate of the token
    :param direction: string to represent moving direction
    :return: the new coordinate of the token
    '''
    if direction == "up":
        return (token_position[0] + 1, token_position[1] - 1)
    elif direction == "down":
        return (token_position[0] - 1, token_position[1] + 1)


def gen_next_all_potential_moves(token_position):
    '''
    Generate all coordinate tuples of next potential slide movement of current token and store them into a list.

    :param token_position: the coordinate of current token
    :return: a list contains all coordinate tuples of next potential slide movement
    '''
    potential_movements = []
    potential_movements.append(vertical_movement(token_position, "up"))
    potential_movements.append(vertical_movement(token_position, "down"))
    potential_movements.append(horizontal_movement(token_position, "left"))
    potential_movements.append(horizontal_movement(token_position, "right"))
    potential_movements.append(diagonal_movement(token_position, "up"))
    potential_movements.append(diagonal_movement(token_position, "down"))
    potential_movements_in_range = potential_movements.copy()
    # if the move is out of the board space, remove it from the list
    for move in potential_movements:
        if boarder_check(move) is False:
            potential_movements_in_range.remove(move)
    return potential_movements_in_range


def get_token_adjacency(token_position, my_token_array):
    '''
    Generate all coordinate tuples of adjacency tokens of current token and store them into a list.

    :param token_position: the coordinate of current token
    :param my_token_array: the upper tokens list
    :return: a list contains all coordinate tuples of adjacency tokens
    '''
    adjacent_token_pos_list = []
    for token in my_token_array:
        if calculate_distance(token_position, token[1]) == 1.0:
            adjacent_token_pos_list.append(token[1])
    return adjacent_token_pos_list


def gen_all_potential_swing_moves(token_position, adjacent_token_list):
    '''
    Generate and return a list that contains all coordinate tuples of potential swing movements of current token.

    :param token_position: the coordinate of current token
    :param adjacent_token_list: the list of all adjacent tokens
    :return: a list contains all coordinate of potential swing movements
    '''
    potential_swing_movements = []
    if len(adjacent_token_list) == 0:
        return potential_swing_movements
    for adjacent_token in adjacent_token_list:
        potential_swing_movements.extend(
            gen_next_all_potential_moves(adjacent_token))
    for move in potential_swing_movements:
        if move == token_position:
            potential_swing_movements.remove(move)
    return potential_swing_movements


def gen_sorted_dist_for_possible_moves(possible_move_list, goal):
    '''
    Generate distance between the position of each possible move and the goal of current token, store each possible move and its distance into a list, and sort these lists in such a way that the move position with the closest distance towards the goal is in the beginning. Then return a list that only contains the position of the possible moves in this order.

    :param possible_move_list: the list of all possible moves of current token
    :param goal: the coordinate of the goal token
    :return: a sorted list contains all coordinates of possible moves in this order.
    '''
    possible_move_list_with_dist = []
    for i in range(len(possible_move_list)):
        possible_move_list_with_dist.append([
            possible_move_list[i],
            calculate_distance(possible_move_list[i], goal)
        ])
    sorted_lst = sorted(possible_move_list_with_dist, key=lambda x: x[1])
    pos_only_lst = []
    for move in sorted_lst:
        pos_only_lst.append(move[0])
    return pos_only_lst


def explore_next_point(destination, explored_pos_lst):
    '''
    Add destination hex to the explored position list if it is not in the list.

    :param destination: the coordinate of destination hex
    :param explored_pos_lst: the list contains all positions the current token can reach when searching the board
    '''
    if destination not in explored_pos_lst:
        explored_pos_lst.append(destination)


def pop_move_history_stack(move_history, branch_pos, origin):
    '''
    Pop the branch position from the moving history stack of the token by checking if the branch position and original position are the same, and also checking the length of the stack.

    :param move_history: the stack to store token's moving route
    :param branch_pos: the branch position of the token
    :param origin: the original position of the token
    '''
    if len(move_history) == 0:
        pass
    else:
        if branch_pos != origin:
            #print("---------------------Pop option 1, popping stack to", branch_pos)
            while branch_pos in move_history:
                if len(move_history) != 0:
                    move_history.pop()
                else:
                    break
            move_history.append(branch_pos)
        elif branch_pos == origin:
            #print("---------------------Pop option 2, popping stack to", branch_pos)
            while len(move_history) != 1:
                move_history.pop()


def gen_closest_goal(token_position, goal_list):
    '''
    Generate the closest goal position for the current token.

    :param token_position: the coordinate (r, q) of current token
    :param goal_list: the list contains all goals' coordinates of current token
    :return: the coordinate of closest goal
    '''
    if not goal_list:
        return
    closest = goal_list[0]
    closest_dist = calculate_distance(token_position, goal_list[0])
    for goal in goal_list:
        distance = calculate_distance(token_position, goal)
        if distance < closest_dist:
            closest = goal
    return closest


def calculate_distance(start, goal):
    '''
    Calculate the distance between two hex coordinates.

    :param start: the coordinate (r, q) of start hex
    :param goal: the coordinate (r, q) of goal hex
    :return: the distance between two hex coordinates
    '''
    distance = math.sqrt((start[0] - goal[0])**2 + (start[1] - goal[1])**2 + (start[0] - goal[0]) * (start[1] - goal[1]))
    return distance
