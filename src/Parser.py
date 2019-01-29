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
        epsilons_added_indexes = []
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
                        epsilons_added_indexes.append(len(next_states))
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

        if len(next_states) > 1:
            non_epsilon_states = []
            for i in range(len(next_states)):
                if i not in epsilons_added_indexes:
                    non_epsilon_states.append(next_states[i])

            if len(non_epsilon_states) == 1:
                return non_epsilon_states[0]


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


# <editor-fold desc="Declaring States">
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
s18 = State("S18")
s19 = State("S19")
s20 = State("S20")
s21 = State("S21")
s22 = State("S22")
s23 = State("S23")
s24 = State("S24")
s25 = State("S25")
s26 = State("S26")
s27 = State("S27")
s28 = State("S28")
s29 = State("S29")
s30 = State("S30")
s31 = State("S31")
s32 = State("S32")
s33 = State("S33")
s34 = State("S34")
s35 = State("S35")
s36 = State("S36")
s37 = State("S37")
s38 = State("S38")
s39 = State("S39")
s40 = State("S40")
s41 = State("S41")
s42 = State("S42")
s43 = State("S43")
s44 = State("S44")
s45 = State("S45")
s46 = State("S46")
s47 = State("S47")
s48 = State("S48")
s49 = State("S49")
s50 = State("S50")
s51 = State("S51")
s52 = State("S52")
s53 = State("S53")
s54 = State("S54")
s55 = State("S55")
s56 = State("S56")
s57 = State("S57")
s58 = State("S58")
s59 = State("S59")
s60 = State("S60")
s61 = State("S61")
s62 = State("S62")
s63 = State("S63")
s64 = State("S64")
s65 = State("S65")
s66 = State("S66")
s67 = State("S67")
s68 = State("S68")
s69 = State("S69")
s70 = State("S70")
s71 = State("S71")
s72 = State("S72")
s73 = State("S73")
s74 = State("S74")
s75 = State("S75")
s76 = State("S76")
s77 = State("S77")
s78 = State("S78")
s79 = State("S79")
s80 = State("S80")
s81 = State("S81")
s82 = State("S82")
s83 = State("S83")
s84 = State("S84")
s85 = State("S85")
s86 = State("S86")
s87 = State("S87")
s88 = State("S88")
s89 = State("S89")
s90 = State("S90")
s91 = State("S91")
s92 = State("S92")
s93 = State("S93")
s94 = State("S94")
s95 = State("S95")
s96 = State("S96")
s97 = State("S97")
s98 = State("S98")
s99 = State("S99")
s100 = State("S100")
s101 = State("S101")
s102 = State("S102")
s103 = State("S103")
s104 = State("S104")
s105 = State("S105")
s106 = State("S106")
s107 = State("S107")
s108 = State("S108")
s109 = State("S109")
s110 = State("S110")
s111 = State("S111")
s112 = State("S112")
s113 = State("S113")
s114 = State("S114")
s115 = State("S115")
s116 = State("S116")
s117 = State("S117")
s118 = State("S118")
s119 = State("S119")
s120 = State("S120")
s121 = State("S121")
s122 = State("S122")
s123 = State("S123")
s124 = State("S124")

start = State("start")
mid1 = State("mid1")
final = State("final")
# </editor-fold>

# <editor-fold desc="Setting Functions">
s4.func_names = ["save_value_type"]
s5.func_names = ["save_variable_name"]
s6.func_names = ["save_variable_type"]
s9.func_names = ["allocate_array"]
s23.func_names = ["add_parameter"]
s25.func_names = ["update_parameter_type"]
s27.func_names = ["time_to_change_blocks"]
s30.func_names = ["time_to_revert_blocks"]
s36.func_names = ["check_declared_id", "check_id_is_int_for_output"]
s40.func_names = ["entering_while"]
s53.func_names = ["exiting_while"]
s62.func_names = ["entering_switch"]
s65.func_names = ["exiting_switch"]
s34.func_names = ["check_valid_break_continue"]
s55.func_names = ["check_return_type"]
s78.func_names = ["check_declared_id", "save_id_for_check"]
s123.func_names = ["add_argument"]
s124.func_names = ["close_arguments"]
s95.func_names = ["check_array_index"]
s96.func_names = ["remove_id_from_ss"]
s96.func_names = ["remove_id_from_ss"]
s90.func_names = ["check_declared_id", "save_id_for_check"]
s115.func_names = ["check_declared_id", "save_id_for_check"]
# </editor-fold>

