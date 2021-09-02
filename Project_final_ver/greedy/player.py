"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part B: Playing the Game
Team Name: Admin
Team Member: Yifeng Pan (955797) & Ziqi Jia (693241)
Description: Player class
"""

import heapq
import random

# all hexes
_HEX_RANGE = range(-4, +4 + 1)
_ORD_HEXES = {
    (r, q) for r in _HEX_RANGE for q in _HEX_RANGE if -r - q in _HEX_RANGE
}
_SET_HEXES = frozenset(_ORD_HEXES)

# nearby hexes
_HEX_STEPS = [(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)]


def _ADJACENT(x):
    rx, qx = x
    return _SET_HEXES & {(rx + ry, qx + qy) for ry, qy in _HEX_STEPS}


# rock-paper-scissors mechanic
_BEATS_WHAT = {"r": "s", "p": "r", "s": "p"}
_WHAT_BEATS = {"r": "p", "p": "s", "s": "r"}
_HEX_BIAS_UP = [list(range(0,4)),list(range(-1,4)),list(range(-2,4)),list(range(-3,4)),list(range(-4,4)),list(range(-4,3)),list(range(-4,2)),list(range(-4,1)),list(range(-4,0))]

def _BATTLE(symbols):
    types = {s.lower() for s in symbols}
    if len(types) == 1:
        # no fights
        return symbols
    if len(types) == 3:
        # everyone dies
        return []
    # else there are two, only some die:
    for t in types:
        # those who are not defeated stay
        symbols = [s for s in symbols if s.lower() != _BEATS_WHAT[t]]
    return symbols

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
        # initialise game board state, and both players with zero throws
        self.board = {x: [] for x in _ORD_HEXES}
        self.my_tokens = {"p":[],"s":[],"r":[]}
        self.rival_tokens = {"p":[],"s":[],"r":[]}
        self.throws = {"my": 0, "rival": 0}
        self.killed = {"my":0,"rival":0}
        self.color = player
        # set for action preference
        self.bias = (9-self.killed["my"])/70

    def print_state(self):
        print("my tokens ")
        print(self.my_tokens)
        print("rival tokens ")
        print(self.rival_tokens)
        print("my color is "+self.color)
        print("throws: ")
        print(self.throws)
        print("killed :")
        print(self.killed)
        #print( h in self.board if len(h)>=0])
        print(self.board)

    def clear(self):
        self.board = {x: [] for x in _ORD_HEXES}
        self.my_tokens = {"p":[],"s":[],"r":[]}
        self.rival_tokens = {"p":[],"s":[],"r":[]}
        self.throws = {"my": 0, "rival": 0}
        self.killed = {"my": 0, "rival": 0}

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
        #you have to throw a token at the first round any way
        if self.throws["my"] == 0:
            allowed_r_coord = 0
            allowed_q_coord = 0
            allowed_coord = (allowed_r_coord, allowed_q_coord)
            if self.color == "upper":
                allowed_r_coord = 4
                allowed_q_coord = [i for i in range(-4, 0)]
                allowed_coord = (allowed_r_coord, random.choice(allowed_q_coord))
            else:
                allowed_r_coord = -4
                allowed_q_coord = [i for i in range(0, 4)]
                allowed_coord = (allowed_r_coord, random.choice(allowed_q_coord))
            type_choice = ["r","s","p"]
            return ("THROW", random.choice(type_choice), allowed_coord)

        # keep performing astar search every round but instead of performing the whole search,
        # and pruning cutoff the unneccessary nodes and fouces on only the current round.
        actions = []

        #there are tokens on the board
        if self.throws["my"] - self.killed["my"] > 0:
            # compute the distance value for swing and slide for paper tokens
            for token in self.my_tokens["p"]:
                target = self.target(token,"p")

                def _adjacent(x):
                    return _ORD_HEXES & {self.add(x,y) for y in _HEX_STEPS}
                adjacent_x = _adjacent(token)
                for y in adjacent_x:
                    #if not self-occupied
                    #if not got token on adjecnt hex we slide
                    if (self.board[y] != "p" and self.board[y] != "r" and self.board[y] != "s" and self.color == "lower") or (self.color == "upper" and self.board[y] != "P" and self.board[y] != "R" and self.board[y] != "S"):
                        away = self.away(y, "p")
                        # consider the distance from its target as well as the distance from its threat
                        value_go = 1/self.distance(target,y)
                        value_away = 1/self.distance(away,y)
                        # heuristic function would be 1/closest_target_distance - 1/closest_beat_it_able_distance
                        value_net = value_go - value_away + self.bias
                        heapq.heappush(actions,(value_net,("SLIDE", (token[0], token[1]), (y[0], y[1]))))
                    # if got token on adjecnt we can swing
                    else:
                        opposite_y = _adjacent(y) - adjacent_x - {token}
                        for z in opposite_y:
                            away = self.away(z,"p")
                            value_go = 1/self.distance(target, z)
                            value_away = 1/self.distance(away,z)
                            value_net = value_go - value_away + self.bias
                            heapq.heappush(actions,(value_net,("SWING", (token[0], token[1]), (z[0], z[1]))))

            # stupid repetition for rock
            for token in self.my_tokens["r"]:
                target = self.target(token,"r")

                def _adjacent(x):
                    return _ORD_HEXES & {self.add(x,y) for y in _HEX_STEPS}
                adjacent_x = _adjacent(token)
                for y in adjacent_x:
                    # if not self-occupied
                    # if not got token on adjecnt hex we slide
                    if (self.board[y] != "p" and self.board[y] != "r" and self.board[y] != "s" and self.color == "lower") or (self.color == "upper" and self.board[y] != "P" and self.board[y] != "R" and self.board[y] != "S"):
                        away = self.away(y, "r")
                        value_go = 1/self.distance(target,y)
                        value_away = 1/self.distance(away,y)
                        value_net = value_go - value_away + self.bias
                        heapq.heappush(actions,(value_net,("SLIDE", (token[0], token[1]), (y[0], y[1]))))
                    # if got token on adjecnt we can swing
                    else:
                        opposite_y = _adjacent(y) - adjacent_x - {token}
                        for z in opposite_y:
                            away = self.away(z,"r")
                            value_go = 1/self.distance(target,z)
                            value_away = 1/self.distance(away,z)
                            value_net = value_go - value_away + self.bias
                            heapq.heappush(actions,(value_net,("SWING", (token[0], token[1]), (z[0], z[1]))))

            # stupid repetition for scissor
            for token in self.my_tokens["s"]:
                target = self.target(token,"s")

                def _adjacent(x):
                    return _ORD_HEXES & {self.add(x,y) for y in _HEX_STEPS}
                adjacent_x = _adjacent(token)
                for y in adjacent_x:
                    # if not self-occupied
                    # if not got token on adjecnt hex we slide
                    if (self.board[y] != "p" and self.board[y] != "r" and self.board[y] != "s" and self.color == "lower") or (self.color == "upper" and self.board[y] != "P" and self.board[y] != "R" and self.board[y] != "S"):
                        away = self.away(y,"s")
                        value_go = 1/self.distance(target,y)
                        value_away = 1/self.distance(away,y)
                        value_net = value_go - value_away + self.bias
                        heapq.heappush(actions,(value_net,("SLIDE", (token[0], token[1]), (y[0], y[1]))))
                    #if got token on adjecnt we can swing
                    else:
                        opposite_y = _adjacent(y) - adjacent_x - {token}
                        for z in opposite_y:
                            away = self.away(z,"s")
                            value_go = 1/self.distance(target,z)
                            value_away = 1/self.distance(away,z)
                            value_net = value_go - value_away + self.bias
                            heapq.heappush(actions,(value_net,("SWING", (token[0], token[1]), (z[0], z[1]))))

        # For throw, we have to consider if there is any rival's token in the first n row(n is our throw_tokens)
        # add the throws actions to the list
        if self.throws["my"] < 9:
            throwable = self.throwable()
            exist_rivals = self.exist_in_throwable(throwable)
            # possible_hex = []
            # check any rival's tokens in our first n row. If there is at least one rival's tokens within our first n row, check all hex of those rivals' tokens.
            if (len(exist_rivals) > 0):
                for tokens in exist_rivals:

                    def _adjacent(x):
                        return _ORD_HEXES & {self.add(x,y) for y in _HEX_STEPS} & throwable
                    adj_x = _adjacent(token[1])
                    for x in adj_x:
                        # if so check if we have beatable tokens near it.
                        if (_WHAT_BEATS[token[0]].lower() not in self.board[x] and self.color == "lower") or (_WHAT_BEATS[token[0]].upper() not in self.board[x] and self.color == "upper"):
                            # we check if any rivals' beatable token to our token near the position (consider slide in this stage and add swing later)
                            if (_BEATS_WHAT[token[0]].upper() not in self.board[x] and self.color == "lower") or (_BEATS_WHAT[token[0]].lower() not in self.board[x] and self.color == "upper"):
                                # how close it is from its beatable rival token
                                # choose the closest one
                                away = self.away(token[1],_WHAT_BEATS[token[0]])
                                value_go = 1/0.1
                                value_away = 1/self.distance(away,token[1])
                                value_net = value_go - value_away
                                heapq.heappush(actions,(value_net,("THROW", _WHAT_BEATS[token[0]], token[1])))
            #if no rival tokens within first n rows, check how close it is from the rival token with largest row (smallest row in our opinion).
            else:
                largest_row = -4+self.throws["my"] if self.color == "lower" else 4 - self.throws["my"]
                # we assume we can get a throw on the largest row possible( all columns on that row and all options of symbol )
                for c in _HEX_BIAS_UP[largest_row+4]:
                    y = (largest_row,c)
                    if (self.board[y] != "p" and self.board[y] != "r" and self.board[y] != "s" and self.color == "lower") or (self.color == "upper" and self.board[y] != "P" and self.board[y] != "R" and self.board[y] != "S"):
                        for symbol in ["p","s","r"]:
                            target = self.target(y,symbol)
                            away = self.away(y,symbol)
                            value_go = 1/self.distance(target,y)
                            value_away = 1/self.distance(away,y)
                            value_net = value_go - value_away
                            #and put this actions to the list
                            heapq.heappush(actions,(value_net,("THROW", symbol, (y[0],y[1]))))
        # After we got all these actions, select the highest action.
        # Note(if a throw and (swing or slide) has same value, we chose the swing or slide, if swing and slide has the same value, we chose swing.)
        return heapq.nlargest(1, actions)[0][1]

    def exist_in_throwable(self,throwable):
        result = []
        for s in self.rival_tokens:
            for t in self.rival_tokens[s]:
                if t in throwable:
                    result.append((s,t))
        return result

    def throwable(self):
        row = self.throws["my"]
        throwable = set([])
        if self.color == "lower":
            #end_row = -4 + row +1
            for j in (list(range(0,row+1))):
                for i in _HEX_BIAS_UP[j]:
                    throwable.update((-4+j,i))
            return throwable
        else:
            '''d2 = np.array(_HEX_BIAS_UP[::-1])
            d1 = np.array(list(range(4，-5,-1))
            return np.vstack((d1, d2)).T'''
            for j in (list(range(0,row+1))):
                for i in _HEX_BIAS_UP[8-j]:
                    throwable.update((4-j,i))
            return throwable

    def away(self, x, s):
        #x position s type
        distance = [self.distance(x,y) for y in self.rival_tokens[_WHAT_BEATS[s]]]
        if len(distance) == 0:
            return (100,100)
        minimum = min(distance)
        #return (x,y) value of the closest target
        return self.rival_tokens[_WHAT_BEATS[s]][distance.index(minimum)]

    def distance(self,x,y):
        z_r = x[0] - y[0]
        z_q = x[1] - y[1]
        value = (abs(z_r) + abs(z_q) + abs(z_r + z_q)) // 2
        if value == 0:
            return 0.1
        else:
            return value

    def target(self,x,s):
        #x position s type
        distance = [self.distance(x,y) for y in self.rival_tokens[_BEATS_WHAT[s]]]
        if len(distance) == 0:
            return (100,100)
        minimum = min(distance)
        #return (x,y) value of the closest target
        return self.rival_tokens[_BEATS_WHAT[s]][distance.index(minimum)]

    def add(self,x,y):
        return(x[0] + y[0], x[1] + y[1])

    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # put your code here
        """
        Submit an action to the game for validation and application.
        If the action is not allowed, raise an InvalidActionException with
        a message describing allowed actions.
        Otherwise, apply the action to the game state.
        """
        # otherwise, apply the actions:
        battles = []
        atype, *aargs = player_action
        if atype == "THROW":
            s, x = aargs
            #UPDATE BOARD
            self.board[x].append(s.upper())
            #UPDATE TOKENS OF PLAYER ->update to the belonging type so serach
            #later would be more efficient
            self.my_tokens[s].append(x)
            #UPDATE THORWS
            self.throws["my"] += 1
            battles.append(x)
        else:
            x, y = aargs
            # remove ONE UPPER-CASE SYMBOL from self.board[x] (all the same)
            t = self.board[x][0].lower()
            s = self.board[x][0].upper()
            self.board[x].remove(s)
            self.board[y].append(s)
            # add it to self.board[y]
            #remove from token lists as well
            self.my_tokens[t].remove(x)
            self.my_tokens[t].append(y)

            battles.append(y)

        atype, *aargs = opponent_action
        if atype == "THROW":
            s, x = aargs
            self.board[x].append(s.lower())
            self.rival_tokens[s].append(x)

            self.throws["rival"] += 1
            battles.append(x)
        else:
            x, y = aargs
            # remove ONE LOWER-CASE SYMBOL from self.board[x] (all the same)
            s = self.board[x][0].lower()
            self.board[x].remove(s)
            self.board[y].append(s)
            # add it to self.board[y]
            self.rival_tokens[s].remove(x)
            self.rival_tokens[s].append(y)
            battles.append(y)

        # resolve hexes with new tokens:
        for x in battles:
            # TODO: include summary of battles in output?
            #print(x)
            self.board[x] = _BATTLE(self.board[x])
            #remove killed from tokens
            for token in self.my_tokens:
                if len(self.board[x]) == 0:
                    self.my_tokens[token] = [e for e in self.my_tokens[token] if e != x]
                else:
                    if token != self.board[x][0].lower():
                        self.my_tokens[token] = [e for e in self.my_tokens[token] if e != x]
            for token in self.rival_tokens:
                if len(self.board[x]) == 0:
                    self.rival_tokens[token] = [e for e in self.rival_tokens[token] if e != x]
                else:
                    if token != self.board[x][0].lower():
                        self.rival_tokens[token] = [e for e in self.rival_tokens[token] if e != x]

        self.killed["my"] = self.throws["my"] - len(self.my_tokens["p"]) - len(self.my_tokens["r"]) - len(self.my_tokens["s"])
        self.killed["rival"] = self.throws["rival"] - len(self.rival_tokens["p"]) - len(self.rival_tokens["r"]) - len(self.rival_tokens["s"])
