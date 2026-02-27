print ("Program started")

#token
class Token:
    def __init__(self, token_type, lexeme):
        self.token_type = token_type
        self.lexeme = lexeme

    def __str__(self):
        return f"{self.token_type:<15} {self.lexeme}"

#keywords
Keywords = {
    "integer", "if", "otherwise", "fi",
    "while", "return", "read", "write"
}

#FSM for Identifier
def indentifier(source, index):
    lexeme = ""
    
    lexeme += source[index]
    index += 1

    while index < len(source) and (
        source[index].isalnum() or source[index] == "_"
    ):
        lexeme += source[index]
        index += 1

    if lexeme.lower() in Keywords:
        return Token("KEYWORD", lexeme), index
    
    return Token("IDENTIFIER", lexeme), index

#FSM for INT or REAL
def num_fsm(source, index):
    lexeme = ""
    is_real = False

    while index < len(source) and source[index].isdigit():
        lexeme += source[index]
        index += 1

    if index < len(source) and source[index] == ".":
        is_real = True
        lexeme += "."
        index += 1

        if index >= len(source) or not source[index].isdigit():
              return Token("INVALID", lexeme), index
        while index < len(source) and source[index].isdigit():
              lexeme += source[index]
              index += 1

    if is_real:
        return Token("REAL", lexeme), index
    else: 
        return Token("INTEGER", lexeme), index
    
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
            while index < len(source) - 1:
                if source[index] == "*" and source[index + 1] == "/":
                    index += 2
                    break
                index += 1
                continue
        
        #Keyword Checker
        if char.isalpha():
            token, index = indentifier(source, index)
            tokens.append(token)
            continue
    
        #int or real
        if char.isdigit():
            token, index = num_fsm(source, index)
            tokens.append(token)
            continue
    
        #operators
        if char in "+-*/=<>" :
            tokens.append(Token("OPERATOR", char))
            index += 1
            continue
    
        #seperator
        if char in "();,{}" :
            tokens.append(Token("SEPARATOR", char))
            index += 1
            continue
        
        tokens.append(Token("UNKNOWN", char))
        index += 1

    tokens.append(Token("EOF", "EOF"))
    return tokens

# RUN
def main():
    input_file = "input.txt"
    output_file = "output.txt"

    with open(input_file, "r") as f:
        source = f.read()

    tokens = lexer(source)

    with open(output_file, "w") as out: 
        for token in tokens: 
            out.write(str(token) + "\n")

    print("Lexical analysis complete.")
    print("Output written to output.txt")

if __name__ == "__main__":
    main() 