# <editor-fold desc="Declaring Diagrams">
program_diagram = Diagram(s1, s3)
dec_diagram = Diagram(s4, s7)
var_dec_diagram = Diagram(s8, s12)
fun_dec_diagram = Diagram(s13, s17)
params_diagram = Diagram(s18, s21)
param_diagram = Diagram(s22, s26)
comp_stmt_diagram = Diagram(s27, s31)
stmt_diagram = Diagram(s32, s33)
expr_stmt_diagram = Diagram(s34, s39)
select_stmt_diagram = Diagram(s41, s48)
iter_stmt_diagram = Diagram(s49, s53)
return_stmt_diagram = Diagram(s54, s57)
switch_stmt_diagram = Diagram(s58, s66)
case_stmts_diagram = Diagram(s67, s68)
case_stmt_diagram = Diagram(s69, s73)
default_diagram = Diagram(s74, s77)
expr_diagram = Diagram(s78, s84)
var_diagram = Diagram(s90, s92)
list_index_diagram = Diagram(s93, s96)
simple_expr_diagram = Diagram(s97, s99)
simple_expr1_diagram = Diagram(s100, s102)
add_expr_diagram = Diagram(s103, s105)
add_expr1_diagram = Diagram(s106, s108)
term_diagram = Diagram(s109, s111)
term1_diagram = Diagram(s112, s114)
factor_diagram = Diagram(s115, s118)
args_diagram = Diagram(s122, s124)

S_diagram = Diagram(start, final)
# </editor-fold>

