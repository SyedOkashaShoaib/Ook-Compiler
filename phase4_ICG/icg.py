import sys
import os
from dataclasses import dataclass
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Phase2_Parser.parser import (
    ProgramNode, CommandNode, LoopNode,
    VariableDeclarationNode, VariableJumpNode
)
from Phase3_semantic.semantic import run_Semantic


@dataclass
class Quad:
    op: str
    arg1: Optional[str]
    arg2: Optional[str]
    result: Optional[str]

    def __str__(self):
        parts = [self.op]
        if self.result is not None:
            parts.append(self.result)
        if self.arg1 is not None:
            parts.append(self.arg1)
        if self.arg2 is not None:
            parts.append(self.arg2)
        return '\t'.join(parts)

class ICGVisitor:
    def __init__(self, var_count: int):
        self.quads: list[Quad] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.var_count = var_count

    def new_temp(self) -> str:
        t = f"t{self.temp_counter}"
        self.temp_counter += 1
        return t

    def new_label(self) -> str:
        L = f"L{self.label_counter}"
        self.label_counter += 1
        return L

    def emit(self, op, arg1=None, arg2=None, result=None):
        self.quads.append(Quad(op, arg1, arg2, result))

    def visit(self, node):
        if isinstance(node, ProgramNode):
            self.visit_program(node)
        elif isinstance(node, CommandNode):
            self.visit_command(node)
        elif isinstance(node, VariableDeclarationNode):
            pass  # compile-time only, no runtime instruction
        elif isinstance(node, VariableJumpNode):
            self.visit_jump_var(node)
        elif isinstance(node, LoopNode):
            self.visit_loop(node)

    def visit_program(self, node: ProgramNode):
        self.emit('INIT_PTR', str(self.var_count), None, 'ptr')
        for stmt in node.statements:
            self.visit(stmt)
        self.emit('HALT', None, None, None)

    def visit_command(self, node: CommandNode):
        t = node.tocken.type

        if t == 'INCREMENT':
            tmp = self.new_temp()
            self.emit('ADD',  'mem[ptr]', '1', tmp)
            self.emit('ASSIGN', tmp, None, 'mem[ptr]')

        elif t == 'DECREMENT':
            tmp = self.new_temp()
            self.emit('SUB',  'mem[ptr]', '1', tmp)
            self.emit('ASSIGN', tmp, None, 'mem[ptr]')

        elif t == 'MOVE_RIGHT':
            tmp = self.new_temp()
            self.emit('ADD',  'ptr', '1', tmp)
            self.emit('MOVE_PTR', tmp, None, 'ptr')

        elif t == 'MOVE_LEFT':
            tmp = self.new_temp()
            self.emit('SUB',  'ptr', '1', tmp)
            self.emit('MOVE_PTR', tmp, None, 'ptr')

        elif t == 'PRINT':
            self.emit('PRINT', 'mem[ptr]', None, None)

        elif t == 'READ':
            self.emit('READ', None, None, 'mem[ptr]')

        elif t == 'GIVE_BANANA':
            self.emit('GIVE_BANANA', None, None, None)

    def visit_jump_var(self, node: VariableJumpNode):
        self.emit('JUMP_ABS', str(node.target_memory_index), None, 'ptr')

    def visit_loop(self, node: LoopNode):
        l_start = self.new_label()
        l_end   = self.new_label()

        self.emit('LABEL',         l_start, None, None)
        self.emit('IF_ZERO_GOTO',  'mem[ptr]', None, l_end)

        for stmt in node.body:
            self.visit(stmt)

        self.emit('GOTO',  l_start, None, None)
        self.emit('LABEL', l_end,   None, None)

def run_ICG(filename):
    annotated_ast, jump_table, symbol_table, var_count = run_Semantic(filename)

    visitor = ICGVisitor(var_count)
    visitor.visit(annotated_ast)

    return visitor.quads, symbol_table, var_count


def print_quads(quads: list[Quad]):
    print(f"  {'#':<5} {'OP':<16} {'RESULT':<14} {'ARG1':<14} {'ARG2'}")
    print(f"  {'-'*5} {'-'*16} {'-'*14} {'-'*14} {'-'*10}")
    for i, q in enumerate(quads):
        print(f"  {i:<5} {q.op:<16} {str(q.result):<14} {str(q.arg1):<14} {str(q.arg2)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SYSTEM ERROR: filename not provided. ook out")
        sys.exit(1)

    target_file = sys.argv[1]

    if not os.path.isfile(target_file):
        print(f"SYSTEM ERROR: file '{target_file}' does not exist. ook out")
        sys.exit(1)

    print(f"\n--- RUNNING PHASE 4: INTERMEDIATE CODE GENERATION ON {target_file} ---")

    quads, symbol_table, var_count = run_ICG(target_file)

    print(f"\n  Variables allocated: {var_count}  (ptr initialised to {var_count})")
    print(f"  Quads generated   : {len(quads)}\n")

    print("--- PHASE 4 OUTPUT: QUAD TABLE (THREE ADDRESS CODE) ---")
    print_quads(quads)
    print("-------------------------------------------------------\n")