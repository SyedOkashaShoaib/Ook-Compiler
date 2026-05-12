import sys
import os
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from phase4_ICG.icg import run_ICG, Quad, print_quads

def is_mem_add(q: Quad) -> bool:
    return q.op == 'ADD' and q.arg1 == 'mem[ptr]'

def is_mem_sub(q: Quad) -> bool:
    return q.op == 'SUB' and q.arg1 == 'mem[ptr]'

def is_mem_assign(q: Quad) -> bool:
    return q.op == 'ASSIGN' and q.result == 'mem[ptr]'

def pass_fold_increments(quads: list) -> list:
    result = []
    i = 0
    folded = 0

    while i < len(quads):
        q = quads[i]

        if (is_mem_add(q) or is_mem_sub(q)) and (i + 1 < len(quads)) and is_mem_assign(quads[i + 1]):
            op       = q.op
            net      = 0        
            base_tmp = q.result

            j = i
            while j + 1 < len(quads):
                nxt_arith  = quads[j]
                nxt_assign = quads[j + 1]

                if (nxt_arith.op == op and
                        nxt_arith.arg1 == 'mem[ptr]' and
                        is_mem_assign(nxt_assign)):
                    net += int(nxt_arith.arg2)
                    j += 2
                    if j > i + 2:  
                        folded += 1
                else:
                    break

            if net == 0:
                i = j
                folded += 1
                continue

            result.append(Quad(op, 'mem[ptr]', str(net), base_tmp))
            result.append(Quad('ASSIGN', base_tmp, None, 'mem[ptr]'))
            i = j
        else:
            result.append(q)
            i += 1

    return result, folded

def pass_dead_code_elimination(quads: list) -> list:
    result = list(quads)
    eliminated = 0
    changed = True

    while changed:
        changed = False
        new = []
        i = 0
        while i < len(result):
            q = result[i]
            if (is_mem_assign(q) and
                    i + 2 < len(result) and
                    (is_mem_add(result[i + 1]) or is_mem_sub(result[i + 1])) and
                    is_mem_assign(result[i + 2])):
                eliminated += 1
                changed = True
                i += 1
                continue

            new.append(q)
            i += 1
        result = new

    return result, eliminated

def pass_copy_propagation(quads: list) -> list:
    result = []
    eliminated = 0
    last_ptr_val = None 
    for q in quads:
        if q.op == 'JUMP_ABS':
            if last_ptr_val == q.arg1:
                # ptr is already at this index — redundant jump
                eliminated += 1
                continue
            last_ptr_val = q.arg1

        elif q.op in ('MOVE_PTR', 'INIT_PTR', 'ADD', 'SUB'):
            last_ptr_val = None

        result.append(q)

    return result, eliminated


def run_Optimizer(quads: list) -> tuple:
    report = {}

    quads, n1 = pass_fold_increments(quads)
    report['Constant Folding (Inc/Dec)'] = n1

    quads, n2 = pass_dead_code_elimination(quads)
    report['Dead Code Elimination'] = n2

    quads, n3 = pass_copy_propagation(quads)
    report['Copy Propagation'] = n3

    return quads, report


def print_report(report: dict, before: int, after: int):
    print(f"\n  Quads before optimisation : {before}")
    for name, count in report.items():
        print(f"  {name:<40}: {count} instruction(s) removed/folded")
    print(f"  Quads after optimisation  : {after}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SYSTEM ERROR: filename not provided. ook out")
        sys.exit(1)

    target_file = sys.argv[1]

    if not os.path.isfile(target_file):
        print(f"SYSTEM ERROR: file '{target_file}' does not exist. ook out")
        sys.exit(1)

    print(f"\n--- RUNNING PHASE 5: OPTIMIZATION ON {target_file} ---")

    raw_quads, symbol_table, var_count = run_ICG(target_file)
    before_count = len(raw_quads)

    optimized_quads, report = run_Optimizer(raw_quads)
    after_count = len(optimized_quads)

    print_report(report, before_count, after_count)

    print("\n--- PHASE 5 OUTPUT: OPTIMIZED QUAD TABLE ---")
    print_quads(optimized_quads)
    print("--------------------------------------------\n")