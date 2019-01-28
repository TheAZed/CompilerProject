from src.Scanner import Scanner, Block


class Librarian:
    def __init__(self, scanner):
        """

        :param scanner:
        :type scanner: Scanner
        """
        self.program_index = 0
        self.scanner = scanner
        self.functions = {"load_next_token": self.load_next_token}
        self.code_generator = CodeGenerator(scanner, self)
        self.children = [self.code_generator]

    def call_func(self, func_name):
        if func_name in self.functions:
            self.functions[func_name]()
            return True
        for child in self.children:
            if child.call_func(func_name):
                return True
        return False

    def load_next_token(self):
        self.scanner.get_next_token()


class CodeGenerator:

    def __init__(self, scanner, librarian):
        """

        :param scanner:
        :type scanner: Scanner
        :param librarian:
        :type librarian: Librarian
        """
        self.ss = []
        self.scanner = scanner
        self.functions = {}
        self.parent = librarian
        self.code_index = 0

    def call_func(self, func_name):
        """
        Call a function by getting its name
        :param func_name:
        :type func_name: str
        :return:
        :rtype: bool
        """
        if func_name in self.functions:
            self.functions[func_name]()
            return True
        return False


class SemanticChecker:
    def __init__(self, scanner, librarian):
        """

        :param scanner:
        :type scanner: Scanner
        :param librarian:
        :type librarian: Librarian
        """
        self.ss = []
        self.scanner = scanner
        self.functions = {}
        self.parent = librarian

    def generate_first_block(self):
        first_block = Block(0, None)
        self.scanner.current_block = first_block

    def save_value_type(self):
        self.ss.append(self.scanner.current_token.string)

    def save_variable_name(self):
        self.ss.append(self.scanner.current_token.string)

    def save_variable_type(self):
        next_str = self.scanner.current_token.string
        variable = self.scanner.current_block.find_variable(self.ss[-1])
        if next_str == ';':
            variable.value_type = self.ss[-2]
            variable.value = 0
            variable.var_type = "var"
            self.ss.pop()
            self.ss.pop()
        elif next_str == '[':
            variable.var_type = "array"
            variable.value_type = self.ss[-2]
            # Should free some space later and save the pointer in value
        elif next_str == '(':
            variable.var_type = "func"
            variable.value_type = self.ss[-2]
            # assigning pointer to the function as the value
            # FIXME: Might need to indent current code_index
            variable.value = self.parent.code_generator.code_index


