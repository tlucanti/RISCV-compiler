# -*- coding: utf-8 -*-
# @Author: kostya
# @Date:   2021-11-15 15:18:12
# @Last Modified by:   kostya
# @Last Modified time: 2021-11-19 16:58:37

import sys
import platform

REGISTER_NUMBER = 32
IMMIDIATE_LIMIT = 127


class Color(object):
    def __init__(self):
        if platform.system() == 'Windows':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        self.BLACK  = "\033[1;90m"
        self.RED    = "\033[1;91m"
        self.GREEN  = "\033[1;92m"
        self.YELLOW = "\033[1;93m"
        self.BLUE   = "\033[1;94m"
        self.PURPLE = "\033[1;95m"
        self.CYAN   = "\033[1;96m"
        self.WHITE  = "\033[1;97m"
        self.RESET  = "\033[0m"

color = Color()


# ----------------------------- EXCEPTIONS CLASSES -----------------------------
class RISCvSyntaxError(SyntaxError):
    def __init__(self, what, error_index):
        super().__init__(what)
        self.name = 'Syntax error'
        self.what = what
        self.index = error_index


class ImmidiateError(RISCvSyntaxError):
    def __init__(self, what, error_index):
        super().__init__(what, error_index)
        self.name = 'Immidiate value error'


class RegisterError(RISCvSyntaxError):
    def __init__(self, what, error_index):
        super().__init__(what, error_index)
        self.name = 'Register name error'


class Instruction(object):
    """
    A class used to code instruction using numeric values for registers,
    immidiate, alu operation, jump flags and data source flags

    instruction components:

    ┌──┬──┬──┬─────┬───────────┬──────────────┬──────────────┬────────────┬───────────────┐
    │31│30│29│28 27│26 25 24 23│22 21 20 19 18│17 16 15 14 13│12 11 10 9 8│7 6 5 4 3 2 1 0│
    └┬─┴┬─┴┬─┴┬────┴┬──────────┴┬─────────────┴┬─────────────┴┬───────────┴┬──────────────┘
     │  │  │  │     │           │              │              │            └─ [const] 8 bit Immidiate value 
     │  │  │  │     │           │              │              └─ [WA] 6 bit address of the register in the register file
     │  │  │  │     │           │              │                 where the record will be made
     │  │  │  │     │           │              └─ [RA2] 6 bit address in register file for the second operand of the alu
     │  │  │  │     │           └─ [RA1] 6 bit address in register file for the first operand of the alu
     │  │  │  │     └─ [ALUop] the operation code to perform on the alu
     │  │  │  │        alu operations:
     │  │  │  │       ┌───────┬───────┬────────────────┐
     │  │  │  │       │op-code│op-name│op-visualisation│
     │  │  │  │       ├───────┼───────┼────────────────┤
     │  │  │  │       │  0000 │ALU_ADD│ x1 = x2  +  x3 │
     │  │  │  │       │  0001 │ALU_SUB│ x1 = x2  -  x3 │
     │  │  │  │       │  0010 │ALU_XOR│ x1 = x2  ^  x3 │
     │  │  │  │       │  0011 │ALU_OR │ x1 = x2  |  x3 │
     │  │  │  │       │  0100 │ALU_AND│ x1 = x2  &  x3 │
     │  │  │  │       │  0101 │ALU_SRA│ x1 = x2 >>> x3 │ (SIGNED OPERATION)
     │  │  │  │       │  0110 │ALU_SRL│ x1 = x2 >>  x3 │
     │  │  │  │       │  0111 │ALU_SLL│ x1 = x2 <<  x3 │
     │  │  │  │       │  1000 │ALU_LTS│ x1 = x2  <  x3 │ (SIGNED OPERATION)
     │  │  │  │       │  1001 │ALU_LTU│ x1 = x2  <  x3 │
     │  │  │  │       │  1010 │ALU_GES│ x1 = x2 >=  x  │ (SIGNED OPERATION)
     │  │  │  │       │  1011 │ALU_GEU│ x1 = x2 >=  x  │
     │  │  │  │       │  1100 │ALU_EQ │ x1 = x2 ==  x  │
     │  │  │  │       │  1101 │ALU_NE │ x1 = x2 !=  x  │
     │  │  │  │       │  1110 │ /--/  │  /----------/  │
     │  │  │  │       │  1111 │ /--/  │  /----------/  │
     │  │  │  │       └───────┴───────┴────────────────┘
     │  │  │  └─ [WS] data source for writing to a register file:
     │  │  │     ┌────┬─────────────────────────┐
     │  │  │     │ WS │ interpritation          │
     │  │  │     ├────┼─────────────────────────┤
     │  │  │     │ 00 │ constant from Immidiate │
     │  │  │     │ 01 │ data from switches      │
     │  │  │     │ 10 │ ALU result              │
     │  │  │     │ 11 │ not set                 │
     │  │  │     └────┴─────────────────────────┘
     │  │  └─ [WE] premission to write to register file
     │  └─ [C] if 1 - do codition jump
     └─ [B] if 1 - do uncodition jump 

    Attributes
    ----------
    B      :  int
        uncodition jump
    C      :  int
        codition jump
    WE     :  int
        premission to write to register file
    WS     :  int
        data source for writing to a register file
    ALUop  :  int
        ALU the operation code
    RA1    :  int
        read address for first operand
    RA2    :  int
        read address for second operand
    WA     :  int
        write address
    const  :  int
        Immidiate
    """

    def __init__(self):
        self.B = 0
        self.C = 0
        self.WE = 0
        self.WS = 2
        self.ALUop = 0
        self.RA1 = 0
        self.RA2 = 0
        self.WA = 0
        self.const = 0

    def compile(self):
        bin_code =  bin_extend(self.B, 1) \
               + bin_extend(self.C, 1) \
               + bin_extend(self.WE, 1) \
               + bin_extend(self.WS, 2) \
               + bin_extend(self.ALUop, 4) \
               + bin_extend(self.RA1, 5) \
               + bin_extend(self.RA2, 5) \
               + bin_extend(self.WA, 5) \
               + bin_extend(self.const, 8)
        hex_code = hex(int(bin_code, 2))[2:]
        hex_code = '0' * (8 - len(hex_code)) + hex_code
        # return hex_code
        return bin_code


