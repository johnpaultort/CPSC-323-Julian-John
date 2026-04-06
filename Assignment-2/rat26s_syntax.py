from rat26s_lexer import lexer, Token

tokens = []
index = 0
current_token = None
print_switch = True # turn on/off production printing
output_file = None

def write(line):
    output_file.write(line + "\n")

def next_token():
    global index, current_token
    if index < len(tokens):
        current_token = tokens[index]
        index += 1
    else:
        current_token = Token('EOF', 'EOF')

# Helper Functions

def error(expected):
    write(f"Syntax Error: Expected {expected}, got Token: {current_token.token_type}, Lexeme: '{current_token.lexeme}'")
    output_file.close()
    exit(1)

def match(expected_type=None, expected_lexeme=None):
    global current_token
    
    if current_token.token_type == "unknown":
        error("valid token")

    write(f"Token: {current_token.token_type:<12} Lexeme: {current_token.lexeme}")

    if expected_type and current_token.token_type != expected_type:
        error(expected_type)

    if expected_lexeme and current_token.lexeme != expected_lexeme:
        error(expected_lexeme)

    next_token()

# Grammar Rules

def StatementList():
    if print_switch:
        write("<StatementList> -> <Statement> <StatementList> | <Epsilon>")
    
    while current_token.token_type != "EOF":
        Statement()

def Statement():
    if print_switch:
        write("<Statement> -> <Assign>")
        Assign()

def Assign():
    if print_switch:
        write("<Assign> -> <Identifier> = <Expression> ;")

    if current_token.token_type == "identifier":
        match("identifier")
        match("operator", "=")
        Expression()
        match("separator", ";")
    else:
        error("identifier")

def Expression():
    if print_switch:
        write("<Expression> -> <Term> <Expression Prime>")
    Term()
    ExpressionPrime()

def ExpressionPrime():
    if current_token.lexeme in ["+", "-"]:
        if print_switch:
            write("<Expression Prime> -> + <Term> <Expression Prime> | - <Term> <Expression Prime>")

        op = current_token.lexeme
        match ("operator", op)
        Term()
        ExpressionPrime()
    else: 
        if print_switch:
            write("<Expression Prime> -> Epsilon")

def Term():
    if print_switch:
        write("<Term> -> <Factor> <Term Prime>")
    Factor()
    TermPrime()

def TermPrime():
    if current_token.lexeme in ["*", "/"]:
        if print_switch:
            write("<Term Prime> -> * | / <Factor> <Term Prime>")

        op = current_token.lexeme
        match("operator", op)
        Factor()
        TermPrime()
    else:
        if print_switch:
            write("<Term Prime> -> Epsilon")

def Factor():
    if current_token.token_type == "identifier":
        if print_switch:
            write("<Factor> -> <Identifier>")
        match("identifier")
    
    elif current_token.token_type in ["integer", "real"]:
        if print_switch:
            write("<Factor> -> <Number>")
        match(current_token.token_type)
    
    elif current_token.lexeme == "(":
        if print_switch:
            write("<Factor> -> ( <Expression> )")
        match("separator", "(")
        Expression()
        match("separator", ")")

    else:
        error("identifier, number, or (")

# Main

def main():
    global tokens, output_file

    input_file = input("Enter input file: ")
    output_name = "output_" + input_file

    try:
        with open(input_file, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print("File not found.")
        return

    tokens = lexer(source)

    output_file = open(output_name, "w")

    next_token()
    StatementList()

    if current_token.token_type != "EOF":
        error("EOF")
    
    write("\nParsing Complete - No Syntax Errors!")
    output_file.close()

    print(f"Output written to {output_name}")

if __name__=="__main__":
    main()