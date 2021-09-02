"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part B: Playing the Game
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)
Description: Player class
"""

from admin.heuristics import *
from admin.pathfinding import *

class Player:
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        # put your code here
        #initialize the player
        self.player = player
        self.my_throws_left = 9
        self.enemies_defeated = 0
        self.my_defeated_token_num = 0
        self.opponent_throws_left = 9
        self.my_throw_range = 0
        self.op_throw_range = 0
        self.player_pos = []
        self.opponent_pos = []


    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
        decision = make_decision(self.player_pos, self.opponent_pos, self.opponent_throws_left, self.my_throw_range, self.op_throw_range, self.my_defeated_token_num, self.enemies_defeated, self.player, self.my_throws_left)
        if decision[0] == "THROW":
            return decision
        elif decision[0] == "Move":
            if calculate_distance(decision[1],decision[2]) == 1.0:
                return ("SLIDE", (decision[1][0], decision[1][1]),(decision[2][0], decision[2][1]))
            else:
                return ("SWING", (decision[1][0], decision[1][1]),(decision[2][0], decision[2][1]))


    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """

        # put your code here

        # Following section updates token positions first
        # Update opponent positions (and pawns if newly added)
        if opponent_action[0] == "THROW":
            if self.op_throw_range <= 9:
                self.op_throw_range += 1
            self.opponent_throws_left -= 1
            self.opponent_pos.append([opponent_action[1],(opponent_action[2][0],opponent_action[2][1]),[],[]]) # a list ['token_type',(r,q),[list_of_goal_pos],[list_of_threat_pos]]
        else:
            for position in self.opponent_pos:
                if position[1] == opponent_action[1]:
                    position[1] = opponent_action[2]

        if player_action[0] == "THROW":
            if self.my_throw_range <= 9:
                self.my_throw_range += 1
            self.my_throws_left -= 1
            self.player_pos.append([player_action[1],(player_action[2][0],player_action[2][1]),[],[]]) # a list ['token_type',(r,q),[list_of_goal_pos],[list_of_threat_pos]]
        else:
            for position in self.player_pos:
                if position[1] == player_action[1]:
                    position[1] = player_action[2]

        # Check for s-p-r dies together situation
        player_pos_copy = self.player_pos.copy()
        opp_pos_copy = self.opponent_pos.copy()
        for i in range(len(player_pos_copy)):
            for j in range(len(opp_pos_copy)):
                for k in range(len(player_pos_copy)):
                    if i != k:
                        if player_pos_copy[i][1] == player_pos_copy[k][1] == opp_pos_copy[j][1]:
                            if (player_pos_copy[i][0] != opp_pos_copy[j][0]) and (player_pos_copy[k][0] != opp_pos_copy[j][0]) and (player_pos_copy[i][0] != player_pos_copy[k][0]):
                                if player_pos_copy[i] in self.player_pos:
                                    self.my_defeated_token_num += 1
                                    self.player_pos.remove(player_pos_copy[i])
                                if player_pos_copy[k] in self.player_pos:
                                    self.my_defeated_token_num += 1
                                    self.player_pos.remove(player_pos_copy[k])
                                if opp_pos_copy[j] in self.opponent_pos:
                                    self.enemies_defeated += 1
                                    self.opponent_pos.remove(opp_pos_copy[j])

        player_pos_copy = self.player_pos.copy()
        opp_pos_copy = self.opponent_pos.copy()
        for i in range(len(opp_pos_copy)):
            for j in range(len(player_pos_copy)):
                for k in range(len(opp_pos_copy)):
                    if i != k:
                        if opp_pos_copy[i][1] == opp_pos_copy[k][1] == player_pos_copy[j][1]:
                            if (opp_pos_copy[i][0] != player_pos_copy[j][0]) and (opp_pos_copy[k][0] != player_pos_copy[j][0]) and (opp_pos_copy[i][0] != opp_pos_copy[k][0]):
                                if opp_pos_copy[i] in self.opponent_pos:
                                    self.enemies_defeated += 1
                                    self.opponent_pos.remove(opp_pos_copy[i])
                                if opp_pos_copy[k] in self.opponent_pos:
                                    self.enemies_defeated += 1
                                    self.opponent_pos.remove(opp_pos_copy[k])
                                if player_pos_copy[j] in self.player_pos:
                                    self.my_defeated_token_num += 1
                                    self.player_pos.remove(player_pos_copy[j])

        # Check for opposing overlapping pawns and remove them by rules
        player_pos_copy = self.player_pos.copy()
        opp_pos_copy = self.opponent_pos.copy()

        for my_token in player_pos_copy:
            my_token_type = my_token[0]
            my_token_pos = my_token[1]
            for enemy_token in opp_pos_copy:
                enemy_token_type = enemy_token[0]
                enemy_token_pos = enemy_token[1]
                if my_token_pos == enemy_token_pos:
                    if (enemy_token_type == "r") and (my_token_type == "s"):
                        if my_token in self.player_pos:
                            self.player_pos.remove(my_token)
                        self.my_defeated_token_num += 1
                        break
                    elif (enemy_token_type == "s") and (my_token_type == "p"):
                        self.my_defeated_token_num += 1
                        if my_token in self.player_pos:
                            self.player_pos.remove(my_token)
                        break
                    elif (enemy_token_type == "p") and (my_token_type == "r"):
                        self.my_defeated_token_num += 1
                        if my_token in self.player_pos:
                            self.player_pos.remove(my_token)
                        break
                    elif (enemy_token_type == "s") and (my_token_type == "r"):
                        self.enemies_defeated += 1
                        if enemy_token in self.opponent_pos:
                            self.opponent_pos.remove(enemy_token)
                        break
                    elif (enemy_token_type == "p") and (my_token_type == "s"):
                        self.enemies_defeated += 1
                        if enemy_token in self.opponent_pos:
                            self.opponent_pos.remove(enemy_token)
                        break
                    elif (enemy_token_type == "r") and (my_token_type == "p"):
                        self.enemies_defeated += 1
                        if enemy_token in self.opponent_pos:
                            self.opponent_pos.remove(enemy_token)
                        break

        # Check for friendly overlapping pawns and remove them by rules (if any)
        player_pos_copy = self.player_pos.copy()
        for token_1 in player_pos_copy:
            token_1_type = token_1[0]
            token_1_pos = token_1[1]
            for token_2 in player_pos_copy:
                token_2_type = token_2[0]
                token_2_pos = token_2[1]
                if token_1_pos == token_2_pos:
                    if (token_1_type == "r") and (token_2_type == "s"):
                        self.my_defeated_token_num += 1
                        if token_2 in self.player_pos:
                            self.player_pos.remove(token_2)
                        break
                    elif (token_1_type == "s") and (token_2_type == "p"):
                        self.my_defeated_token_num += 1
                        if token_2 in self.player_pos:
                            self.player_pos.remove(token_2)
                        break
                    elif (token_1_type == "p") and (token_2_type == "r"):
                        self.my_defeated_token_num += 1
                        if token_2 in self.player_pos:
                            self.player_pos.remove(token_2)
                        break
                    elif (token_1_type == "s") and (token_2_type == "r"):
                        self.my_defeated_token_num += 1
                        if token_1 in self.player_pos:
                            self.player_pos.remove(token_1)
                        break
                    elif (token_1_type == "p") and (token_2_type == "s"):
                        self.my_defeated_token_num += 1
                        if token_1 in self.player_pos:
                            self.player_pos.remove(token_1)
                        break
                    elif (token_1_type == "r") and (token_2_type == "p"):
                        self.my_defeated_token_num += 1
                        if token_1 in self.player_pos:
                            self.player_pos.remove(token_1)
                        break

        # Check for enemy's overlapping pawns and remove them by rules (if any)
        opp_pos_copy = self.opponent_pos.copy()
        for token_1 in opp_pos_copy:
            token_1_type = token_1[0]
            token_1_pos = token_1[1]
            for token_2 in opp_pos_copy:
                token_2_type = token_2[0]
                token_2_pos = token_2[1]
                if token_1_pos == token_2_pos:
                    if (token_1_type == "r") and (token_2_type == "s"):
                        self.enemies_defeated += 1
                        if token_2 in self.opponent_pos:
                            self.opponent_pos.remove(token_2)
                        break
                    elif (token_1_type == "s") and (token_2_type == "p"):
                        self.enemies_defeated += 1
                        if token_2 in self.opponent_pos:
                            self.opponent_pos.remove(token_2)
                        break
                    elif (token_1_type == "p") and (token_2_type == "r"):
                        self.enemies_defeated += 1
                        if token_2 in self.opponent_pos:
                            self.opponent_pos.remove(token_2)
                        break
                    elif (token_1_type == "s") and (token_2_type == "r"):
                        self.enemies_defeated += 1
                        if token_1 in self.opponent_pos:
                            self.opponent_pos.remove(token_1)
                        break
                    elif (token_1_type == "p") and (token_2_type == "s"):
                        self.enemies_defeated += 1
                        if token_1 in self.opponent_pos:
                            self.opponent_pos.remove(token_1)
                        break
                    elif (token_1_type == "r") and (token_2_type == "p"):
                        self.enemies_defeated += 1
                        if token_1 in self.opponent_pos:
                            self.opponent_pos.remove(token_1)
                        break

        # Update friendly token's goal and threat
        for token in self.player_pos:
            token[2] = []
            token[3] = []
            my_token_type = token[0]
            for target in self.opponent_pos:
                enemy_token_type = target[0]
                enemy_token_pos = target[1]
                if (enemy_token_type == "s") and (my_token_type == "r"):
                    token[2].append(enemy_token_pos)
                elif (enemy_token_type == "p") and (my_token_type == "s"):
                    token[2].append(enemy_token_pos)
                elif (enemy_token_type == "r") and (my_token_type == "p"):
                    token[2].append(enemy_token_pos)
                if (enemy_token_type == "r") and (my_token_type == "s"):
                    token[3].append(enemy_token_pos)
                elif (enemy_token_type == "s") and (my_token_type == "p"):
                    token[3].append(enemy_token_pos)
                elif (enemy_token_type == "p") and (my_token_type == "r"):
                    token[3].append(enemy_token_pos)

        # Update enemy token's goal and threat
        for token in self.opponent_pos:
            token[2] = []
            token[3] = []
            my_token_type = token[0]
            for target in self.player_pos:
                enemy_token_type = target[0]
                enemy_token_pos = target[1]
                if (enemy_token_type == "s") and (my_token_type == "r"):
                    token[2].append(enemy_token_pos)
                elif (enemy_token_type == "p") and (my_token_type == "s"):
                    token[2].append(enemy_token_pos)
                elif (enemy_token_type == "r") and (my_token_type == "p"):
                    token[2].append(enemy_token_pos)
                if (enemy_token_type == "r") and (my_token_type == "s"):
                    token[3].append(enemy_token_pos)
                elif (enemy_token_type == "s") and (my_token_type == "p"):
                    token[3].append(enemy_token_pos)
                elif (enemy_token_type == "p") and (my_token_type == "r"):
                    token[3].append(enemy_token_pos)