class _ALU(object):
    def __init__(self):
        self.ALU_ADD = 0b0000
        self.ALU_SUB = 0b0001
        self.ALU_XOR = 0b0010
        self.ALU_OR  = 0b0011
        self.ALU_AND = 0b0100
        self.ALU_SRA = 0b0101
        self.ALU_SRL = 0b0110
        self.ALU_SLL = 0b0111
        self.ALU_LTS = 0b1000
        self.ALU_LTU = 0b1001
        self.ALU_GES = 0b1010
        self.ALU_GEU = 0b1011
        self.ALU_EQ  = 0b1100
        self.ALU_NE  = 0b1101

        self.ops = {
            'add': self.ALU_ADD,
            'sub': self.ALU_SUB,
            'xor': self.ALU_XOR,
            'or': self.ALU_OR,
            'and': self.ALU_AND,
            'sra': self.ALU_SRA,
            'srl': self.ALU_SRL,
            'sll': self.ALU_SLL,
            'lt' : self.ALU_LTS,
            'ltu': self.ALU_LTU,
            'ge' : self.ALU_GES,
            'geu': self.ALU_GEU,
            'eq': self.ALU_EQ,
            'ne': self.ALU_NE
        }

    def __getitem__(self, other):
        return self.ops[other]


ALU = _ALU()


