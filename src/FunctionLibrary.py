from src import ErrorMaster
from src.Scanner import Scanner, Block, Variable, FunctionVariable, ArrayVariable


class Librarian:
    def __init__(self, scanner):
        """

        :param scanner:
        :type scanner: Scanner
        """
        self.program_index = 0
        self.scanner = scanner
        self.functions = {"load_next_token": self.load_next_token}
        self.block = Block(0, None)
        self.code_generator = CodeGenerator(scanner, self)
        self.semantic_checker = SemanticChecker(scanner, self)
        self.children = [self.code_generator, self.semantic_checker]
        self.set_block(self.block)

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

    def set_block(self, block):
        self.scanner.current_block = block
        self.block = block
        for child in self.children:
            child.block = block


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
        self.block = librarian.block

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
        self.functions = {"save_value_type": self.save_value_type,
                          "save_variable_name": self.save_variable_name,
                          "save_variable_type": self.save_variable_type,
                          "allocate_array": self.allocate_array,
                          "add_parameter": self.add_parameter,
                          "update_parameter_type": self.update_parameter_type,
                          "time_to_change_blocks": self.time_to_change_blocks,
                          "time_to_revert_blocks": self.time_to_revert_blocks,
                          "check_declared_id": self.check_declared_id,
                          "check_id_is_int_for_output": self.check_id_is_int_for_output,
                          "entering_while": self.entering_while,
                          "exiting_while": self.exiting_while,
                          "entering_switch": self.entering_switch,
                          "exiting_switch": self.exiting_switch,
                          "check_valid_break_continue": self.check_valid_break_continue,
                          "check_return_type": self.check_return_type,
                          "save_id_for_check": self.save_id_for_check,
                          "add_argument": self.add_argument,
                          "close_arguments": self.close_arguments,
                          "check_array_index": self.check_array_index,
                          "remove_id_from_ss": self.remove_id_from_ss,

                          }
        self.parent = librarian
        self.block = librarian.block
        self.while_depth = 0
        self.switch_depth = 0

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

    def save_value_type(self):
        self.ss.append(self.scanner.current_token.string)

    def save_variable_name(self):  # and add variable to current_block
        next_str = self.scanner.current_token.string
        self.ss.append(next_str)

    def save_variable_type(self):
        next_str = self.scanner.current_token.string
        possible_variable = self.block.find_variable(self.ss[-1])
        if possible_variable is not None:
            if possible_variable.block == self.block:
                ErrorMaster.add_error("Semantic", next_str + " is already declared in this scope!")
                return
        if next_str == ';':
            variable = Variable(self.scanner.previous_token, "", self.block)
            self.block.static_variables.append(variable)
            variable.value_type = self.ss[-2]
            variable.value = 0
            variable.var_type = "var"
            self.ss.pop()
            self.ss.pop()
        elif next_str == '[':
            variable = ArrayVariable(self.scanner.previous_token, "", self.block)
            self.block.static_variables.append(variable)
            variable.var_type = "array"
            variable.value_type = self.ss[-2]
            self.ss.append(variable)
            # Should free some space later and save the pointer in value
        elif next_str == '(':
            variable = FunctionVariable(self.scanner.previous_token, "", self.block)
            self.block.static_variables.append(variable)
            variable.var_type = "func"
            variable.value_type = self.ss[-2]
            # assigning pointer to the function as the value
            # FIXME: Might need to indent current code_index
            variable.value = self.parent.code_generator.code_index
            self.ss.append(variable)
            # new_block = Block(self.scanner.current_block.level + 1, self.scanner.current_block, variable.token)
            # self.scanner.current_block = new_block

    def allocate_array(self):
        next_str = self.scanner.current_token.string
        array_len = int(next_str)
        variable = self.ss.pop()
        variable.length = array_len
        variable.value = len(self.block.heap)
        for i in range(array_len):
            new_var = Variable(None, "var", self.block, variable.value_type)
            self.block.heap.append(new_var)
        self.ss.pop()
        self.ss.pop()

    def add_parameter(self):
        type_str = self.scanner.previous_token.string
        variable = Variable(self.scanner.current_token, "var", None, type_str)
        self.ss[-1].parameters.append(variable)

    def update_parameter_type(self):
        variable = self.ss[-1].parameters[-1]
        variable.var_type = "array"

    def time_to_change_blocks(self):
        if type(self.ss[-1] == FunctionVariable):
            func_var = self.ss[-1]
            self.ss.pop()
            new_block = Block(self.block.level + 1, self.block, func_var)
            for param in func_var.parameters:
                param.block = new_block
                new_block.static_variables.append(param)
        else:
            new_block = Block(self.block.level + 1, self.block)
        self.parent.set_block(new_block)

    def time_to_revert_blocks(self):
        if self.block.func_var is not None:
            self.ss.pop()
            self.ss.pop()
        self.parent.set_block(self.block.parent_block)

    def check_declared_id(self):
        if self.scanner.current_token.token_type != "ID":
            return
        next_str = self.scanner.current_token.string
        possible_var = self.block.find_variable(next_str)
        if possible_var is None:
            ErrorMaster.add_error("Semantic", "Using variable " + next_str + " without declaration")

    def check_id_is_int_for_output(self):
        next_str = self.scanner.current_token.string
        possible_var = self.block.find_variable(next_str)
        if possible_var is not None and possible_var.value_type != "int":
            ErrorMaster.add_error("Semantic", "Cannot print void variable " + next_str)

    def entering_while(self):
        self.while_depth += 1

    def exiting_while(self):
        self.while_depth -= 1

    def entering_switch(self):
        self.switch_depth += 1
        new_block = Block(self.block.level + 1, self.block)
        self.parent.set_block(new_block)

    def exiting_switch(self):
        self.switch_depth -= 1
        self.parent.set_block(self.block.parent_block)

    def check_valid_break_continue(self):
        next_str = self.scanner.current_token.string
        if next_str == "break" and self.switch_depth + self.while_depth <= 0:
            ErrorMaster.add_error("Semantic", "invalid break out of a while or switch")
        elif next_str == "continue" and self.while_depth <= 0:
            ErrorMaster.add_error("Semantic", "invalid continue out of a while loop")

    def check_return_type(self):
        next_str = self.scanner.current_token.string
        if next_str == ";" and self.ss[-2] != "void":
            ErrorMaster.add_error("Semantic", "Function " + self.ss[-1] + " needs a return value")
        self.ss.pop()
        self.ss.pop()

    def save_id_for_check(self):
        if self.scanner.current_token.token_type == "ID":
            variable = self.block.find_variable(self.scanner.current_token.string)
            # if variable.value_type == "void":
            #     ErrorMaster.add_error("Semantic", "Can't use a void variable in expressions")
            #     return
            if type(variable) == FunctionVariable:
                self.ss.append(0)
            self.ss.append(variable)

    def add_argument(self):
        if type(self.ss[-1]) != FunctionVariable:
            ErrorMaster.add_error("Semantic", "Variable " + self.ss[-1].token.string + " is not a function")
            return
        if self.ss[-2] >= len(self.ss[-1].parameters):
            ErrorMaster.add_error("Semantic", "Too many arguments for " + self.ss[-1].token.string)
        else:
            self.ss[-2] += 1
            # TODO set parameter value

    def close_arguments(self):
        if self.ss[-2] < len(self.ss[-1].parameters):
            ErrorMaster.add_error("Semantic", "Not enough arguments for " + self.ss[-1].token.string)
        self.ss.pop()
        self.ss.pop()

    def check_array_index(self):
        if type(self.ss[-1]) != ArrayVariable:
            ErrorMaster.add_error("Semantic", "Variable " + self.ss[-1].token.string + " is not an array")
        number = self.parent.code_generator.ss[-1]
        if number < 0 or number >= self.ss[-1].array_len:
            ErrorMaster.add_error("Semantic", "Array index out of range for " + self.ss[-1].token.string)

    def remove_id_from_ss(self):
        self.ss.pop()
