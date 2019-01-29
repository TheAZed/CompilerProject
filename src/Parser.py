from src.FunctionLibrary import Librarian
from src.Scanner import Scanner
EPSILON = "epsilon"
STACK = []
SCANNER = Scanner("../Test/ParserTest.txt")
LIBRARIAN = Librarian(scanner=SCANNER)
LIBRARIAN.call_func("generate_first_block")


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
        self.func_names = []

    def set_function(self, func_name):
        self.func_names.append(func_name)

    def call_functions(self):
        for func_name in self.func_names:
            LIBRARIAN.call_func(func_name)

    def set_next_state(self, literal, state):
        if isinstance(literal, str):
            self.set_next_state(Terminal(literal), state)
        else:
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
        global STACK
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
                        next_states.append((non_terminal.diagram.start_state, False, non_terminal))
                        edge_is_non_terminal = True
                if len(next_states) == 0:
                    if EPSILON in non_terminal.first:
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
            message = "more than one choice from state '" + self.name + "' with token '" + token + "': "
            for state, _, _ in next_states:
                message += state.name + ", "

            class UnPredictiveGrammarException(Exception):
                __module__ = Exception.__module__
                pass

            raise UnPredictiveGrammarException(message[:-2])


class Diagram:
    def __init__(self, start, final):
        self.start_state = start
        self.final_state = final
        self.final_state.is_end = True


def parse(start_state, final_state):
    global token, STACK
    parsed = ""
    accepted = ""
    current_state = start_state
    while True:
        #print_stack()
        if current_state == final_state and token == "EOF":
            return True, accepted, parsed
        next_state = current_state.get_next_state(token)

        """Panic mode is handled below. It does not work well..."""
        if next_state is None:  # panic mode
            if token is None:
                return False, accepted, parsed
            print(current_state.name, ",", token, "->", "Panic!")
            dumped_input = ""
            dumped_input += token
            token = get_next_token()
            if len(STACK) > 0:
                last_item_in_stack = STACK.pop()
                while token not in last_item_in_stack[2].follow and token is not None:
                    dumped_input += token
                    token = get_next_token()
                #next_state = last_item_in_stack
                #accepted += token
                #token = get_next_token()
            else:
                return False, accepted, parsed
            print("dumped input:", dumped_input)
            continue
            #return False, accepted, parsed

        print(current_state.name, ",", token, "->", next_state[0].name, end=" ")
        current_state.call_functions()
        current_state, is_edge_terminal = next_state[0], next_state[1]
        if is_edge_terminal == True:  # shift
            if token != "EOF":
                accepted += token
            token = get_next_token()
        print("accepted:", accepted)


token = ""


def get_next_token():
    if token == "EOF" or token is None:
        return None
    return SCANNER.get_next_token().token_type

token = get_next_token()


s0 = State("S0")
s1 = State("S1")
s2 = State("S2")
s3 = State("S3")
s4 = State("S4")
s5 = State("S5")
s6 = State("S6")
s7 = State("S7")
s8 = State("S8")
s9 = State("S9")
s10 = State("S10")
s11 = State("S11")
s12 = State("S12")
s13 = State("S13")
s14 = State("S14")
s15 = State("S15")
s16 = State("S16")
s17 = State("S17")

start = State("start")
mid1 = State("mid1")
final = State("final")


E_diagram = Diagram(s0, s2)
E1_diagram = Diagram(s3, s6)
T_diagram = Diagram(s7, s9)
T1_diagram = Diagram(s10, s13)
F_diagram = Diagram(s14, s17)
S_diagram = Diagram(start, final)

E = NonTerminal("E", ["(", "ID"], ["EOF", ")"], E_diagram)
E1 = NonTerminal("E1", ["+", EPSILON], ["EOF", ")"], E1_diagram)
T = NonTerminal("T", ["(", "ID"], ["+", "EOF", ")"], T_diagram)
T1 = NonTerminal("T1", ["*", EPSILON], ["+", "EOF", ")"], T1_diagram)
F = NonTerminal("F", ["(", "ID"], ["+", "*", "EOF", ")"], F_diagram)
S = NonTerminal("S", ["(", "ID"], ["EOF"], S_diagram)

STACK.append((start, True, Terminal("start")))

s0.set_next_state(T, s1)
s1.set_next_state(E1, s2)
s3.set_next_state("+", s4)
s3.set_next_state(EPSILON, s6)
s4.set_next_state(T, s5)
s5.set_next_state(E1, s6)
s7.set_next_state(F, s8)
s8.set_next_state(T1, s9)
s10.set_next_state("*", s11)
s10.set_next_state(EPSILON, s13)
s11.set_next_state(F, s12)
s12.set_next_state(T1, s13)
s14.set_next_state("(", s15)
s14.set_next_state("ID", s17)
s15.set_next_state(E, s16)
s16.set_next_state(")", s17)

start.set_next_state(E, mid1)
mid1.set_next_state(Terminal("EOF"), final)

flag, accepted, parsed = parse(start, final)
print("accepted:", accepted)