class _RISCV(object):
    def __init__(self):
        pass

    def parse(self, line):
        match line.split():
            case 'nop', *ops:
                instr = self.NoInstructionPseudo(ops)
            case 'li', *ops:
                instr = self.LoadImmidiate(ops)
            case 'ls', *ops:
                instr = self.LoadSwitches(ops)
            case 'beq' | 'bne' | 'blt' | 'bge' | 'bltu' | 'bgeu' as op, *ops:
                instr = self.BranchIfOp(op, ALU[op[1:]], ops)
            case 'add' | 'sub' | 'xor' | 'or' | 'and' | 'sll' | 'srl' | 'sra' \
                 | 'slt' | 'slru' as op, *ops:
                instr = self.AluOp(op, ALU[op], ops)
            case 'j', *ops:
                instr = self.JumpPseudo(ops)
            case ops:
                raise RISCvSyntaxError(
                    '{YELLOW}illegal instruction {CYAN}`' + ops[0] \
                    + '`{RESET}', (0, 0))
                instr = None

        return instr

    @staticmethod
    def LoadImmidiate(ops):
        """
        LoadImmidiate command parser
        creates instruction to load immidiate value to register

        Usage:
         >> li [register] [immidiate]

        Example:
         >> li x3 0x123
        """
        if len(ops) != 2:
            raise RISCvSyntaxError(
                '{YELLOW}instruction {CYAN}`li`{YELLOW} expecting two operands'\
                '{WHITE}\n >> li {PURPLE}[register] [immidiate]{RESET}',
                (3, len(ops)))
        instruction = Instruction()
        reg, imm = ops
        reg = parse_reg(reg, 1)
        imm = parse_imm(imm, 2)
        instruction.WA = reg
        instruction.WS = 0
        instruction.const = imm
        instruction.WE = 1
        return instruction

    @staticmethod
    def LoadSwitches(ops):
        """
        LoadSwitches command parser
        creates instruction to load values from switches to register

        Usage:
         >> ls [register]

        Example:
         >> ls t0
        """
        if len(ops) != 1:
            raise RISCvSyntaxError(
                '{YELLOW}instruction {CYAN}`ls`{YELLOW} expecting one operand' \
                '{WHITE}\n >> ls {PURPLE}[register]{RESET}', (2, len(ops)))
            return None
        instruction = Instruction()
        reg, = ops
        reg = parse_reg(reg, 1)
        instruction.WA = reg
        instruction.WE = 1
        instruction.WS = 1
        return instruction

    @staticmethod
    def BranchIfOp(operation, ALUop, ops):
        """
        BranchIfOp command parser
        creates instruction that shift program counter to value in immidiate if
        values in registers are match alu operation command

        Usage:
         >> [operation] [reg1] [reg2] [immidiate]

        Example:
         >> beq s4 s7
        """
        if len(ops) != 3:
            raise RISCvSyntaxError(
                '{YELLOW}instruction {CYAN}`' + operation + \
                '`{YELLOW} expecting three operands{WHITE}\n >> ' + operation \
                + ' {PURPLE}[register1] [register2] [immidiate]{RESET}',
                (4, len(ops)))
            return None
        instruction = Instruction()
        reg1, reg2, imm = ops
        reg1 = parse_reg(reg1, 1)
        reg2 = parse_reg(reg2, 2)
        imm = parse_imm(imm, 3)
        instruction.C = 1
        instruction.ALUop = ALUop
        instruction.RA1 = reg1
        instruction.RA2 = reg2
        instruction.const = imm
        return instruction

    @staticmethod
    def AluOp(operation, ALUop, ops):
        """
        AluOp command parser
        creates instruction thad do ALU operation between registers and store
        result to register

        Usage:
         >> [operation] [write_reg] [read_reg_1] [read_reg_2]

        Example:
         >> add x3 t3 t4 
        """
        if len(ops) != 3:
            raise RISCvSyntaxError(
                '{YELLOW}instruction {CYAN}`' + operation + \
               '`{YELLOW} expecting three operands{WHITE}\n >> ' + operation + \
               ' {PURPLE}[write_reg] [read_reg_1] [read_reg_2]{RESET}',
               (4, len(ops)))
            return None
        instruction = Instruction()
        wreg, reg1, reg2 = ops
        wreg = parse_reg(wreg, 1)
        reg1 = parse_reg(reg1, 2)
        reg2 = parse_reg(reg2, 3)
        instruction.WE = 1
        instruction.ALUop = ALUop
        instruction.RA1 = reg1
        instruction.RA2 = reg2
        instruction.WA = wreg
        return instruction

    @staticmethod
    def JumpAndLink(ops):
        """
        JumpAndLink command parser
        creates instruction that shift program counter to value in immidiate and
        saves previous program counter value in register without any conditions

        Usage:
         >> jal [reg] [immidiate]
        """
        if len(ops) != 2:
            raise RISCvSyntaxError(
                '{YELLOW}instruction {CYAN}`jal`{YELLOW} expecting two operands'\
                '{WHITE}\n >> jal {PURPLE}[register] [immidiate]{RESET}',
                (3, len(ops)))
            return None
        instruction = Instruction()
        reg, imm = ops
        # try:
        # reg = parse_reg(reg)
        # imm = parse_imm(imm)

    @staticmethod
    def JumpPseudo(ops):
        """
        Jump pseudo instruction parser
        creates instruction that shift program counter to value in immidiate

        Usage:
         >> j [immidiate]

        Example:
         >> j -4
        """

        if len(ops) != 1:
            raise RISCvSyntaxError(
                '{YELLOW}instruction {CYAN}`j`{YELLOW} expecting one' \
                ' operand{WHITE}\n >> j {PURPLE}[immidiate]{RESET}',
                (2, len(ops)))
            return None
        instruction = Instruction()
        imm, = ops
        imm = parse_imm(imm, 1)
        instruction.B = 1
        instruction.const = imm
        return instruction

    @staticmethod
    def NoInstructionPseudo(ops):
        """
        Empty pseudo instruction parser
        crestes `add x0 x0 x0` instruction

        Usage:
         >> nop

        Example:
         >> nop
        """

        if len(ops) != 0:
            raise RISCvSyntaxError(
                '{YELLOW}instruction {CYAN}`nop`{YELLOW} not expecting ' \
                'operands{WHITE}\n >> nop{RESET}', (1, len(ops)))
        instruction = Instruction()
        return RISCV.parse('add x0 x0 x0')

