print ("Welcome to LEXER")

import sys

#token
class Token:
    def __init__(self, token_type, lexeme):
        self.token_type = token_type
        self.lexeme = lexeme

    def __str__(self):
        return f"{self.token_type:<15} {self.lexeme}"

#keywords
Keywords = {
    "integer", "boolean", "real", "true", "false",
    "if", "otherwise", "fi",
    "while", "return", "read", "write"
}

#FSM for Identifier
def indentifier_fsm(source, index): # FSM to handle 'words'
    lexeme = ""
    
    lexeme += source[index]
    index += 1

    while index < len(source) and (
        source[index].isalnum() or source[index] == "_"
    ):
        lexeme += source[index]
        index += 1

    if lexeme.lower() in Keywords: # Checks if the result is a keyword, if so return keyword
        return Token("keyword", lexeme), index
    
    return Token("identifier", lexeme), index # Else, return identifier

#FSM for INT or REAL
def number_fsm(source, index): # FSM to handle numbers
    lexeme = ""
    is_real = False

    while index < len(source) and source[index].isdigit():
        lexeme += source[index]
        index += 1

    if index < len(source) and source[index] == ".": # Check for '.' which indicates when to switch to number mode
        is_real = True
        lexeme += "."
        index += 1

        if index >= len(source) or not source[index].isdigit(): # Throws 'invalid' if there is no '.'
              return Token("invalid", lexeme), index
        
        while index < len(source) and source[index].isdigit():
              lexeme += source[index]
              index += 1

    if is_real:
        return Token("real", lexeme), index
    else: 
        return Token("integer", lexeme), index
    
#Lexer
def lexer(source):
    tokens = []
    index = 0

    while index < len(source):
        char = source[index]

        if char.isspace():
            index += 1
            continue

        if char == "/" and index + 1 < len(source) and source[index + 1] == "*":
            index += 2
            while index + 1 < len(source):
                if source[index] == "*" and source[index + 1] == "/":
                    index += 2
                    break
                index += 1
            continue
        
        if index + 1 < len(source):
            two_char = source[index:index+2]
            if two_char in ["<=", ">=", "==", "!=","=>"]:
                tokens.append(Token("operator", two_char))
                index += 2
                continue

        #Keyword Checker
        if char.isalpha():
            token, index = indentifier_fsm(source, index)
            tokens.append(token)
            continue
    
        #int or real
        if char.isdigit():
            token, index = number_fsm(source, index)
            tokens.append(token)
            continue
    
        #operators
        if char in "+-*/=<>" :
            tokens.append(Token("operator", char))
            index += 1
            continue
    
        #seperator
        if char in "();,{}@" :
            tokens.append(Token("separator", char))
            index += 1
            continue
        
        tokens.append(Token("unknown", char))
        index += 1

    tokens.append(Token("EOF", "EOF"))
    return tokens

# RUN
def main():

    if len(sys.argv) < 2:
        print("Usage: python3 rat26s_lexer.py <inputfile>")
        return
    
    input_file = sys.argv[1]
    output_file = "output_" + input_file

    try:
        with open(input_file, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    tokens = lexer(source)

    with open(output_file, "w") as out:
        out.write("Token       Lexeme\n")
        out.write("----------------------\n")
        for token in tokens:
            out.write(str(token) + "\n")

    print("Lexer Complete.")
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()    
