from src.Scanner import Scanner

scanner = Scanner("ScannerTest.txt")
current_token = scanner.get_next_token()
while current_token.string != "EOF":
    print(current_token.string + " " + current_token.token_type)
    current_token = scanner.get_next_token()
