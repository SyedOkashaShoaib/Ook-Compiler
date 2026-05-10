import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Phase1_lexical.lexer import run_Lexer

# ==========================================
# 1. AST NODES
# ==========================================

class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

class CommandNode:
    def __init__(self, tocken):
        self.tocken = tocken

class VariableDeclarationNode:
    def __init__(self, identifier_tocken):
        self.identifier_tocken = identifier_tocken

class VariableJumpNode:
    def __init__(self, identifier_tocken):
        self.identifier_tocken = identifier_tocken

class LoopNode:
    def __init__(self, start_tocken):
        self.start_tocken = start_tocken
        self.body = []
        
# ==========================================
# 2. PARSER CORE
# ==========================================

class Parser:
    def __init__(self, tocken_stream):
        self.tocken_stream = tocken_stream
        self.pos = 0
        self.current_tocken = self.tocken_stream[self.pos]

    def get_next_token(self):
        self.pos += 1
        if self.pos < len(self.tocken_stream):
            return self.tocken_stream[self.pos]
        return self.tocken_stream[-1] # Safely return EOF if we go out of bounds

    def error(self, message):
        print(f"SYNTAX ERROR: {message}")
        sys.exit(1)

    def eat(self, tocken_type):
        if self.current_tocken.type == tocken_type:
            self.current_tocken = self.get_next_token()
        else:
            self.error(f"Expected '{tocken_type}' but found '{self.current_tocken.type}' at Line {self.current_tocken.index}.")

    # --- GRAMMAR RULES ---

    def parse_program(self):
        """Program → StatementList"""
        statements = []
        
        # Keep parsing statements until we hit the End of File
        while self.current_tocken.type != 'EOF':
            # Catch unmatched closing brackets
            if self.current_tocken.type == 'LOOP_END':
                self.error(f"Unexpected 'LOOP_END' at Line {self.current_tocken.index} without a matching 'LOOP_START'.")
                
            statements.append(self.parse_statement())
            
        return ProgramNode(statements)

    def parse_statement(self):
        """Statement → Command | Loop | VariableDecl | VariableJump"""
        valid_commands = ('INCREMENT', 'DECREMENT', 'MOVE_RIGHT', 'MOVE_LEFT', 'READ', 'PRINT', 'GIVE_BANANA')
        
        tocken = self.current_tocken
        
        # 1. Standard single-token commands
        if tocken.type in valid_commands:
            self.eat(tocken.type)
            return CommandNode(tocken)
            
        # 2. Variable Declaration: DECLARE_VAR IDENTIFIER
        elif tocken.type == 'DECLARE_VAR':
            self.eat('DECLARE_VAR')
            id_tocken = self.current_tocken
            self.eat('IDENTIFIER')
            return VariableDeclarationNode(id_tocken)
            
        # 3. Variable Jump: JUMP_VAR IDENTIFIER
        elif tocken.type == 'JUMP_VAR':
            self.eat('JUMP_VAR')
            id_tocken = self.current_tocken
            self.eat('IDENTIFIER')
            return VariableJumpNode(id_tocken)
            
        # 4. Loops
        elif tocken.type == 'LOOP_START':
            return self.parse_loop()
            
        else:
            self.error(f"Invalid statement starting with '{tocken.type}' at Line {tocken.index}.")

    def parse_loop(self):
        """Loop → LOOP_START StatementList LOOP_END"""
        # Save the start token for error line reporting and Phase 3 jumps
        start_tocken = self.current_tocken
        self.eat('LOOP_START')
        
        loop_node = LoopNode(start_tocken)
        
        # Parse the inside of the loop until we see the matching closing bracket
        while self.current_tocken.type != 'LOOP_END':
            # If we hit EOF before closing the loop, it's an underflow error
            if self.current_tocken.type == 'EOF':
                self.error(f"Unclosed loop originating at Line {start_tocken.index}.")
                
            loop_node.body.append(self.parse_statement())
            
        self.eat('LOOP_END')
        return loop_node

# ==========================================
# 3. UTILITY AND EXECUTION
# ==========================================

def print_ast(node, indent=""):
    """Recursively prints the AST in a readable, hierarchical format."""
    if isinstance(node, ProgramNode):
        print("Program:")
        for stmt in node.statements:
            print_ast(stmt, indent + "  ")
            
    elif isinstance(node, CommandNode):
        print(f"{indent}Command: {node.tocken.type} (Line {node.tocken.index})")
        
    elif isinstance(node, VariableDeclarationNode):
        print(f"{indent}VariableDecl: {node.identifier_tocken.value} (Line {node.identifier_tocken.index})")
        
    elif isinstance(node, VariableJumpNode):
        print(f"{indent}VariableJump: {node.identifier_tocken.value} (Line {node.identifier_tocken.index})")
        
    elif isinstance(node, LoopNode):
        print(f"{indent}Loop (Started Line {node.start_tocken.index}):")
        for stmt in node.body:
            print_ast(stmt, indent + "  ")

def run_Parser(filename):
    # 1. Get the tokens silently from Phase 1
    tocken_stream = run_Lexer(filename)
    print("\n--- PHASE 1: TOKEN STREAM RECIEVED ---")
    for t in tocken_stream:
        print(t)
    print("--------------------------------------\n")
    
    # 2. Feed them into the Parser
    parser = Parser(tocken_stream)
    
    # 3. Build the AST
    ast = parser.parse_program()
    
    return ast

# --- INDEPENDENT EXECUTION BLOCK ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SYSTEM ERROR: filename not provided. ook out")
        sys.exit(1)
        
    target_filename = sys.argv[1]
    
    if not os.path.isfile(target_filename):
        print(f"SYSTEM ERROR: file {target_filename} does not exist. ook out")
        sys.exit(1)

    print(f"\n--- RUNNING PHASE 2: SYNTAX ANALYSIS ON {target_filename} ---")
    
    final_ast = run_Parser(target_filename)
    
    print("\n--- ABSTRACT SYNTAX TREE ---")
    print_ast(final_ast)
    print("----------------------------\n")