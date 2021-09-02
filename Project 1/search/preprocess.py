'''
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)

This module contain functions to preprocessing the data.
'''

def visual_data_preprocess(data_dict):
    '''
    Initialize the board dictionary and return a dictionary with the format
    that can be used in print_board function.

    :param data_dict: data that describe the board configuration
    :return: A dictionary with (r, q) tuples as keys and printable objects as values.
    '''
    board_dict = {}
    for token_type in data_dict:
        if token_type == "upper":
            for token in data_dict[token_type]:
                board_dict[(token[1], token[2])] = token[0].upper()
        elif token_type == "lower":
            for token in data_dict[token_type]:
                board_dict[(token[1], token[2])] = token[0]
        elif token_type == "block":
            for token in data_dict[token_type]:
                board_dict[(token[1], token[2])] = "Block"
    return board_dict


def gen_my_tokens(data_dict):
    '''
    Generate and return a list of all upper tokens from the board dictionary. Each token is represented by a list with its symbol ('r', 's', or 'p'), coordinate (r, q) and a empty list that will be used to store its goals' coordinates.

    :param data_dict: the board dictionary
    :return: a list contains all the upper tokens
    '''
    my_token_array = []
    for token in data_dict["upper"]:
        my_token_array.append([token[0], (token[1], token[2]), []])
    return my_token_array


def gen_opponent_tokens(data_dict):
    '''
    Generate and return a list of all lower pieces from the board dictionary. Each lower piece is represented by a list with its symbol ('r', 's', or 'p'), and coordinate (r, q).

    :param data_dict: the board dictionary
    :return: a list contains all the lower tokens
    '''
    opponent_token_array = []
    for token in data_dict["lower"]:
        opponent_token_array.append([token[0], (token[1], token[2])])
    return opponent_token_array


def gen_blocks(data_dict):
    '''
    Generate and return a list of all block's coordinates from the board dictionary.

    :param data_dict: the board dictionary
    :return: a list of tuples contains the coordinates of block's pieces
    '''
    block_array = []
    for block in data_dict["block"]:
        block_array.append((block[1], block[2]))
    return block_array


def gen_goal_for_token(data_dict, my_token_array):
    '''
    For each upper token, generate the coordinate tuples of its goal pieces and update the upper tokens list.

    :param data_dict: the board dictionary
    :param my_token_array: the upper tokens list
    :return: a list contains all the upper tokens with goals' coordinates
    '''
    for token in data_dict["lower"]:
        if token[0] == "r":
            for my_token in my_token_array:
                if my_token[0] == "p":
                    my_token[2].append((token[1], token[2]))
        elif token[0] == "s":
            for my_token in my_token_array:
                if my_token[0] == "r":
                    my_token[2].append((token[1], token[2]))
        elif token[0] == "p":
            for my_token in my_token_array:
                if my_token[0] == "s":
                    my_token[2].append((token[1], token[2]))
    for my_token in my_token_array:
        # A flag indicating whether the token has been moved or not
        my_token.append(True)
    return my_token_array