RISCV = _RISCV()


# ------------------------------- UTILS FUNCTIONS ------------------------------
def contains_only(st, available):
    if len(set(st) | set(available)) > len(set(available)):
        return False
    else:
        return True


def bin_extend(num, cnt):
    if num < 0:
        num = pow(2, cnt) + num
    st = bin(num)[2:]
    return '0' * (cnt - len(st)) + st


# ------------------------------- PARSE FUNCTIONS ------------------------------
def parse_reg(st, error_index):
    REGISTER_INDEX_MESSAGE = \
        '{YELLOW}Invalid register index: {CYAN}`{__reg__}`{RESET}'
    REGISTER_LIMIT_MESSAGE = \
        '{YELLOW}Invalid register index: {CYAN}`{__reg__}`{YELLOW}, ' \
        'limit is {PURPLE}{__limit__}{RESET}'
    REGISTER_FORMAT_MESSAGE = \
        '{YELLOW}Invalid register format: {CYAN}`{__reg__}`{RESET}'

    if not contains_only(st.lower(), '0123456789rasgfptxzeo'):
        raise RegisterError(REGISTER_FORMAT_MESSAGE.replace('{__reg__}', st),
            (error_index, error_index))
    match st.lower():
        case 'zero':
            return parse_reg('x0', error_index)
        case 'ra':
            return parse_reg('x1', error_index)
        case 'sp':
            return parse_reg('x2', error_index)
        case 'gp':
            return parse_reg('x3', error_index)
        case 'tp':
            return parse_reg('x4', error_index)
        case 't0' | 't1' | 't2' as T:
            return parse_reg('x' + str(int(T[1]) + 5), error_index)
        case 's0' | 'fp':
            return parse_reg('x8', error_index)
        case 's1':
            return parse_reg('x9', error_index)
        case _:
            pass

    if st.startswith(('a', 't', 'x')) and st[1].isdigit():
        try:
            reg_cnt = int(st[1:])
        except ValueError:
            raise RegisterError(REGISTER_INDEX_MESSAGE.replace( \
                '{__reg__}', st[1:]), (error_index, error_index))
        match st[0]:
            case 'a':
                if reg_cnt > 7:
                    raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
                        '{__reg__}', st[1:]).replace('{__limit__}', '7'),
                        (error_index, error_index))
                return parse_reg('x' + str(reg_cnt + 10), error_index)
            case 't':
                if reg_cnt > 6:
                    raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
                        '{__reg__}', st[1:]).replace('{__limit__}', '6'),
                        (error_index, error_index))
                return parse_reg('x' + str(reg_cnt + 25), error_index)
            case 's':
                if reg_cnt > 11:
                    raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
                        '{__reg__}', st[1:]).replace('{__limit__}', '11'),
                        (error_index, error_index))
                return parse_reg('x' + str(reg_cnt + 16), error_index)
            case 'x':
                if reg_cnt > 31:
                    raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
                        '{__reg__}', st[1:]).replace('{__limit__}', \
                        str(REGISTER_NUMBER - 1)), (error_index, error_index))
                return reg_cnt
    else:
        raise RegisterError(REGISTER_FORMAT_MESSAGE.replace('{__reg__}', st),
            (error_index, error_index))


