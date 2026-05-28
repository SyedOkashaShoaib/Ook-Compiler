# Ook! Compiler

> *A programming language for orangutans.*

Ook! is a fully-featured compiled language built in Python, inspired by the esoteric [Ook! language](https://esolangs.org/wiki/Ook!). This project implements a complete compiler pipeline from source to executable stack machine code, along with a custom virtual machine to run it.

---

## Pipeline

The compiler processes `.ook` source files through six sequential phases:

| Phase | Description |
|-------|-------------|
| **1 — Lexical Analysis** | Tokenizes the source file into a stream of tokens |
| **2 — Syntax Analysis** | Parses the token stream into an Abstract Syntax Tree (AST) |
| **3 — Semantic Analysis** | Validates the AST; builds a symbol table and jump table |
| **4 — Intermediate Code Generation (ICG)** | Produces a flat list of three-address quads from the AST |
| **5 — Optimization** | Applies peephole optimizations to reduce instruction count |
| **6 — Code Generation** | Emits stack machine instructions to a `.sm` output file |

The compiled `.sm` file is then executed by a custom stack-based virtual machine (`vm.py`) with a 30,000-cell memory tape.

---

## Usage

### Compile a source file

```bash
python main.py <source.ook>
```

### Compile with verbose diagnostics

Prints the token stream, AST, symbol table, quad tables, optimization report, and final stack machine code.

```bash
python main.py <source.ook> -v
```

### Compile and run immediately

```bash
python main.py <source.ook> --run
```

### Specify a custom output path

```bash
python main.py <source.ook> -o <output.sm>
```

### Run a compiled `.sm` file directly

```bash
python vm.py <output.sm>
```

---

## Project Structure

```
Ook-Compiler/
├── main.py                  # Compiler driver
├── vm.py                    # Stack machine virtual machine
├── Phase1_lexical/          # Lexer
├── Phase2_Parser/           # Parser and AST
├── Phase3_semantic/         # Semantic analyzer, symbol table, jump table
├── phase4_ICG/              # Intermediate code generation
├── phase5_optimizer/        # Peephole optimizer
├── phase6_CG/               # Stack machine code generation
└── test_cases/              # Sample .ook programs
```

---

## Requirements

- Python 3.x
- No external dependencies

---
