from rat26s_lexer import lexer, Token

# ===================================================================================================================================================================================
#  Assignment 3 TO-DO
#   TO-DO 1: The simplified Rat26s is the same except the program has no function definitions and no real type is allowed 
#
#   TO-DO 2: Consider that true has an int value of 1 and false has an int value of 0. No arithmetic operations are allowed for bools
#            The types must match for the arithmetic operations.
#
#   TO-DO 3: Every identifier declared  in the program should be placed in a symbol table and accessed by the symbol table handling procedures.
#
#            Each entry in the symbol table should hold the lexeme, and a "memory Aress" where an  identifier is placed within the symbol table.  
#               For example, define a global integer variable called "Memory_Aress" and set initially 10000 and increment it by one when a new identifier 
#               is declared and placed into the table. 
#           
#            You need to write a procedure that will check to see if a particular identifier is already in the table, a procedure that will insert into the table 
#               and a procedure that will printout all identifiers in the table. If an identifier is used without declaring it, then the parser should provide an error message. 
#               Also, if an identifier is already in the table and wants to declare it for the second time, then the parser should provide an error message. Also, you should check 
#               the type match.
#
#   TO-DO 4: Modify your parser according to the simplified Rat26S and A code to your parser that will produce the assembly code instructions. The instructions should be kept in an 
#            array and at the end, the content of the array is printed out to produce the listing of assembly code. Your array should hold at least 1000 assembly instructions. 
#            The instruction starts from 1. The listing should include an array index for each entry so that it serves as label to jmp to. 
#            (The compiler should also produce a listing of all the identifiers)
# ====================================================================================================================================================================================

# ==============
#  Global State 
# ==============
 
tokens          = []       # full token list from the lexer
index           = 0        # index of the next token to read
current_token   = None     # the token currently being analyzed
print_switch    = True     # set to False to suppress rule printing
output_file     = None     # file handle for output
 
# ============
# Symbol Table
# ============
 
# Each entry stores the identifier name, its type, and its memory address.
# Memory addresses start at 10000 and increment by 1 for each new identifier.
symbol_table    = []
Memory_Aress    = 10000    # global memory address counter starting at 10000 (TO-DO 3a)
 
# ==================
# Instruction Table
# ==================
 
# Holds all generated assembly instructions as dicts: {address, op, oprnd}
# Instructions are numbered starting at 1 (1-based).
# Table is initialized to hold 1000 instructions as required (TO-DO 4).
instr_table     = []
instr_address   = 1
 
# ================
# Back-patch Stack
# ================
 
# When a JMPZ or JMP is generated before the target address is known,
# we push the instruction index onto this stack. Later, back_patch()
# fills in the correct jump target once we know where to jump.
jmp_stack       = []
 
# ==============
#  Output Helper
# ==============
 
def write(line):
    output_file.write(line + "\n")
 
 
# ===============
#  Lexer Advance
# ===============
 
def next_token():
    # Move to the next token. If no more tokens exist, set to EOF.
    global index, current_token
    if index < len(tokens):
        current_token = tokens[index]
        index += 1
    else:
        current_token = Token('EOF', 'EOF')
 
 
# =========================
#  Symbol Table Procedures
# =========================
 
def get_address(lexeme):
    # Return the memory address of a declared identifier.
    # Used when generating PUSHM and POPM instructions.
    for entry in symbol_table:
        if entry["lexeme"] == lexeme:
            return entry["memory_address"]
    return None
 
 
def get_type(lexeme):
    # Return the declared type of an identifier (integer or boolean).
    # Used for type checking during assignment and arithmetic operations (TO-DO 2).
    for entry in symbol_table:
        if entry["lexeme"] == lexeme:
            return entry["type"]
    return None
 
 
def is_in_table(lexeme):
    # Procedure to check if a particular identifier is already in the table (TO-DO 3b).
    # Returns True if found, False otherwise.
    return any(e["lexeme"] == lexeme for e in symbol_table)
 
 
def insert_symbol(lexeme, var_type):
    # Procedure to insert a new identifier into the symbol table (TO-DO 3b).
    # Assigns the next available memory address then increments the counter.
    global Memory_Aress
    symbol_table.append({
        "lexeme":         lexeme,
        "type":           var_type,
        "memory_address": Memory_Aress
    })
    Memory_Aress += 1
 
 
