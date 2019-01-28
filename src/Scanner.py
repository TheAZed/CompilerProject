import re
import threading

reserved_words = [word for word in open("../Documents/ReservedWords.txt", "r")]
symbol_list = [symbol for symbol in open("../Documents/LanguageSymbols.txt", "r")]
delim_list = symbol_list[0:9]
whitespaces = ['\t', '\n', '\r', ' ']


class Scanner:

    def __init__(self, file_address):
        super().__init__()
        self.errors = []
        self.file = open(file_address, "r")
        self.previous_token = None
        self.current_token = None
        self.token_list = []
        self.token_list_pointer = 0
        self.machine_finals = [(2, False), (5, False), (6, True), (10, True), (13, True), (12, False)]
        self.state_machine = StateMachine(14, [(0, 0, r'[\r\s]'), (0, 1, r'[A-Za-z]'), (1, 1, r'[A-Za-z0-9]'),
                                               (1, 2, r'[^A-Za-z0-9]'), (0, 3, r'[\+\-]'), (3, 3, r'[\r\s]'),
                                               (0, 4, r'[0-9]'), (3, 4, r'[0-9]'), (4, 4, r'[0-9]'), (4, 5, r'[^0-9]'),
                                               (0, 6, r'[\+\;\:\,\-\{\}\[\]\(\)\*\<]'), (0, 7, r'[\/]'),
                                               (7, 8, r'[\*]'), (8, 8, r'[^\*]'), (8, 9, r'[\*]'), (9, 8, r'[^\*\/]'),
                                               (9, 9, r'[\*]'), (9, 10, r'[\/]'), (0, 11, r'[\=]'), (11, 12, r'[^\=]'),
                                               (11, 13, r'[\=]')],
                                          self.machine_finals)
        self.go_next = True
        self.next_char = ''

    def get_next_token(self):
        """

        :return: :type Token
        """
        if self.go_next:
            self.next_char = self.file.read(1)
        while self.next_char != '':
            self.go_next = True
            state = self.state_machine.move(self.next_char, self.previous_token)
            if state == -1:
                self.errors.append("Invalid " + self.next_char + "!")
                self.state_machine.reset()
            elif state > 0:
                self.go_next = [f_state[1] for f_state in self.machine_finals if f_state[0] == state][0]
                if not self.go_next:
                    token_str = self.state_machine.accumulated_string[:-1]
                else:
                    token_str = self.state_machine.accumulated_string
                if state == 2:
                    #  FIXME: Should check parse table
                    self.token_list.append(Token(token_str, "ID"))
                elif state == 5:
                    self.token_list.append(Token(token_str, "NUM"))
                elif state == 6:
                    if token_str == "<":
                        self.token_list.append(Token(token_str, "relop"))
                    else:
                        self.token_list.append(Token(token_str, "Sym"))
                elif state == 10:
                    self.token_list.append(Token(token_str, "Comment"))
                elif state == 12:
                    self.token_list.append(Token(token_str, "Sym"))
                elif state == 13:
                    self.token_list.append(Token(token_str, "relop"))
                self.previous_token = self.token_list[len(self.token_list) - 2]
                self.state_machine.reset()
                return self.token_list[len(self.token_list) - 1]
            if self.go_next:
                self.next_char = self.file.read(1)
        self.token_list.append(Token("EOF", "EOF"))
        self.previous_token = self.token_list[len(self.token_list) - 2]
        self.state_machine.reset()
        return self.token_list[len(self.token_list) - 1]


class StateMachine:
    def __init__(self, nodes_count, edge_list, final_states):
        self.current_pointer = 0
        self.nodes_count = nodes_count
        self.edge_list = edge_list
        self.accumulated_string = ""
        self.final_states = final_states
        self.done = False

    def move(self, current_input, prev_token):
        """

        :param current_input: :type str
        :param prev_token: :type Token
        :return: :type int
        """
        if not self.done:
            # Special case
            if self.current_pointer == 0 and current_input == '+' or current_input == '-':
                if prev_token is not None and prev_token.token_type == "ID" or prev_token.token_type == "NUM":
                    self.current_pointer = 6
                    self.done = True
                    return self.current_pointer
                else:
                    self.current_pointer = 3
                    return 0
            while True:
                possible_edges = [edge for edge in self.edge_list if edge[0] == self.current_pointer]
                for edge in possible_edges:
                    if edge[2] is not None:
                        if re.match(edge[2], current_input) is not None:
                            self.current_pointer = edge[1]
                            if edge[2] != r'[\r\s]':
                                self.accumulated_string += current_input
                            for final in self.final_states:
                                if self.current_pointer == final[0]:
                                    self.done = True
                                    # type of return can be found using
                                    return self.current_pointer
                            # 0 means no error and not in final state
                            return 0
                moved = False
                if not moved:
                    for edge in possible_edges:
                        if edge[2] is None:
                            self.current_pointer = edge[1]
                            moved = True
                            break
                if not moved:
                    # -1 means error
                    self.done = True
                    return -1

    def reset(self):
        self.accumulated_string = ""
        self.done = False
        self.current_pointer = 0

    def accept_state(self):
        return self.current_pointer == self.nodes_count - 1 and self.done


class Token:
    def __init__(self, string, token_type):
        """

        :param string: :type str
        :param token_type: :type str
        """
        self.string = string
        self.token_type = token_type

    def __eq__(self, other):
        if other is None:
            return False
        if type(other) == Token:
            return self.string == other.string
        if type(other) == str:
            return self.string == other
        return False


