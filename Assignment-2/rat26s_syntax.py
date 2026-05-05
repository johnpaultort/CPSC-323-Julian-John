from rat26s_lexer import lexer, Token

#
# Global Variables
#

tokens = []             # List of all tokens from lexer
index = 0               # Index of current token
current_token = None    # Current analzyed token
print_switch = True     # turn on/off production printing
output_file = None      # File for output

def write(line):
    output_file.write(line + "\n")

def next_token():
    # Advance to the next token, else EOF
    global index, current_token
    if index < len(tokens):
        current_token = tokens[index]
        index += 1
    else:
        current_token = Token('EOF', 'EOF')

#
# Helper Functions
#

def error(expected):
    # Print a syntax error and exit
    # Shows expected token
    write(f"Syntax Error: Expected {expected}, got Token: {current_token.token_type}, Lexeme: '{current_token.lexeme}'")
    output_file.close()
    exit(1)

def match(expected_type=None, expected_lexeme=None):
    # Match current token to either expected type or lexeme
    global current_token
    
    # Check if valid token
    if current_token.token_type == "unknown":
        error("valid token")

    # Print token/lexme to output_...
    write(f"Token: {current_token.token_type:<12} Lexeme: {current_token.lexeme}")

    # Checks for token type
    if expected_type and current_token.token_type != expected_type:
        error(expected_type)

    # Check for expected lexeme
    if expected_lexeme and current_token.lexeme != expected_lexeme:
        error(expected_lexeme)

    # Moves to next token
    next_token()

def print_rule(rule):
    if print_switch:
        write(f"   {rule}")

#
# Grammar Rules
#

# R1
def Rat26s():
    print_rule("<Rat26s> -> @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @")
    match("separator", "@")
    OptFunctionDefinitions()
    match("separator", "@")
    OptDeclarationList()
    match("separator", "@")
    StatementList()
    match("separator", "@")

# R2
def OptFunctionDefinitions():
    print_rule("<Opt Function Definitions> -> <Function Definitions> | <Empty>")
    if current_token.lexeme == "function":
        FunctionDefinitions()
    else:
        Empty()

# R3
def FunctionDefinitions():
    print_rule("<Function Definitions> -> <Function> | <Function> <Function Definitions>")
    Function()
    if current_token.lexeme == "function":
        FunctionDefinitions()