def print_symbol_table():
    # Procedure to print out all identifiers in the symbol table (TO-DO 3b).
    write("\n" + "-" * 50)
    write("  Symbol Table")
    write("-" * 50)
    write(f"  {'Identifier':<20} {'Memory Address':<20} {'Type'}")
    write("-" * 50)
    for entry in symbol_table:
        write(f"  {entry['lexeme']:<20} {entry['memory_address']:<20} {entry['type']}")
    write("-" * 50)
 
 
# ==============================
#  Instruction Table Procedures
# ==============================
 
def generate_instruction(op, oprnd=None):
    # Append one instruction to the instruction table (TO-DO 4).
    # Each instruction has an address (1-based), an operation, and an operand.
    # The array index serves as the label for JMP instructions.
    global instr_address
    instr_table.append({
        "address": instr_address,
        "op":      op,
        "oprnd":   oprnd
    })
    instr_address += 1
 
 
def push_jmp_stack(addr):
    # Push an instruction address onto the back-patch stack.
    # This marks a JMPZ or JMP whose target is not yet known.
    jmp_stack.append(addr)
 
 
def back_patch(jmp_address):
    # Pop the most recent instruction address from the stack and
    # fill in its operand with the now-known jump target address.
    addr = jmp_stack.pop()
    instr_table[addr - 1]["oprnd"] = jmp_address   # addr is 1-based, list is 0-based
 
 
def print_instruction_table():
    # Print the full assembly instruction listing at end of output (TO-DO 4).
    # Array index is included for each entry to serve as a jump label.
    write("\n" + "-" * 40)
    write("  Assembly Code Listing")
    write("-" * 40)
    for instr in instr_table:
        oprnd_str = str(instr["oprnd"]) if instr["oprnd"] is not None else ""
        write(f"  {instr['address']:<6} {instr['op']:<10} {oprnd_str}")
    write("-" * 40)
 
 
# ===============
#  Error Helpers
# ===============
 
def error(expected):
    # Print a syntax error showing what was expected vs what was found, then exit.
    write(f"Syntax Error: Expected {expected}, "
          f"got Token: {current_token.token_type}, "
          f"Lexeme: '{current_token.lexeme}'")
    output_file.close()
    exit(1)
 
 
def semantic_error(msg):
    # Print a semantic error (type mismatch, undeclared variable, etc.) then exit.
    write(f"Semantic Error: {msg}")
    output_file.close()
    exit(1)
 
 
def match(expected_type=None, expected_lexeme=None):
    # Verify the current token matches what the grammar expects,
    # print it to the output file, then advance to the next token.
    global current_token
 
    if current_token.token_type == "unknown":
        error("valid token")
 
    write(f"Token: {current_token.token_type:<12} Lexeme: {current_token.lexeme}")
 
    if expected_type and current_token.token_type != expected_type:
        error(expected_type)
    if expected_lexeme and current_token.lexeme != expected_lexeme:
        error(expected_lexeme)
 
    next_token()
 
 
def print_rule(rule):
    # Print the grammar rule being applied, if print_switch is on.
    if print_switch:
        write(f"   {rule}")
 
 
# ==================================
#  Grammar Rules (Simplified Rat26S)
# ==================================
 
# R1 - Top level rule. Simplified Rat26S has no function definitions (TO-DO 1),
# so we consume the first two @ separators and go straight to declarations.
def Rat26s():
    print_rule("<Rat26s> -> @ <Opt Declaration List> @ <Statement List> @")
    match("separator", "@")
    match("separator", "@")       # no function definitions in simplified version (TO-DO 1)
    OptDeclarationList()
    match("separator", "@")
    StatementList()
    match("separator", "@")
 
 
# R10 - If the next token is a type keyword, parse declarations. Otherwise empty.
def OptDeclarationList():
    print_rule("<Opt Declaration List> -> <Declaration List> | <Empty>")
    if current_token.lexeme in ["integer", "boolean", "real"]:
        DeclarationList()
    else:
        Empty()
 
 
# R11 - Parse one or more declarations separated by semicolons.
def DeclarationList():
    print_rule("<Declaration List> -> <Declaration> ; | <Declaration> ; <Declaration List>")
    Declaration()
    match("separator", ";")
    if current_token.lexeme in ["integer", "boolean", "real"]:
        DeclarationList()
 
 
