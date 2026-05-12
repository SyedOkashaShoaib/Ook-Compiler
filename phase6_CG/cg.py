import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from phase4_ICG.icg import run_ICG, Quad
from phase5_optimizer.optimizer import run_Optimizer


# ==========================================
# STACK MACHINE INSTRUCTION SET
#
# INIT_PTR  n           ptr = n
# SET_PTR   n           ptr = n  (variable jump)
# INC_PTR               ptr++
# DEC_PTR               ptr--
# PUSH_CELL             stack.push(mem[ptr])
# POP_CELL              mem[ptr] = stack.pop()
# ADD_IMM   n           stack[-1] += n
# SUB_IMM   n           stack[-1] -= n
# LABEL     Lx          jump target
# JZ        Lx          if stack.pop() == 0: jump Lx
# JMP       Lx          jump Lx
# PRINT                 output chr(mem[ptr])
# READ                  mem[ptr] = ord(input char)
# BANANA                Ook? Ook? easter egg
# HALT                  end program
# ==========================================

def generate(quads: list[Quad]) -> list[str]:
    instructions = []

    for q in quads:

        if q.op == 'INIT_PTR':
            instructions.append(f"INIT_PTR {q.arg1}")

        elif q.op == 'JUMP_ABS':
            instructions.append(f"SET_PTR {q.arg1}")

        elif q.op == 'MOVE_PTR':
            # arg1 is a temp holding ptr±1; arg2 tells direction via parent ADD/SUB
            # We re-derive direction from result being 'ptr' and check the temp name
            # Direction was encoded at ICG time: ADD→INC, SUB→DEC
            # We stored the op on the Quad so we can't check here — instead ICG
            # emits MOVE_PTR with arg2 hint. We just emit based on arg1 containing +/-
            # Actually we encoded it simply: the temp value IS the new ptr.
            # Emit SET_PTR would be wrong (absolute). ICG emits ADD ptr,1 → MOVE_PTR.
            # We flag direction by checking what produced the temp: not accessible here.
            # Solution: ICG already emits separate ADD/SUB for ptr, we just need to
            # map those. We handle this via the ptr-specific ADD/SUB check below.
            pass 

        elif q.op == 'ADD':
            if q.arg1 == 'ptr':
                n = int(q.arg2)
                for _ in range(n):
                    instructions.append("INC_PTR")
            elif q.arg1 == 'mem[ptr]':
                n = int(q.arg2)
                instructions.append("PUSH_CELL")
                instructions.append(f"ADD_IMM {n}")

        elif q.op == 'SUB':
            if q.arg1 == 'ptr':
                n = int(q.arg2)
                for _ in range(n):
                    instructions.append("DEC_PTR")
            elif q.arg1 == 'mem[ptr]':
                n = int(q.arg2)
                instructions.append("PUSH_CELL")
                instructions.append(f"SUB_IMM {n}")

        elif q.op == 'ASSIGN':
            if q.result == 'mem[ptr]':
                instructions.append("POP_CELL")

        elif q.op == 'LABEL':
            instructions.append(f"LABEL {q.arg1}")

        elif q.op == 'IF_ZERO_GOTO':
            instructions.append("PUSH_CELL")
            instructions.append(f"JZ {q.result}")

        elif q.op == 'GOTO':
            instructions.append(f"JMP {q.arg1}")

        elif q.op == 'PRINT':
            instructions.append("PRINT")

        elif q.op == 'READ':
            instructions.append("READ")

        elif q.op == 'GIVE_BANANA':
            instructions.append("BANANA")

        elif q.op == 'HALT':
            instructions.append("HALT")

    return instructions


def write_sm(instructions: list[str], output_path: str):
    with open(output_path, 'w') as f:
        for instr in instructions:
            f.write(instr + '\n')


def print_sm(instructions: list[str]):
    print(f"  {'#':<6} INSTRUCTION")
    print(f"  {'-'*6} {'-'*30}")
    for i, instr in enumerate(instructions):
        if instr.startswith("LABEL"):
            print(f"\n  {instr}:")
        else:
            print(f"  {i:<6} {instr}")


def run_CodeGen(filename, output_path=None):
    quads, symbol_table, var_count = run_ICG(filename)
    optimized_quads, report = run_Optimizer(quads)
    instructions = generate(optimized_quads)

    if output_path is None:
        base = os.path.splitext(filename)[0]
        output_path = base + ".sm"

    write_sm(instructions, output_path)
    return instructions, output_path, report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SYSTEM ERROR: filename not provided. ook out")
        sys.exit(1)

    target_file = sys.argv[1]

    if not os.path.isfile(target_file):
        print(f"SYSTEM ERROR: file '{target_file}' does not exist. ook out")
        sys.exit(1)

    output_file = sys.argv[2] if len(sys.argv) >= 3 else None

    print(f"\n--- RUNNING PHASE 6: CODE GENERATION ON {target_file} ---")

    instructions, out_path, report = run_CodeGen(target_file, output_file)

    print(f"\n  Output written to: {out_path}")
    print(f"  Instructions emitted: {len(instructions)}")

    print("\n--- PHASE 6 OUTPUT: STACK MACHINE CODE ---")
    print_sm(instructions)
    print("------------------------------------------\n")
    print(f"[INFO] Run your program with: python vm.py {out_path}")