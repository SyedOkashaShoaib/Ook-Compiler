import sys
import os

TAPE_SIZE = 30000


def load(filepath: str):
    instructions = []
    labels = {}

    with open(filepath, 'r') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            if line.startswith("LABEL"):
                label_name = line.split()[1]
                labels[label_name] = len(instructions)
            else:
                instructions.append(line)

    return instructions, labels


def run(filepath: str):
    if not os.path.isfile(filepath):
        print(f"VM ERROR: file '{filepath}' not found.")
        sys.exit(1)

    instructions, labels = load(filepath)

    memory = [0] * TAPE_SIZE
    ptr    = 0
    stack  = []
    ip     = 0    

    while ip < len(instructions):
        instr = instructions[ip]
        parts = instr.split()
        op    = parts[0]

        if op == 'INIT_PTR':
            ptr = int(parts[1])

        elif op == 'SET_PTR':
            ptr = int(parts[1])

        elif op == 'INC_PTR':
            ptr += 1
            if ptr >= TAPE_SIZE:
                print("VM ERROR: pointer moved past end of tape.")
                sys.exit(1)

        elif op == 'DEC_PTR':
            ptr -= 1
            if ptr < 0:
                print("VM ERROR: pointer moved before start of tape.")
                sys.exit(1)

        elif op == 'PUSH_CELL':
            stack.append(memory[ptr])

        elif op == 'POP_CELL':
            if not stack:
                print(f"VM ERROR: stack underflow at instruction {ip}.")
                sys.exit(1)
            memory[ptr] = stack.pop() & 0xFF   # keep in byte range

        elif op == 'ADD_IMM':
            if not stack:
                print(f"VM ERROR: stack underflow at instruction {ip}.")
                sys.exit(1)
            stack[-1] = (stack[-1] + int(parts[1])) & 0xFF

        elif op == 'SUB_IMM':
            if not stack:
                print(f"VM ERROR: stack underflow at instruction {ip}.")
                sys.exit(1)
            stack[-1] = (stack[-1] - int(parts[1])) & 0xFF

        elif op == 'JZ':
            if not stack:
                print(f"VM ERROR: stack underflow at instruction {ip}.")
                sys.exit(1)
            val = stack.pop()
            if val == 0:
                label = parts[1]
                if label not in labels:
                    print(f"VM ERROR: undefined label '{label}'.")
                    sys.exit(1)
                ip = labels[label]
                continue  

        elif op == 'JMP':
            label = parts[1]
            if label not in labels:
                print(f"VM ERROR: undefined label '{label}'.")
                sys.exit(1)
            ip = labels[label]
            continue

        elif op == 'PRINT':
            sys.stdout.write(chr(memory[ptr] & 0xFF))
            sys.stdout.flush()

        elif op == 'READ':
            ch = sys.stdin.read(1)
            memory[ptr] = ord(ch) if ch else 0

        elif op == 'BANANA':
            # Use a raw string (r""") to safely print ASCII art without escape sequence crashes
            banana_art = r"""
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkZ++++__hhkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkb'. ;^^". vkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk' '1i>~ .ckkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbk' `*ZLU. ckkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbk'  8kZQ  vkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'  8kZO.'~[bkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbY.  8bqQC<^..Uqkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbb\`.`r&bkbmC|)'`Lkkbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbp  oa8hkkkbJJ0..:!kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkp  B8#bkkbkb0JL..^kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkb\) .%MkkkkbkbOJC. ^kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkb'..&kkkkkkbkbOJC. ^kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbb' .8kkkkkkkkk0JC. `cbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbb. .8kbkkkkkbkddJX! .hkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbb'  8kkkkkkkkkkbCJ! .hkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbb' .&/ttkkQ/tkbbLJ! .hkkkkkC/tttfbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkb` .&  .bbr  hkkCJ!  hkkkL^'.,`' 'hkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbp.  8  .bbj .hkkCJ! .kkdd. `;)~I  akkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..:*h' 'bbr.'hbbCJ!.'hi"..ohkbbr  akkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk. ,8bppqkkdppkbbCJ!  ^.`:*hkkbpj  akkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk. ,8bkkkkkkkkkkkCJ!. rrv*kkkkZ{> .abkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk. ,8bkkkkkkkkkkkCLJL.hkkkkkkdJ'.'pkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbhp  ,8bkkkkkkkkkkhJLCL:bbkkkdmCY`.`kbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkdb;:::;Ukkkkkkkkkkkkkkkk<: .#akbkkkkkkkkkkhCCCJCCCCCCJ|:. )dbkbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkka; ....,:;hkkkkkkkbahh:;^.'hahkkkkkkkkkkkkbUC+lCLLLLLI^.'rCkbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkka .(nYtjr.'1\\\\\\\.  'xrnobbbbbOO/bbkkkkkkkJ/)..     :[vhkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkko'.!>dkhaq'''`''''``1ppoaakkkkdLl!.kbkkkkkbbdLCv. "tftjvpkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk:^..qbkh&&&888&&&&*bkkkkkbbbz.  .wkkkkkkbkkQQJ,''.vzJbkkkkkkkkkkbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkb0Q..l>Obbkkkkkkbkkkkkkkk0;<..uf'.okkkkkkkbkbCJ:'.:bkbkkbkkkbkkkbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbh/'..l>00O0kbkkkkkbQOOOl'''/zf'.ixabkkkkkkbqJu/'.!\ahahh!lll!okkbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbbk0\]}....')}}}}}}['...._}vuvuz}`'`/hbkkkkkbb|{{..     .xil: 'Qkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbm0w1{)).'......`.<1){vuvuvucv}l..}ZkbkkkkkUczzJJJJCJJ*>l, '0kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbkkkkkkkbkkkkkkkkhdkkkkbbbXXvuU, .^mZZmddbdddbbddd0zz'..;kkbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbkkkkkbkkkkkkkkkkkkkkkkkkbkkbd0wmv1:..  `--_--_____-!.. <}kbbkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkhqwj|\|;            .^|\CZkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkbbbkbkkhkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
 """
            print(banana_art)
            print("OOK!")

        elif op == 'HALT':
            break

        else:
            print(f"VM ERROR: unknown instruction '{op}' at index {ip}.")
            sys.exit(1)

        ip += 1

    print()  


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: python vm.py <file.sm>")
        sys.exit(1)

    run(sys.argv[1])