# R12 - A declaration is a type followed by a list of identifiers.
# We capture the type here so we can store it in the symbol table (TO-DO 3).
def Declaration():
    print_rule("<Declaration> -> <Qualifier> <IDs>")
    var_type = current_token.lexeme
    Qualifier()
    IDs_declare(var_type)
 
 
# R8 - Only integer and boolean are allowed in simplified Rat26S (TO-DO 1).
# Real type is explicitly rejected with a clear semantic error message.
def Qualifier():
    print_rule("<Qualifier> -> integer | boolean")
    if current_token.lexeme == "real":
        semantic_error("Type 'real' is not allowed in simplified Rat26S.")
    elif current_token.lexeme in ["integer", "boolean", "real"]:
        match("keyword")
    else:
        error("integer or boolean")
 
 
# IDs during declaration - inserts each identifier into the symbol table.
# Gives a semantic error if the identifier is already declared (TO-DO 3b).
def IDs_declare(var_type):
    print_rule("<IDs> -> <Identifier> | <Identifier>, <IDs>")
    lexeme = current_token.lexeme
    if is_in_table(lexeme):
        semantic_error(f"Identifier '{lexeme}' is already declared.")
    insert_symbol(lexeme, var_type)
    match("identifier")
    if current_token.lexeme == ",":
        match("separator", ",")
        IDs_declare(var_type)
 
 
# IDs during read() - validates each identifier is declared before use (TO-DO 3b).
def IDs_use():
    print_rule("<IDs> -> <Identifier> | <Identifier>, <IDs>")
    lexeme = current_token.lexeme
    if not is_in_table(lexeme):
        semantic_error(f"Identifier '{lexeme}' used without being declared.")
    match("identifier")
    if current_token.lexeme == ",":
        match("separator", ",")
        IDs_use()
 
 
# R14 - Parse one or more statements until we hit }, @, fi, or EOF.
def StatementList():
    print_rule("<Statement List> -> <Statement> | <Statement> <Statement List>")
    Statement()
    while current_token.token_type not in ("EOF",) and \
          current_token.lexeme not in ("}", "@", "fi"):
        Statement()
 
 
# R15 - Dispatch to the correct statement type based on the current token.
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
 
 
# R16 - A compound statement is a block of statements wrapped in { }.
def Compound():
    print_rule("<Compound> -> { <Statement List> }")
    match("separator", "{")
    StatementList()
    match("separator", "}")
 
 
# R17 - Assignment: check types match, evaluate expression, then POPM to store.
# Type checking enforced here: expression type must match declared variable type (TO-DO 2).
# Generates: [expression instructions] POPM {memory_address}
def Assign():
    print_rule("<Assign> -> <Identifier> = <Expression> ;")
    lexeme = current_token.lexeme
    if not is_in_table(lexeme):
        semantic_error(f"Identifier '{lexeme}' used without being declared.")
    var_type = get_type(lexeme)
    match("identifier")
    match("operator", "=")
    expr_type = Expression()
    # TO-DO 2: types must match for assignment
    if var_type != expr_type:
        semantic_error(f"Type mismatch: cannot assign '{expr_type}' to '{var_type}' variable '{lexeme}'.")
    generate_instruction("POPM", get_address(lexeme))
    match("separator", ";")
 
 
# R18 - If statement with optional otherwise branch.
# For if only:       condition -> JMPZ (patched) -> body -> LABEL
# For if/otherwise:  condition -> JMPZ -> body -> JMP -> otherwise body -> LABEL
def If():
    print_rule("<If> -> if ( <Condition> ) <Statement> fi | if ( <Condition> ) <Statement> otherwise <Statement> fi")
    match("keyword", "if")
    match("separator", "(")
    Condition()
    match("separator", ")")
    Statement()
    if current_token.lexeme == "otherwise":
        # Emit JMP to skip over otherwise block after the if body runs
        else_jmp_addr = instr_address
        generate_instruction("JMP", None)       # back-patched later
        back_patch(instr_address)               # JMPZ lands at start of otherwise
        push_jmp_stack(else_jmp_addr)           # save JMP for patching
        match("keyword", "otherwise")
        Statement()
        back_patch(instr_address)               # JMP lands past otherwise block
    else:
        back_patch(instr_address)               # JMPZ jumps past if body
    generate_instruction("LABEL", None)
    match("keyword", "fi")
 
 
# R19 - Return statement with optional expression.
def Return():
    print_rule("<Return> -> return ; | return <Expression> ;")
    match("keyword", "return")
    if current_token.lexeme != ";":
        Expression()
    match("separator", ";")
 
 
