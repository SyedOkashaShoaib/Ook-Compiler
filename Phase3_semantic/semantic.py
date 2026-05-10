import sys
import os

# Dynamically link the Phase 2 folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Phase2_Parser.parser import (
    run_Parser, ProgramNode, CommandNode, LoopNode, 
    VariableDeclarationNode, VariableJumpNode, print_ast
)

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.instruction_counter = 0
        self.jump_table = [] 
        
        # NEW: The Symbol Table and Variable Counter
        self.symbol_table = {} 
        self.variable_count = 0

    def error(self, message, line_num):
        """Halts the compiler when a Semantic Error is found."""
        print(f"SEMANTIC ERROR: {message} at Line {line_num}. Ook out.")
        sys.exit(1)

    def analyze(self):
        self.visit(self.ast)
        return self.ast, self.jump_table, self.symbol_table, self.variable_count

    def visit(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.visit(stmt)

        elif isinstance(node, CommandNode):
            self.instruction_counter += 1
            node.instruction_index = self.instruction_counter

        # NEW: Handle Variable Declarations
        elif isinstance(node, VariableDeclarationNode):
            var_name = node.identifier_tocken.value
            line_num = node.identifier_tocken.index
            
            # Semantic Check: Did they already declare this?
            if var_name in self.symbol_table:
                self.error(f"Variable '{var_name}' was already declared", line_num)
                
            # Add to Symbol Table and assign it the current memory offset
            self.symbol_table[var_name] = self.variable_count
            self.variable_count += 1
            
            # We don't increment instruction_counter here because declarations 
            # don't generate runtime instructions; they just offset the tape at compile-time.

        # NEW: Handle Variable Jumps
        elif isinstance(node, VariableJumpNode):
            var_name = node.identifier_tocken.value
            line_num = node.identifier_tocken.index
            
            # Semantic Check: Does this variable actually exist?
            if var_name not in self.symbol_table:
                self.error(f"Undeclared variable '{var_name}'", line_num)
                
            # Annotate the AST so Phase 4 knows EXACTLY which memory cell to jump to!
            node.target_memory_index = self.symbol_table[var_name]
            
            self.instruction_counter += 1
            node.instruction_index = self.instruction_counter

        elif isinstance(node, LoopNode):
            self.instruction_counter += 1
            start_index = self.instruction_counter
            node.start_instruction = start_index 

            for stmt in node.body:
                self.visit(stmt)

            self.instruction_counter += 1
            end_index = self.instruction_counter
            node.end_instruction = end_index 

            self.jump_table.append({
                'start_idx': start_index,
                'end_idx': end_index,
                'line_num': node.start_tocken.index
            })

def print_jump_table(jump_table):
    if not jump_table:
        print("  No loops found in the program.")
        return
    for pair in jump_table:
        print(f"  LOOP_START [{pair['start_idx']}] <---> LOOP_END [{pair['end_idx']}]")

def print_symbol_table(symbol_table):
    if not symbol_table:
        print("  No variables declared.")
        return
    for var_name, mem_index in symbol_table.items():
        print(f"  {var_name} -> Memory Cell [{mem_index}]")

def run_Semantic(filename):
    raw_ast = run_Parser(filename)
    
    analyzer = SemanticAnalyzer(raw_ast)
    annotated_ast, jump_table, symbol_table, var_count = analyzer.analyze()
    
    return annotated_ast, jump_table, symbol_table, var_count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SYSTEM ERROR: filename not provided. ook out")
        sys.exit(1)
        
    target_filename = sys.argv[1]
    
    if not os.path.isfile(target_filename):
        print(f"SYSTEM ERROR: file {target_filename} does not exist. ook out")
        sys.exit(1)

    print(f"\n--- RUNNING PHASE 3: SEMANTIC ANALYSIS ON {target_filename} ---")
    
    final_ast, jump_table, symbol_table, var_count = run_Semantic(target_filename)
    
    print("\n--- PHASE 3 OUTPUT: SYMBOL TABLE ---")
    print_symbol_table(symbol_table)
    print(f"\nTotal Variable Offsets Required for Phase 4: {var_count}")
    
    print("\n--- PHASE 3 OUTPUT: JUMP TABLE ---")
    print_jump_table(jump_table)
    print("--------------------------------------------------\n")