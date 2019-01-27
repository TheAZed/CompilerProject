EPSILON = "epsilon"
STACK = []


def print_stack():
    for state, _, _ in STACK:
        print(state.non_terminal.name, end="")
    print()


class Literal:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


class Terminal(Literal):
    pass


class NonTerminal(Literal):
    def __init__(self, name, first_list, follow_list, diagram):  # lists of firsts and follows contain Terminals' names(str)
        Literal.__init__(self, name)
        self.first = first_list
        self.follow = follow_list
        self.diagram = diagram
        self.diagram.start_state.non_terminal = self


class State:
    def __init__(self, name="", is_end=False, non_terminal=None):
        self.name = name
        self.non_terminal = non_terminal
        self.neighbors = {}  # {terminal.name(str): (state, is edge terminal?, literal)}
        self.is_end = is_end

    def set_next_state(self, literal, state):
        if literal.get_name() == EPSILON:
            if state.non_terminal is None:
                state.non_terminal = self.non_terminal
            self.neighbors[EPSILON] = (state, EPSILON, literal)
            return
        if isinstance(literal, Terminal):
            if state.non_terminal is None:
                state.non_terminal = self.non_terminal
            self.neighbors[literal.get_name()] = (state, True, literal)
        if isinstance(literal, NonTerminal):
            if state.non_terminal is None:
                state.non_terminal = self.non_terminal
            self.neighbors[literal.get_name()] = (state, False, literal)

    def get_next_state(self, token):
        next_states = []
        edge_is_non_terminal = False
        for literal_name in self.neighbors:
            if self.neighbors[literal_name][1]:  # Terminal
                if literal_name == token:
                    next_states.append(self.neighbors[literal_name])
            else:                                # NonTerminal
                non_terminal = self.neighbors[literal_name][2]
                for first_name in non_terminal.first:
                    if first_name == token:
                        global STACK
                        next_states.append((non_terminal.diagram.start_state, False, non_terminal))
                        edge_is_non_terminal = True
                if edge_is_non_terminal:
                    STACK.append(self.neighbors[literal_name])

        if len(next_states) == 1:
            return next_states[0]
        if len(next_states) == 0:
            if self.is_end:  # reduce
                if token in self.non_terminal.follow:
                    return STACK.pop()
            if self.neighbors.__contains__(EPSILON):
                return self.neighbors[EPSILON]
            else:  # panic
                return None

        if len(next_states) > 1:  # grammar is not predictive
            message = "following states are available with current token: " + token + "\n"
            for state in next_states:
                message += state.name
            raise Exception(message)


class Diagram:
    def __init__(self, start, final):
        self.start_state = start
        self.final_state = final
        self.final_state.is_end = True


def parse(start_state, final_state, scanner=None):
    global token, STACK
    parsed = ""
    accepted = ""
    current_state = start_state
    while True:
        #print_stack()
        if current_state == final_state and token is None:
            return True, accepted, parsed
        next_state = current_state.get_next_state(token)
        if next_state is None:  # panic mode
            print(current_state.name, ",", token, "->", "Panic!")
            dumped_input = ""
            if token is not None:
                dumped_input += token
                token = get_next_token()
                while token not in end_tokens and token is not None:
                    dumped_input += token
                    token = get_next_token()

            print("dumped input:", dumped_input)
            #return False, accepted, parsed
            continue
        print(current_state.name, ",", token, "->", next_state[0].name, end=" ")
        current_state, is_edge_terminal = next_state[0], next_state[1]
        if is_edge_terminal == True:  # shift
            if token is not None:
                accepted += token
            token = get_next_token()
        print("accepted:", accepted)



scanner_output = "$accdbaaaaloiaa;ab;$"
pointer = 0
end_tokens = [";"]


def get_next_token():
    global pointer
    pointer += 1
    try:
        return scanner_output[pointer - 1]
    except IndexError:
        return None


token = get_next_token()


s1 = State("S1")
s2 = State("S2")
s3 = State("S3")
s3_1 = State("S3_1")
s3_2 = State("S3_2")
s4 = State("S4")
s5 = State("S5")
s6 = State("S6")
s7 = State("S7")
s8 = State("S8")
s9 = State("S9")
s10 = State("S10")
s11 = State("S11")
start = State("$s")
mid1 = State("$1")
mid2 = State("$2")
final = State("$f")


A_diagram = Diagram(s1, s3_1)
B_diagram = Diagram(s4, s6)
C_diagram = Diagram(s7, s11)
U_diagram = Diagram(s9, s10)
S_diagram = Diagram(start, final)

A = NonTerminal("A", ["a"], ["$"], A_diagram)
B = NonTerminal("B", ["b"], [";"], B_diagram)
C = NonTerminal("C", ["c", "d"], [";"], C_diagram)
U = NonTerminal("U", ["b", "c", "d"], [";"], U_diagram)
S = NonTerminal("S", ["$"], [], S_diagram)

"""
s1.non_terminal = A
s2.non_terminal = A
s3.non_terminal = A
s3_1.non_terminal = A
s4.non_terminal = B
s5.non_terminal = B
s6.non_terminal = B
s7.non_terminal = C
s8.non_terminal = C
s9.non_terminal = U
s10.non_terminal = U
s11.non_terminal = C
start.non_terminal = S
mid1.non_terminal = S
mid2.non_terminal = S
final.non_terminal = S
"""

s1.set_next_state(Terminal("a"), s2)
s2.set_next_state(U, s3)
s3.set_next_state(Terminal(";"), s3_1)
s3_1.set_next_state(Terminal(EPSILON), s1)
s4.set_next_state(Terminal("b"), s5)
s5.set_next_state(Terminal("a"), s5)
s5.set_next_state(Terminal(EPSILON), s6)
s7.set_next_state(Terminal("c"), s7)
s7.set_next_state(Terminal("d"), s8)
s9.set_next_state(B, s10)
s9.set_next_state(C, s10)
s8.set_next_state(U, s11)
start.set_next_state(Terminal("$"), mid1)
mid1.set_next_state(A, mid2)
mid2.set_next_state(Terminal("$"), final)

flag, accepted, parsed = parse(start, final)
print("accepted:", accepted)
