error_list = []


def show_all_errors():
    for error in error_list:
        print(error.error_msg)


class Error:
    def __init__(self, error_type, error_msg):
        """

        :param error_type:
        :type error_type: str
        :param error_msg:
        :type error_msg: str
        """
        self.error_type = error_type
        self.error_msg = error_msg
