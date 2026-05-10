import sys
import os
import argparse

# Import compiler pipeline modules
from Phase1_lexical.lexer import run_Lexer
from Phase2_Parser.parser import Parser, print_ast
from Phase3_semantic.semantic import SemanticAnalyzer, print_symbol_table, print_jump_table
# TODO: Import Phase 4 modules here when ready
def print_welcome_banner():
    # 1. Paste your ASCII text ("Ook! Compiler") inside these quotes
    ook_text_art = r"""
     ______     ______    __  ___  __       ______   ______   .___  ___. .______    __   __       _______ .______      
 /  __  \   /  __  \  |  |/  / |  |     /      | /  __  \  |   \/   | |   _  \  |  | |  |     |   ____||   _  \     
|  |  |  | |  |  |  | |  '  /  |  |    |  ,----'|  |  |  | |  \  /  | |  |_)  | |  | |  |     |  |__   |  |_)  |    
|  |  |  | |  |  |  | |    <   |  |    |  |     |  |  |  | |  |\/|  | |   ___/  |  | |  |     |   __|  |      /     
|  `--'  | |  `--'  | |  .  \  |__|    |  `----.|  `--'  | |  |  |  | |  |      |  | |  `----.|  |____ |  |\  \----.
 \______/   \______/  |__|\__\ (__)     \______| \______/  |__|  |__| | _|      |__| |_______||_______|| _| `._____|
                                                                                                                    
    """
    

    
    subtitle = "                                       A programming language for orangutans"
    

    print(ook_text_art)
    print(subtitle)
    print("=" * 120 + "\n")
def main():
    print_welcome_banner()
    # Setup Command Line Arguments
    arg_parser = argparse.ArgumentParser(description="Ook! Compiler Driver")
    arg_parser.add_argument("filename", help="The target .ook source file to compile")
    arg_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose diagnostic output for all compiler phases")
    
    args = arg_parser.parse_args()
    target_file = args.filename

    if not os.path.isfile(target_file):
        print(f"[ERROR] File '{target_file}' not found. Compilation aborted.")
        sys.exit(1)

    print(f"[INFO] Starting compilation process for: {target_file}\n")

    try:
        # ==========================================
        # COMPILER PIPELINE EXECUTION
        # ==========================================
        
        # Phase 1: Lexical Analysis
        token_stream = run_Lexer(target_file)
        
        # Phase 2: Syntax Analysis
        syntax_parser = Parser(token_stream)
        ast = syntax_parser.parse_program()
        
        # Phase 3: Semantic Analysis
        semantic_analyzer = SemanticAnalyzer(ast)
        final_ast, jump_table, symbol_table, var_count = semantic_analyzer.analyze()

        # ==========================================
        # TODO: PHASE 4 - CODE GENERATION
        # ==========================================
        # Teammate extension point:
        # Pass the annotated AST, Jump Table, and var_count to Phase 4 to generate C code.
        # Example: 
        # generated_code = generate_c_code(final_ast, jump_table, symbol_table, var_count)
        # write_output(generated_code, output_filename)

        print("[SUCCESS] Compilation completed successfully. Ook Ook")

        # ==========================================
        # VERBOSE OUTPUT (Diagnostic Mode)
        # ==========================================
        
        if args.verbose:
            print("\n" + "="*50)
            print(" DIAGNOSTICS: PHASE 1 (TOKEN STREAM)")
            print("="*50)
            for t in token_stream:
                print(t)

            print("\n" + "="*50)
            print(" DIAGNOSTICS: PHASE 2 (ABSTRACT SYNTAX TREE)")
            print("="*50)
            print_ast(final_ast)

            print("\n" + "="*50)
            print(" DIAGNOSTICS: PHASE 3 (SEMANTIC DATA)")
            print("="*50)
            
            print("[SYMBOL TABLE]")
            print_symbol_table(symbol_table)
            print(f"\nTotal Memory Slots Allocated for Variables: {var_count}. Ook Ook")
            
            print("\n[JUMP TABLE]")
            print_jump_table(jump_table)
            print("="*50 + "\n")

    except Exception as e:
        print(f"[FATAL] An unexpected error occurred during compilation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()