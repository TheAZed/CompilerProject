EPSILON = "epsilon"


class Literal:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


class Terminal(Literal):
    pass


class NonTerminal(Literal):
    def __init__(self, name, first_list, diagram):  # list of firsts. contains Terminals' names(str)
        Literal.__init__(self, name)
        self.first = first_list
        self.diagram = diagram

    def get_firsts(self):
        return self.first


class State:
    def __init__(self, name=""):
        self.name = name
        self.neighbors = {}  # {terminal.name(str): (state, is edge terminal?)}

    def set_next_state(self, literal, state):
        if literal.get_name() == EPSILON:
            self.neighbors[EPSILON] = (state, False)
            return
        if isinstance(literal, Terminal):
            self.neighbors[literal.get_name()] = (state, True)
        if isinstance(literal, NonTerminal):
            literal.diagram.final_state.set_next_state(Terminal(EPSILON), state)
            for terminal_names in literal.get_firsts():
                self.neighbors[terminal_names] = (literal.diagram.start_state, False)

    def get_next_state(self, token):
        next_states = []
        for terminal_name in self.neighbors:
            if terminal_name == token:
                next_states.append(self.neighbors[terminal_name])
        if len(next_states) == 1:
            return next_states[0]
        if len(next_states) == 0:
            if self.neighbors.__contains__(EPSILON):
                return self.neighbors[EPSILON]
            else:
                return None  # panic mode

        if len(next_states) > 1:  # grammar is not predictive
            message = "following states are available with current token: " + token + "\n"
            for state in next_states:
                message += state.name
            raise Exception(message)


class Diagram:
    def __init__(self, start, final):
        self.start_state = start
        self.final_state = final

    def accepts(self, scanner=None):
        global token
        accepted = ""
        current_state = self.start_state
        while current_state != self.final_state:
            print(current_state.name, ",", token, "->", end=" ")
            next_state = current_state.get_next_state(token)
            if next_state is None:
                print("Panic!")
                return False, accepted  # panic mode
            print(next_state[0].name)
            current_state, is_edge_terminal = next_state[0], next_state[1]
            if is_edge_terminal:
                accepted += token
                token = get_next_token()
        return True, accepted


scanner_output = "aabbbaa"
pointer = 0


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
s4 = State("S4")
s5 = State("S5")
s6 = State("S6")

A_diagram = Diagram(s1, s3)
B_diagram = Diagram(s4, s6)
A = NonTerminal("A", ["a"], A_diagram)
B = NonTerminal("B", ["b"], B_diagram)

s1.set_next_state(Terminal("a"), s2)
s2.set_next_state(B, s3)
s4.set_next_state(Terminal("b"), s5)
s5.set_next_state(Terminal("a"), s5)
s5.set_next_state(Terminal(EPSILON), s6)


flag, accepted = A_diagram.accepts()
if flag:
    print("A accepted:", accepted)
else:
    print("A did not accept")