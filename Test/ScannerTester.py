from src.Scanner import Scanner, Block

scanner = Scanner("ScannerTest.txt")
first_block = Block(0, None)
scanner.current_block = first_block
current_token = scanner.get_next_token()
while current_token.string != "EOF":
    print(current_token.string + " " + current_token.token_type)
    current_token = scanner.get_next_token()