def parse_imm(st, error_index):
    IMMIDIATE_ERROR_MESSAGE = '{YELLOW}Invalid Immidiate value with base ' \
        '{PURPLE}{__base__}: {CYAN}`{__value__}`{RESET}'
    IMMIDIATE_LIMIT_MESSAGE = '{YELLOW}Immidiate value to big: ' \
        '{CYAN}`{__value__}`{YELLOW}, limit is {PURPLE}' \
        + f'[{-IMMIDIATE_LIMIT - 1} : {IMMIDIATE_LIMIT}]' + '{RESET}'
    IMMIDIATE_ERROR_BASE = '{YELLOW}Invalid Immidiate value: ' \
        '{CYAN}`{__value__}`{RESET}'

    sign = 1
    if st[0] == '-':
        sign = -1
        st = st[1:]
    if st[0] == '+':
        st = st[1:]
    match st[0:2]:
        case '0x' | '0X':
            i = st[2:]
            base = 16
            if not contains_only(i, '0123456789abcdefABCDEF'):
                raise ImmidiateError(IMMIDIATE_ERROR_MESSAGE.replace( \
                    '{__base__}', '16').replace('{__value__}', i),
                    (error_index, error_index))
        case '0o' | '0O':
            i = st[2:]
            base = 8
            if not contains_only(i, '01234567'):
                raise ImmidiateError(IMMIDIATE_ERROR_MESSAGE.replace( \
                   '{__base__}', '8').replace('{__value__}', i),
                    (error_index, error_index))
        case '0b' | '0B':
            i = st[2:]
            base = 2
            if not contains_only(i, '01'):
                raise ImmidiateError(IMMIDIATE_ERROR_MESSAGE.replace( \
                   '{__base__}', '2').replace('{__value__}', i),
                    (error_index, error_index))
        case _:
            i = st
            base = 10
    try:
        ans = int(i, base=base) * sign
        if not -IMMIDIATE_LIMIT - 1 <= ans <= IMMIDIATE_LIMIT:
            raise ImmidiateError(IMMIDIATE_LIMIT_MESSAGE.replace( \
                '{__value__}', i), (error_index, error_index))
        return ans
    except ValueError:
        raise ImmidiateError(IMMIDIATE_ERROR_BASE.replace('{__value__}', i),
            (error_index, error_index))


def create_arrow(line, index):
    def _find_non_space(st, start):
        for _i in range(start, len(st)):
            if st[_i] != ' ':
                return _i

    split = line.split()
    size = list(map(len, split))
    word_start = []
    word_end = []
    word_index = 0
    for i in range(len(split)):
        word_start.append(_find_non_space(line, word_index))
        word_end.append(word_start[-1] + size[i])
        word_index = word_end[-1]
    if index[0] > len(split):
        arrow = ' ' * len(line) + ' '
    else:
        arrow = ' ' * word_start[index[0]]
    if index[0] > index[1]:
        arrow += '{GREEN}^~~{RESET}'
    else:
        arrow += '{GREEN}^' + '~' \
            * (word_end[index[1]] - word_start[index[0]] - 1) + '{RESET}'
    arrow += '\n'
    return arrow.format(RESET=color.RESET, GREEN=color.GREEN)