# R20 - Print: evaluate expression, then SOUT pops and outputs the value.
# Generates: [expression instructions] SOUT
def Print():
    print_rule("<Print> -> write ( <Expression> ) ;")
    match("keyword", "write")
    match("separator", "(")
    Expression()
    generate_instruction("SOUT")
    match("separator", ")")
    match("separator", ";")
 
 
# R21 - Scan: for each identifier, SIN reads input and POPM stores it.
# Generates: SIN, POPM {address} for each identifier
def Scan():
    print_rule("<Scan> -> read ( <IDs> ) ;")
    match("keyword", "read")
    match("separator", "(")
    Scan_IDs()
    match("separator", ")")
    match("separator", ";")
 
 
def Scan_IDs():
    lexeme = current_token.lexeme
    if not is_in_table(lexeme):
        semantic_error(f"Identifier '{lexeme}' used without being declared.")
    generate_instruction("SIN")
    generate_instruction("POPM", get_address(lexeme))
    match("identifier")
    if current_token.lexeme == ",":
        match("separator", ",")
        Scan_IDs()
 
 
# R22 - While loop using LABEL and back-patching.
# Generates: LABEL -> condition -> JMPZ (patched) -> body -> JMP back to LABEL
def While():
    print_rule("<While> -> while ( <Condition> ) <Statement>")
    addr = instr_address                  # save address where LABEL is placed
    generate_instruction("LABEL", None)
    match("keyword", "while")
    match("separator", "(")
    Condition()
    match("separator", ")")
    Statement()
    generate_instruction("JMP", addr)     # jump back to LABEL to repeat loop
    back_patch(instr_address)             # JMPZ exits loop to here when condition is false
 
 
# R23 - Condition: evaluate both expressions, then emit the comparison instruction.
# After comparison, emit JMPZ with target to be filled in by back_patch later.
def Condition():
    print_rule("<Condition> -> <Expression> <Relop> <Expression>")
    Expression()
    op = current_token.lexeme
    Relop()
    Expression()
    # Map the relational operator to the correct virtual machine instruction
    relop_map = {
        "<":  "LES",
        ">":  "GRT",
        "==": "EQU",
        "!=": "NEQ",
        "<=": "LEQ",
        "=>": "GEQ",
        ">=": "GEQ",
    }
    if op in relop_map:
        generate_instruction(relop_map[op], None)
    else:
        semantic_error(f"Unknown relational operator '{op}'")
    # JMPZ jumps if condition is false (0). Target filled in later by back_patch.
    push_jmp_stack(instr_address)
    generate_instruction("JMPZ", None)
 
 
# R24 - Relational operator.
def Relop():
    print_rule("<Relop> -> == | != | > | < | <= | =>")
    if current_token.lexeme in ["==", "!=", ">", "<", "<=", "=>", ">="]:
        match("operator")
    else:
        error("relational operator (==, !=, >, <, <=, =>)")
 
 
# R25 - Expression with left recursion removed.
# Original: E -> E + T | E - T | T
# Rewritten: E -> T E'    E' -> + T E' | - T E' | empty
# Returns the type of the expression for type checking (TO-DO 2).
def Expression():
    print_rule("<Expression> -> <Term> <Expression Prime>")
    expr_type = Term()
    ExpressionPrime(expr_type)
    return expr_type
 
 
def ExpressionPrime(expr_type):
    if current_token.lexeme in ["+", "-"]:
        # TO-DO 2: no arithmetic operations allowed on boolean types
        if expr_type == "boolean":
            semantic_error("Arithmetic operations are not allowed on boolean types.")
        op = current_token.lexeme
        print_rule(f"<Expression Prime> -> {op} <Term> <Expression Prime>")
        match("operator")
        term_type = Term()
        # TO-DO 2: types must match for arithmetic operations
        if term_type != expr_type:
            semantic_error(f"Type mismatch in expression: cannot mix '{expr_type}' and '{term_type}'.")
        if op == "+":
            generate_instruction("A", None)
        else:
            generate_instruction("S", None)
        ExpressionPrime(expr_type)
    else:
        print_rule("<Expression Prime> -> <Empty>")
 
 
