from rat26s_lexer import lexer, Token

tokens = []
index = 0
current_token = None
print_switch = True # turn on/off production printing

def next_token():
    global index, current_token
    if index < len(tokens):
        current_token = tokens[index]
        index += 1
    else:
        current_token = Token('EOF', 'EOF')

# Helper Functions

def error(expected):
    print(f"Syntax Error: Expected {expected}, got Token: {current_token.token_type}, Lexeme: '{current_token.lexeme}'")
    exit(1)

def match(expected_type=None, expected_lexeme=None):
    global current_token
    
    if current_token.token_type == "unknown":
        error("valid token")

    print(f"Token: {current_token.token_type:<12} Lexeme: {current_token.lexeme}")

    if expected_type and current_token.token_type != expected_type:
        error(expected_type)

    if expected_lexeme and current_token.lexeme != expected_lexeme:
        error(expected_lexeme)

    next_token()

# Grammar Rules

def Statement():
    if print_switch:
        print("<Statement> -> <Assign>")
    Assign()

def Assign():
    if print_switch:
        print("<Assign> -> <Identifier> = <Expression> ;")

    if current_token.token_type == "identifier":
        match("identifier")
        match("operator", "=")
        Expression()
        match("separator", ";")
    else:
        error("identifier")

def Expression():
    if print_switch:
        print("<Expression> -> <Term> <Expression Prime>")
    Term()
    ExpressionPrime()

def ExpressionPrime():
    if current_token.lexeme in ["+", "-"]:
        if print_switch:
            print("<Expression Prime> -> + | - <Term> <Expression Prime>")
        op = current_token.lexeme
        match ("operator", op)
        Term()
        ExpressionPrime()
    else: 
        if print_switch:
            print("<Expression Prime> -> Epsilon")

def Term():
    if print_switch:
        print("<Term> -> <Factor> <Term Prime>")
    Factor()
    TermPrime()

def TermPrime():
    if current_token.lexeme in ["*", "/"]:
        if print_switch:
            print("<Term Prime> -> * | / <Factor> <Term Prime>")
        op = current_token.lexeme
        match("operator", op)
        Factor()
        TermPrime()
    else:
        if print_switch:
            print("<Term Prime> -> Epsilon")

def Factor():
    if current_token.token_type == "identifier":
        if print_switch:
            print("<Factor> -> <Identifier>")
        match("identifier")
    
    elif current_token.token_type in ["integer", "real"]:
        if print_switch:
            print("<Factor> -> <Number>")
        match(current_token.token_type)
    
    elif current_token.lexeme == "(":
        if print_switch:
            print("<Factor> -> ( <Expression> )")
        match("separator", "(")
        Expression()
        match("separator", ")")

    else:
        error("identifier, number, or (")

def StatementList():
    if print_switch:
        print("<StatementList> -> <Statement> <StatementList> | Epsilon")

    while current_token.token_type != "EOF":
        Statement()

# Main

def main():
    global tokens

    input_file = input("Enter input file: ")

    try:
        with open(input_file, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print("File not found.")
        return

    tokens = lexer(source)

    next_token()
    StatementList()

    if current_token.token_type != "EOF":
        error("EOF")
    
    print("\nParsing Complete - No Syntax Errors!")

if __name__=="__main__":
    main()