def compile(prog, fname):
    SYNTAX_ERROR_MESSAGE = \
        "{WHITE}{fname}:{line_num}{RED} error: {WHITE}{exc_name}{RESET}\n" \
        "{exc_message}{RESET}\n{WHITE}{line_num:>5} |  {RESET}{line}\n" \
        "{WHITE}      |  {error_arrow}{RESET}"
    ERROR_LIMIT_MESSAGE = \
        "{WHITE}{fname}:{line_num} {CYAN}note: {WHITE}compilation terminated " \
        "due to error limit = 20{RESET}"

    error_cnt = 0
    ans = []
    for ind, line in enumerate(prog.split('\n')):
        line = line.expandtabs(4)
        if '#' in line:
            line = line[:line.index('#')]
        if len(line) == 0:
            continue
        try:
            instr = RISCV.parse(line)
            ans.append(instr)
        except RISCvSyntaxError as exc:
            error_cnt += 1
            if error_cnt <= 20:
                exc_message = exc.what.format(BLACK=color.BLACK,
                                              RED=color.RED,
                                              GREEN=color.GREEN,
                                              YELLOW=color.YELLOW,
                                              BLUE=color.BLUE,
                                              PURPLE=color.PURPLE,
                                              CYAN=color.CYAN,
                                              WHITE=color.WHITE,
                                              RESET=color.RESET)
                print(SYNTAX_ERROR_MESSAGE.format(fname=fname, line_num=ind,
                                                  error_arrow=create_arrow( \
                                                    line, exc.index),
                                                  exc_name=exc.name,
                                                  exc_message=exc_message,
                                                  line=line,
                                                  BLACK=color.BLACK,
                                                  RED=color.RED,
                                                  GREEN=color.GREEN,
                                                  YELLOW=color.YELLOW,
                                                  BLUE=color.BLUE,
                                                  PURPLE=color.PURPLE,
                                                  CYAN=color.CYAN,
                                                  WHITE=color.WHITE,
                                                  RESET=color.RESET))
            else:
                print(ERROR_LIMIT_MESSAGE.format(fname=fname, line_num=ind))
                return None
    if error_cnt > 0:
        return None
    for i in range(len(ans)):
        ans[i] = ans[i].compile()
    return ans


def main():
    argv = sys.argv[1:]
    if len(argv) < 1:
        print("{WHITE}usage: python asm.py {PURPLE}[program.s] {YELLOW}..." \
            "{RESET}".format(WHITE=color.WHITE, PURPLE=color.PURPLE, \
                YELLOW=color.YELLOW, RESET=color.RESET))
        print("  where {PURPLE}[program.s]{RESET} is file with RISC-V " \
            "assembly code".format(PURPLE=color.PURPLE, RESET=color.RESET))
    for file_name in argv:
        try:
            if not file_name.endswith('.s'):
                if '.' not in file_name:
                    print('unsupported file type')
                else:
                    print(f'unsupported file type: .{file_name.split(".")[-1]}')
                continue
            with open(file_name, 'r') as file:
                text = file.read()
            obj = compile(text, file_name)
            if obj is None:
                print("{WHITE}{fname}: compilation {RED}error{RESET}".format(
                    fname=file_name, RED=color.RED, RESET=color.RESET,
                    WHITE=color.WHITE))
                continue
            with open(file_name[:-2] + '.bin', 'w') as file:
                file.write('\n'.join(obj))
            print( \
                "{WHITE}{fname}: compilation {GREEN}succsessfull{RESET}".format(
                fname=file_name, GREEN=color.GREEN, RESET=color.RESET,
                WHITE=color.WHITE))
        except FileNotFoundError:
            print(f'file not found: {file_name}')


if __name__ == '__main__':
    main()
