import sys
import os
import argparse

from Phase1_lexical.lexer import run_Lexer
from Phase2_Parser.parser import Parser, print_ast
from Phase3_semantic.semantic import SemanticAnalyzer, print_symbol_table, print_jump_table
from phase4_ICG.icg import ICGVisitor, print_quads
from phase5_optimizer.optimizer import run_Optimizer, print_report
from phase6_CG.cg import generate, write_sm, print_sm

def print_welcome_banner():
    ook_text_art = r"""
  ░██████              ░██       ░██      ░██████                                        ░██░██                     
 ░██   ░██             ░██       ░██     ░██   ░██                                          ░██                     
░██     ░██  ░███████  ░██    ░██░██    ░██         ░███████  ░█████████████  ░████████  ░██░██  ░███████  ░██░████ 
░██     ░██ ░██    ░██ ░██   ░██ ░██    ░██        ░██    ░██ ░██   ░██   ░██ ░██    ░██ ░██░██ ░██    ░██ ░███     
░██     ░██ ░██    ░██ ░███████  ░██    ░██        ░██    ░██ ░██   ░██   ░██ ░██    ░██ ░██░██ ░█████████ ░██      
 ░██   ░██  ░██    ░██ ░██   ░██         ░██   ░██ ░██    ░██ ░██   ░██   ░██ ░███   ░██ ░██░██ ░██        ░██      
  ░██████    ░███████  ░██    ░██░██      ░██████   ░███████  ░██   ░██   ░██ ░██░█████  ░██░██  ░███████  ░██      
                                                                              ░██                                   
                                                                              ░██                                   
    """
    subtitle = "                                       A programming language for orangutans"
    print(ook_text_art)
    print(subtitle)
    print("=" * 120 + "\n")

def main():
    print_welcome_banner()

    arg_parser = argparse.ArgumentParser(description="Ook! Compiler Driver")
    arg_parser.add_argument("filename", help="The target .ook source file to compile")
    arg_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose diagnostic output for all compiler phases")
    arg_parser.add_argument("-o", "--output", help="Output path for the .sm file (default: same name as input)", default=None)
    arg_parser.add_argument("--run", action="store_true", help="Execute the compiled .sm file immediately after compilation")

    args = arg_parser.parse_args()
    target_file = args.filename

    if not os.path.isfile(target_file):
        print(f"[ERROR] File '{target_file}' not found. Compilation aborted.")
        sys.exit(1)

    output_file = args.output
    if output_file is None:
        output_file = os.path.splitext(target_file)[0] + ".sm"

    print(f"[INFO] Starting compilation process for: {target_file}\n")

    try:
        # ── Phase 1: Lexical Analysis ──────────────────────────────────────
        token_stream = run_Lexer(target_file)
        print("[Phase 1] Lexical Analysis       ✓")

        # ── Phase 2: Syntax Analysis ───────────────────────────────────────
        syntax_parser = Parser(token_stream)
        ast = syntax_parser.parse_program()
        print("[Phase 2] Syntax Analysis         ✓")

        # ── Phase 3: Semantic Analysis ─────────────────────────────────────
        semantic_analyzer = SemanticAnalyzer(ast)
        final_ast, jump_table, symbol_table, var_count = semantic_analyzer.analyze()
        print("[Phase 3] Semantic Analysis       ✓")

        # ── Phase 4: Intermediate Code Generation ─────────────────────────
        icg = ICGVisitor(var_count)
        icg.visit(final_ast)
        quads = icg.quads
        print(f"[Phase 4] ICG                     ✓  ({len(quads)} quads)")

        # ── Phase 5: Optimization ──────────────────────────────────────────
        optimized_quads, opt_report = run_Optimizer(quads)
        total_removed = sum(opt_report.values())
        print(f"[Phase 5] Optimization            ✓  ({total_removed} instruction(s) removed/folded)")

        # ── Phase 6: Target Code Generation ───────────────────────────────
        instructions = generate(optimized_quads)
        write_sm(instructions, output_file)
        print(f"[Phase 6] Code Generation         ✓  ({len(instructions)} instructions → {output_file})")

        print(f"\n[SUCCESS] Compilation complete. Ook Ook")
        print(f"[INFO]    Run your program with: python vm.py {output_file}\n")

        # ── Verbose diagnostics ────────────────────────────────────────────
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
            print(f"\nTotal Memory Slots Allocated: {var_count}")
            print("\n[JUMP TABLE]")
            print_jump_table(jump_table)

            print("\n" + "="*50)
            print(" DIAGNOSTICS: PHASE 4 (QUAD TABLE — RAW ICG)")
            print("="*50)
            print_quads(quads)

            print("\n" + "="*50)
            print(" DIAGNOSTICS: PHASE 5 (OPTIMIZATION REPORT + OPTIMIZED QUADS)")
            print("="*50)
            print_report(opt_report, len(quads), len(optimized_quads))
            print()
            print_quads(optimized_quads)

            print("\n" + "="*50)
            print(" DIAGNOSTICS: PHASE 6 (STACK MACHINE CODE)")
            print("="*50)
            print_sm(instructions)
            print("="*50 + "\n")

        # ── Optional immediate execution ───────────────────────────────────
        if args.run:
            print(f"[VM] Executing {output_file}...\n")
            import importlib.util
            vm_path = os.path.join(os.path.dirname(__file__), 'vm.py')
            spec = importlib.util.spec_from_file_location("vm", vm_path)
            vm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vm)
            vm.run(output_file)

    except Exception as e:
        print(f"[FATAL] Unexpected error during compilation: {e}")
        raise


if __name__ == "__main__":
    main()