# R4
def Function():
    print_rule("<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
    match("keyword", "function")
    match("identifier")
    match("separator", "(")
    OptParameterList()
    match("separator", ")")
    OptDeclarationList()
    Body()

# R5
def OptParameterList():
    print_rule("<Opt Parameter List> -> <Parameter List> | <Empty>")
    if current_token.token_type == "identifier":
        ParameterList()
    else:
        Empty()

# R6
def ParameterList():
    print_rule("<Parameter List> -> <Parameter> | <Parameter>, <Parameter List>")
    Parameter()
    if current_token.lexeme == ",":
        match("separator", ",")
        ParameterList()

# R7
def Parameter():
    print_rule("<Parameter> -> <IDs> <Qualifier>")
    IDs()
    Qualifier()

# R8
def Qualifier():
    print_rule("<Qualifier> -> integer | boolean | real")
    if current_token.lexeme in ["integer", "boolean", "real"]:
        match("keyword")
    else:
        error("integer, boolean, or real")

# R9
def Body():
    print_rule("<Body> -> { <Statement List> }")
    match("separator", "{")
    StatementList()
    match("separator", "}")

# R10
def OptDeclarationList():
    print_rule("<Opt Declaration List> -> <Declaration List> | <Empty>")
    if current_token.lexeme in ["integer", "boolean", "real"]:
        DeclarationList()
    else:
        Empty()
    
# R11
def DeclarationList():
    print_rule("<Declaration List> -> <Declaration> ; | <Declaration> ; <Declaration List>")
    Declaration()
    match("separator", ";")
    if current_token.lexeme in ["integer", "boolean", "real"]:
        DeclarationList()

# R12
def Declaration():
    print_rule("<Declaration> -> <Qualifier> <IDs>")
    Qualifier()
    IDs()

# R13
def IDs():
    print_rule("<IDs> -> <Identifier> | <Identifier>, <IDs>")
    match("identifier")
    if current_token.lexeme == ",":
        match("separator", ",")
        IDs()

# R14
def StatementList():
    print_rule("<Statement List> -> <Statement> | <Statement> <Statement List>")
    Statement()

    while current_token.token_type not in ("EOF",) and \
          current_token.lexeme not in ("}", "@", "fi"):
        Statement()
    
# R15
def Statement():
    print_rule("<Statement> -> <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>")
    if current_token.lexeme == "{":
        Compound()
    elif current_token.token_type == "identifier":
        Assign()
    elif current_token.lexeme == "if":
        If()
    elif current_token.lexeme == "return":
        Return()
    elif current_token.lexeme == "write":
        Print()
    elif current_token.lexeme == "read":
        Scan()
    elif current_token.lexeme == "while":
        While()
    else:
        error("statement (compound, assign, if, return, write, read, or while)")

# R16
def Compound():
    print_rule("<Compound> -> { <Statement List> }")
    match("separator", "{")
    StatementList()
    match("separator", "}")

# R17
def Assign():
    print_rule("<Assign> -> <Identifier> = <Expression> ;")
    match("identifier")
    match("operator", "=")
    Expression()
    match("separator", ";")

# R18
def If():
    print_rule("<If> -> if ( <Condition> ) <Statement> fi | if ( <Condition> ) <Statement> otherwise <Statement> fi")
    match("keyword", "if")
    match("separator", "(")
    Condition()
    match("separator", ")")
    Statement()
    if current_token.lexeme == "otherwise":
        match("keyword", "otherwise")
        Statement()
    match("keyword", "fi")

# R19
def Return():
    print_rule("<Return> -> return ; | return <Expression> ;")
    match("keyword", "return")
    if current_token.lexeme != ";":
        Expression()
    match("separator", ";")

# R20. <Print> ::= write ( <Expression> ) ;
def Print():
    print_rule("<Print> -> write ( <Expression> ) ;")
    match("keyword", "write")
    match("separator", "(")
    Expression()
    match("separator", ")")
    match("separator", ";")
 
 
# R21. <Scan> ::= read ( <IDs> ) ;
def Scan():
    print_rule("<Scan> -> read ( <IDs> ) ;")
    match("keyword", "read")
    match("separator", "(")
    IDs()
    match("separator", ")")
    match("separator", ";")
 
 
# R22. <While> ::= while ( <Condition> ) <Statement>
def While():
    print_rule("<While> -> while ( <Condition> ) <Statement>")
    match("keyword", "while")
    match("separator", "(")
    Condition()
    match("separator", ")")
    Statement()
 
 
# R23. <Condition> ::= <Expression> <Relop> <Expression>
def Condition():
    print_rule("<Condition> -> <Expression> <Relop> <Expression>")
    Expression()
    Relop()
    Expression()
 
 
# R24. <Relop> ::= == | != | > | < | <= | =>
def Relop():
    print_rule("<Relop> -> == | != | > | < | <= | =>")
    if current_token.lexeme in ["==", "!=", ">", "<", "<=", "=>"]:
        match("operator")
    else:
        error("relational operator (==, !=, >, <, <=, =>)")
 
 
# R25. <Expression> ::= <Expression> + <Term> | <Expression> - <Term> | <Term>
#      Left recursion removed:
#      <Expression>       -> <Term> <Expression Prime>
#      <Expression Prime> -> + <Term> <Expression Prime>
#                          | - <Term> <Expression Prime>
#                          | <Empty>
def Expression():
    print_rule("<Expression> -> <Term> <Expression Prime>")
    Term()
    ExpressionPrime()
 
 
def ExpressionPrime():
    if current_token.lexeme in ["+", "-"]:
        print_rule(f"<Expression Prime> -> {current_token.lexeme} <Term> <Expression Prime>")
        match("operator")
        Term()
        ExpressionPrime()
    else:
        print_rule("<Expression Prime> -> <Empty>")
 
 
# R26. <Term> ::= <Term> * <Factor> | <Term> / <Factor> | <Factor>
#      Left recursion removed:
#      <Term>       -> <Factor> <Term Prime>
#      <Term Prime> -> * <Factor> <Term Prime>
#                    | / <Factor> <Term Prime>
#                    | <Empty>
def Term():
    print_rule("<Term> -> <Factor> <Term Prime>")
    Factor()
    TermPrime()
 
 
def TermPrime():
    if current_token.lexeme in ["*", "/"]:
        print_rule(f"<Term Prime> -> {current_token.lexeme} <Factor> <Term Prime>")
        match("operator")
        Factor()
        TermPrime()
    else:
        print_rule("<Term Prime> -> <Empty>")
 
 
# R27. <Factor> ::= - <Primary> | <Primary>
def Factor():
    if current_token.lexeme == "-":
        print_rule("<Factor> -> - <Primary>")
        match("operator", "-")
        Primary()
    else:
        print_rule("<Factor> -> <Primary>")
        Primary()
 
 
# R28. <Primary> ::= <Identifier> | <Integer> | <Identifier> ( <IDs> )
#                  | ( <Expression> ) | <Real> | true | false
def Primary():
    if current_token.token_type == "identifier":
        # Check if it's a function call: identifier ( <IDs> )
        # We need to peek ahead — save state and check next
        match("identifier")
        if current_token.lexeme == "(":
            print_rule("<Primary> -> <Identifier> ( <IDs> )")
            match("separator", "(")
            IDs()
            match("separator", ")")
        else:
            print_rule("<Primary> -> <Identifier>")
            # Already consumed the identifier above, nothing more to do
 
    elif current_token.token_type == "integer":
        print_rule("<Primary> -> <Integer>")
        match("integer")
 
    elif current_token.token_type == "real":
        print_rule("<Primary> -> <Real>")
        match("real")
 
    elif current_token.lexeme == "(":
        print_rule("<Primary> -> ( <Expression> )")
        match("separator", "(")
        Expression()
        match("separator", ")")
 
    elif current_token.lexeme in ["true", "false"]:
        print_rule(f"<Primary> -> {current_token.lexeme}")
        match("keyword")
 
    else:
        error("identifier, integer, real, '(', true, or false")
 
 
# R29. <Empty> ::= ε
def Empty():
    print_rule("<Empty> -> ε")
 
 
#
#  Main
# 
 
def main():
    global tokens, output_file
 
    input_file = input("Enter input file: ").strip()
    output_name = "output_" + input_file
 
    # Read source code
    try:
        with open(input_file, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
 
    # Tokenize
    tokens = lexer(source)
 
    # Open output file
    output_file = open(output_name, "w")
    write("=" * 60)
    write("  Rat26s Syntax Analyzer — Output")
    write("=" * 60)
 
    # Start parse from top-level rule R1
    next_token()
    Rat26s()
 
    # Should be at EOF now
    if current_token.token_type != "EOF":
        error("EOF")
 
    write("\n" + "=" * 60)
    write("  Parsing Complete — No Syntax Errors!")
    write("=" * 60)
    output_file.close()
 
    print(f"Output written to: {output_name}")
 
 
if __name__ == "__main__":
    main()