# R26 - Term with left recursion removed.
# Original: T -> T * F | T / F | F
# Rewritten: T -> F T'    T' -> * F T' | / F T' | empty
# Returns the type of the term for type checking (TO-DO 2).
def Term():
    print_rule("<Term> -> <Factor> <Term Prime>")
    term_type = Factor()
    TermPrime(term_type)
    return term_type
 
 
def TermPrime(term_type):
    if current_token.lexeme in ["*", "/"]:
        # TO-DO 2: no arithmetic operations allowed on boolean types
        if term_type == "boolean":
            semantic_error("Arithmetic operations are not allowed on boolean types.")
        op = current_token.lexeme
        print_rule(f"<Term Prime> -> {op} <Factor> <Term Prime>")
        match("operator")
        factor_type = Factor()
        # TO-DO 2: types must match for arithmetic operations
        if factor_type != term_type:
            semantic_error(f"Type mismatch in expression: cannot mix '{term_type}' and '{factor_type}'.")
        if op == "*":
            generate_instruction("M", None)
        else:
            generate_instruction("D", None)
        TermPrime(term_type)
    else:
        print_rule("<Term Prime> -> <Empty>")
 
 
# R27 - Factor handles unary minus by multiplying by -1.
# Returns the type for type checking (TO-DO 2).
def Factor():
    if current_token.lexeme == "-":
        print_rule("<Factor> -> - <Primary>")
        match("operator", "-")
        prim_type = Primary()
        # TO-DO 2: unary minus not allowed on booleans
        if prim_type == "boolean":
            semantic_error("Unary minus is not allowed on boolean types.")
        generate_instruction("PUSHI", -1)
        generate_instruction("M", None)
        return prim_type
    else:
        print_rule("<Factor> -> <Primary>")
        return Primary()
 
 
# R28 - Primary: the base unit of an expression.
# Handles identifiers (PUSHM), integers (PUSHI),
# parenthesized expressions, and boolean literals true/false.
# true = 1 and false = 0 per TO-DO 2.
# Returns the type for type checking up the call chain (TO-DO 2).
def Primary():
    if current_token.token_type == "identifier":
        lexeme = current_token.lexeme
        if not is_in_table(lexeme):
            semantic_error(f"Identifier '{lexeme}' used without being declared.")
        prim_type = get_type(lexeme)
        generate_instruction("PUSHM", get_address(lexeme))
        match("identifier")
        print_rule("<Primary> -> <Identifier>")
        return prim_type
 
    elif current_token.token_type == "integer":
        val = int(current_token.lexeme)
        generate_instruction("PUSHI", val)
        print_rule("<Primary> -> <Integer>")
        match("integer")
        return "integer"
 
    elif current_token.lexeme == "(":
        print_rule("<Primary> -> ( <Expression> )")
        match("separator", "(")
        prim_type = Expression()
        match("separator", ")")
        return prim_type
 
    elif current_token.lexeme == "true":
        # TO-DO 2: true has integer value of 1
        print_rule("<Primary> -> true")
        generate_instruction("PUSHI", 1)
        match("keyword")
        return "boolean"
 
    elif current_token.lexeme == "false":
        # TO-DO 2: false has integer value of 0
        print_rule("<Primary> -> false")
        generate_instruction("PUSHI", 0)
        match("keyword")
        return "boolean"
 
    else:
        error("identifier, integer, '(', true, or false")
 
 
# R29 - Empty production (epsilon).
def Empty():
    print_rule("<Empty> -> e")
 
 
# =====
#  Main
# =====
 
def main():
    global tokens, output_file
 
    input_file  = input("Enter input file: ").strip()
    output_name = "output_" + input_file
 
    try:
        with open(input_file, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
 
    # Tokenize the source code using the lexer from Assignment 1
    tokens = lexer(source)
 
    output_file = open(output_name, "w", encoding="utf-8")
    write("-" * 60)
    write("  Rat26S Compiler - Assignment 3 Output")
    write("-" * 60)
 
    # Start parsing from the top-level grammar rule
    next_token()
    Rat26s()
 
    if current_token.token_type != "EOF":
        error("EOF")
 
    write("\n" + "-" * 60)
    write("  Parsing Complete - No Syntax Errors!")
    write("-" * 60)
 
    # Print the generated assembly instructions (TO-DO 4)
    print_instruction_table()
 
    # Print the symbol table with all declared identifiers (TO-DO 3b)
    print_symbol_table()
 
    output_file.close()
    print(f"Output written to: {output_name}")
 
 
if __name__ == "__main__":
    main()
 