# <editor-fold desc="Declaring NonTerminals">
add_expr = NonTerminal("add_expr", ['(', 'NUM', 'ID'], ['<', '==', ',', ')', ']', ';'], add_expr_diagram)
add_expr1 = NonTerminal("add_expr1", [EPSILON, '+', '-'], ['<', '==', ',', ')', ']', ';'], add_expr1_diagram)
args = NonTerminal("args", [EPSILON, 'ID', '(', 'NUM'], [')'], args_diagram)
case_stmt = NonTerminal("case_stmt", ['case'], ['case', 'ID', '(', 'NUM', 'default'], case_stmt_diagram)
case_stmts = NonTerminal("case_stmts", [EPSILON, 'case'], ['ID', '(', 'NUM', 'default'], case_stmts_diagram)
comp_stmt = NonTerminal("comp_stmt", ['{'], ['else', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', 'int', 'void', 'EOF', '}', 'case', 'default'], comp_stmt_diagram)
dec = NonTerminal("dec", ['int', 'void'], ['int', 'void', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', 'EOF'], dec_diagram)
default = NonTerminal("default", ['default', EPSILON], ['}'], default_diagram)
expr = NonTerminal("expr", ['ID', '(', 'NUM'], [',', ')', ']', ';'], expr_diagram)
expr_stmt = NonTerminal("expr_stmt", ['continue', 'break', ';', 'ID', '(', 'NUM'], ['else', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', '}', 'case', 'default'], expr_stmt_diagram)
factor = NonTerminal("factor", ['(', 'NUM', 'ID'], ['*', '+', '-', '<', '==', ',', ')', ']', ';'], factor_diagram)
fun_dec = NonTerminal("fun_dec", ['('], ['int', 'void', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', 'EOF'], fun_dec_diagram)
iter_stmt = NonTerminal("iter_stmt", ['while'], ['else', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', '}', 'case', 'default'], iter_stmt_diagram)
list_index = NonTerminal("list_index", ['[', EPSILON], ['=', '*', '+', '-', '<', '==', ',', ')', ']', ';'], list_index_diagram)
param = NonTerminal("param", ['int', 'void'], [',', ')'], param_diagram)
params = NonTerminal("params", ['void', 'int'], [')'], params_diagram)
program = NonTerminal("program", ['EOF', EPSILON, 'int', 'void'], ['EOF'], program_diagram)
return_stmt = NonTerminal("return_stmt", ['return'], ['else', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', '}', 'case', 'default'], return_stmt_diagram)
select_stmt = NonTerminal("select_stmt", ['if'], ['else', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', '}', 'case', 'default'], select_stmt_diagram)
simple_expr = NonTerminal("simple_expr", ['(', 'NUM', 'ID'], [',', ')', ']', ';'], simple_expr_diagram)
simple_expr1 = NonTerminal("simple_expr1", [EPSILON, '<', '=='], [',', ')', ']', ';'], simple_expr1_diagram)
stmt = NonTerminal("stmt", ['continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while'], ['else', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', '}', 'case', 'default'], stmt_diagram)
switch_stmt = NonTerminal("switch_stmt", ['switch'], ['else', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', '}', 'case', 'default'], switch_stmt_diagram)
term = NonTerminal("term", ['(', 'NUM', 'ID'], ['+', '-', '<', '==', ',', ')', ']', ';'], term_diagram)
term1 = NonTerminal("term1", ['*', EPSILON], ['+', '-', '<', '==', ',', ')', ']', ';'], term1_diagram)
var = NonTerminal("var", ['ID'], ['=', '*', '+', '-', '<', '==', ',', ')', ']', ';'], var_diagram)
var_dec = NonTerminal("var_dec", ['[', ';'], ['int', 'void', 'continue', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'switch', 'while', 'EOF'], var_dec_diagram)

# </editor-fold>

STACK.append((start, True, Terminal("start")))

# <editor-fold desc="Setting Edges on Diagrams">
s1.set_next_state(dec, s1)
s1.set_next_state(EPSILON, s2)
s2.set_next_state("EOF", s3)
s4.set_next_state("int", s5)
s4.set_next_state("void", s5)
s5.set_next_state("ID", s6)
s6.set_next_state(var_dec, s7)
s6.set_next_state(fun_dec, s7)
s8.set_next_state("[", s9)
s8.set_next_state(";", s12)
s9.set_next_state("NUM", s10)
s10.set_next_state("]", s11)
s11.set_next_state(";", s12)
s13.set_next_state("(", s14)
s14.set_next_state(params, s15)
s15.set_next_state(")", s16)
s16.set_next_state(comp_stmt, s17)
s18.set_next_state(param, s19)
s18.set_next_state("void", s21)
s19.set_next_state(EPSILON, s21)
s19.set_next_state(";", s20)
s20.set_next_state(param, s19)
s22.set_next_state("int", s23)
s23.set_next_state("ID", s24)
s24.set_next_state(EPSILON, s26)
s24.set_next_state("[", s25)
s25.set_next_state("]", s26)
s27.set_next_state("{", s28)
s28.set_next_state(dec, s28)
s28.set_next_state(EPSILON, s29)
s29.set_next_state(stmt, s29)
s29.set_next_state(EPSILON, s30)
s30.set_next_state("}", s31)
s32.set_next_state(expr_stmt, s33)
s32.set_next_state(comp_stmt, s33)
s32.set_next_state(select_stmt, s33)
s32.set_next_state(iter_stmt, s33)
s32.set_next_state(return_stmt, s33)
s32.set_next_state(switch_stmt, s33)
s34.set_next_state(expr, s38)
s34.set_next_state("continue", s38)
s34.set_next_state("break", s38)
s34.set_next_state(EPSILON, s38)
s34.set_next_state("output", s35)
s35.set_next_state("(", s36)
s36.set_next_state("ID", s37)
s37.set_next_state(")", s38)
s38.set_next_state(";", s39)
s41.set_next_state("if", s42)
s42.set_next_state("(", s43)
s43.set_next_state(expr, s44)
s44.set_next_state(")", s45)
s45.set_next_state(stmt, s46)
s46.set_next_state("else", s47)
s47.set_next_state(stmt, s48)
s49.set_next_state("while", s50)
s50.set_next_state("(", s51)
s51.set_next_state(expr, s52)
s52.set_next_state(")", s40)
s40.set_next_state(stmt, s53)
s54.set_next_state("return", s55)
s55.set_next_state(expr, s56)
s55.set_next_state(EPSILON, s56)
s56.set_next_state(";", s57)
s58.set_next_state("switch", s59)
s59.set_next_state("(", s60)
s60.set_next_state(expr, s61)
s61.set_next_state(")", s62)
s62.set_next_state("{", s63)
s63.set_next_state(case_stmts, s64)
s64.set_next_state(default, s65)
s65.set_next_state("}", s66)
s67.set_next_state(case_stmt, s67)
s67.set_next_state(EPSILON, s68)
s69.set_next_state("case", s70)
s70.set_next_state("NUM", s71)
s71.set_next_state(":", s72)
s72.set_next_state(stmt, s72)
s72.set_next_state(EPSILON, s73)
s74.set_next_state("default", s75)
s74.set_next_state(EPSILON, s77)
s75.set_next_state(":", s76)
s76.set_next_state(stmt, s76)
s76.set_next_state(EPSILON, s77)
s78.set_next_state("(", s79)
s78.set_next_state("NUM", s81)
s78.set_next_state("ID", s85)
s79.set_next_state(expr, s80)
s80.set_next_state(")", s81)
s81.set_next_state(term1, s82)
s82.set_next_state(add_expr1, s83)
s83.set_next_state(simple_expr1, s84)
s85.set_next_state("(", s86)
s85.set_next_state(list_index, s88)
s86.set_next_state(args, s87)
s87.set_next_state(")", s81)
s88.set_next_state(term1, s82)
s88.set_next_state("=", s89)
s89.set_next_state(expr, s84)
s90.set_next_state("ID", s91)
s91.set_next_state(list_index, s92)
s93.set_next_state("[", s94)
s93.set_next_state(EPSILON, s96)
s94.set_next_state(expr, s95)
s95.set_next_state("]", s96)
s97.set_next_state(add_expr, s98)
s98.set_next_state(simple_expr1, s99)
s100.set_next_state("<", s101)
s100.set_next_state("==", s101)
s100.set_next_state(term1, s102)
s101.set_next_state(add_expr, s102)
s103.set_next_state(term, s104)
s104.set_next_state(add_expr1, s105)
s106.set_next_state("+", s107)
s106.set_next_state("-", s107)
s106.set_next_state(EPSILON, s108)
s107.set_next_state(term, s106)
s109.set_next_state(factor, s110)
s110.set_next_state(term1, s111)
s112.set_next_state("*", s113)
s112.set_next_state(EPSILON, s114)
s113.set_next_state(factor, s112)
s115.set_next_state("(", s116)
s115.set_next_state("NUM", s118)
s115.set_next_state("ID", s119)
s116.set_next_state(expr, s117)
s117.set_next_state(")", s118)
s119.set_next_state("(", s120)
s119.set_next_state(list_index, s118)
s120.set_next_state(args, s121)
s121.set_next_state(")", s118)
s122.set_next_state(expr, s123)
s122.set_next_state(EPSILON, s124)
s123.set_next_state(",", s122)
s123.set_next_state(EPSILON, s124)




start.set_next_state(program, mid1)
mid1.set_next_state(Terminal("EOF"), final)
# </editor-fold>

flag, accepted, parsed = parse(start, final)
print("accepted:", accepted)
