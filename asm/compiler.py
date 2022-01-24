# -*- coding: utf-8 -*-
# @Author: kostya
# @Date:   2021-12-08 20:56:10
# @Last Modified by:   kostya
# @Last Modified time: 2022-01-24 17:01:30

import sys
import platform

from asm import contains_only

error_index = 0


class Color:
    if platform.system() == 'Windows':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    BLACK = "\033[1;90m"
    RED = "\033[1;91m"
    GREEN = "\033[1;92m"
    YELLOW = "\033[1;93m"
    BLUE = "\033[1;94m"
    PURPLE = "\033[1;95m"
    CYAN = "\033[1;96m"
    WHITE = "\033[1;97m"
    RESET = "\033[0m"


class AlwaysContains:

    def __init__(self):
        pass

    def __contains__(self, _):
        return True


def twos_complement(n, bits=32):
    mask = (1 << bits) - 1
    if n < 0:
        n = ((abs(n) ^ mask) + 1)
    return bin(n & mask)[2:]


# ----------------------------- EXCEPTIONS CLASSES -----------------------------
class RISCvSyntaxError(SyntaxError):
    def __init__(self, what):
        super().__init__(what)
        self.name = 'Syntax error'
        self.what = what
        self.index = error_index


class RISCvImmediateError(RISCvSyntaxError):
    def __init__(self, what):
        super().__init__(what)
        self.name = 'Immediate value error'


class RISCvRegisterError(RISCvSyntaxError):
    def __init__(self, what):
        super().__init__(what)
        self.name = 'Register name error'


class RISCvLabelError(RISCvSyntaxError):
    def __init__(self, what):
        super().__init__(what)
        self.name = 'Invalid label name'


# ------------------------------ SUPPORT CLASSES -------------------------------
class ALU:
    ALU_ADD = 0b0000
    ALU_SUB = 0b0001
    ALU_XOR = 0b0010
    ALU_OR = 0b0011
    ALU_AND = 0b0100
    ALU_SRA = 0b0101
    ALU_SRL = 0b0110
    ALU_SLL = 0b0111
    ALU_LTS = 0b1000
    ALU_LTU = 0b1001
    ALU_GES = 0b1010
    ALU_GEU = 0b1011
    ALU_EQ = 0b1100
    ALU_NE = 0b1101


class Immediate:

    def __init__(self, imm, type):
        if not contains_only(imm, '+-0123456789bBoOxX'):
            raise RISCvSyntaxError(f'invalid immediate literal: {imm}')
        try:
            exec(f'imm = {imm}')
        except SyntaxError as exc:
            msg = str(exc).split()
            msg = f'{msg[0]} {msg[1]} {msg[2]}: {imm}'
            raise RISCvSyntaxError(msg)
        except NameError as exc:
            raise RISCvSyntaxError(f'invalid immediate literal: {imm}')
        if type in 'IS':
            rng = range(-2048, 2048)
            self.imm_bin = twos_complement(imm, 12)
        elif type in 'B':
            rng = range(-2048, 2048)
            self.imm_bin = twos_complement(imm, 12)
        elif type in 'U':
            rng = range(0, 1048576)
            self.imm_bin = twos_complement(imm, 20)
        elif type in 'J':
            rng = range(-524288, 524288)
            self.imm_bin = twos_complement(imm, 20)
        elif type == 'shift':
            rng = range(0, 31)
            self.imm_bin = twos_complement(imm, 12)
        elif type == 'check':
            rng = AlwaysContains()
        else:
            raise SystemError(
                '[internal error]: Immediate::__init__ (invalid immediate type')

        if imm not in rng:
            raise RISCvImmediateError(
                f'immediate of type {type} is out of range {str(rng)[5:]}')

    def __bytes__(self):
        return self.imm_bin

    def __repr__(self):
        return self.__bytes__()

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.imm_bin[::-1][idx]
        else:
            return self.imm_bin[::-1][idx.stop:idx.start][::-1]


class Register():
    reg_map = {
        'zero': 0, 'x0': 0,
        'ra': 1, 'x1': 1,
        'sp': 2, 'x2': 2,
        'gp': 3, 'x3': 3,
        'tp': 4, 'x4': 4,
        't0': 5, 'x5': 5,
        't1': 6, 'x6': 6,
        't2': 7, 'x7': 7,
        'fp': 8, 'x8': 8,
        's0': 8,
        's1': 9, 'x9': 9,
        'a0': 10, 'x10': 10,
        'a1': 11, 'x11': 11,
        'a2': 12, 'x12': 12,
        'a3': 13, 'x13': 13,
        'a4': 14, 'x14': 14,
        'a5': 15, 'x15': 15,
        'a6': 16, 'x16': 16,
        'a7': 17, 'x17': 17,
        's2': 18, 'x18': 18,
        's3': 19, 'x19': 19,
        's4': 20, 'x20': 20,
        's5': 21, 'x21': 21,
        's6': 22, 'x22': 22,
        's7': 23, 'x23': 23,
        's8': 24, 'x24': 24,
        's9': 25, 'x25': 25,
        's10': 26, 'x26': 26,
        's11': 27, 'x27': 27,
        't3': 28, 'x28': 28,
        't4': 29, 'x29': 29,
        't5': 30, 'x30': 30,
        't6': 31, 'x31': 31,
    }

    def __init__(self, reg):
        if reg not in self.reg_map:
            raise RISCvRegisterError(f'register {reg} is not recognozed')
        self.reg = self.reg_map[reg]

    def __bytes__(self):
        return '{reg:05b}'.format(reg=self.reg)

    def __repr__(self):
        return self.__bytes__()


class Funct3:

    def __init__(self, f3):
        self.f3 = f3

    def __bytes__(self):
        return '{f3:03b}'.format(f3=self.f3)

    def __repr__(self):
        return self.__bytes__()


class Funct7:

    def __init__(self, f7):
        self.f7 = f7

    def __bytes__(self):
        return '{f7:07b}'.format(f7=self.f7)

    def __repr__(self):
        return self.__bytes__()


class Opcode:

    def __init__(self, op):
        self.op = op

    def __bytes__(self):
        return '{op:07b}'.format(op=self.op)

    def __repr__(self):
        return self.__bytes__()


class OpHt:

    def __init__(self, opcode, funct7=None, funct3=None):
        self.funct7 = Funct7(funct7)
        self.funct3 = Funct3(funct3)
        self.opcode = Opcode(opcode)


# --------------------------- MAIN INSTRUCTION CLASS ---------------------------
class Instruction:
    R_inst = {'slli', 'srli', 'srai', 'add', 'sub', 'sll', 'slt', 'sltu', 'xor',
              'srl', 'sra', 'or', 'ans'}
    I_inst = {'jalr', 'lb', 'lh', 'lw', 'lbu', 'lhu', 'addi', 'slti', 'sltiu',
              'xori', 'ori', 'andi', 'fence', 'ecall',
              'ebreak'}
    S_inst = {'sb', 'sh', 'sw'}
    B_inst = {'beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu'}
    U_inst = {'lui', 'auipc'}
    J_inst = {'jal'}
    Pseudo_inst = {'la', 'nop', 'mv', 'not', 'neg', 'seqz', 'sneq', 'sltz',
                   'sgez',
                   'beqz', 'bnez', 'blez', 'bgez', 'bltz',
                   'bgtz', 'ble', 'bgtu', 'bleu', 'j', 'jr', 'ret', 'call',
                   'tail'}

    def __init__(self):
        self.labels = dict()

    def parse(self, line, instr_cnt):
        split = line.split()
        error_index = -1
        while split[0].endswith(':'):
            error_index += 1
            label = split[0][:-1]
            if not label.isalnum():
                raise RISCvLabelError(
                    f"label name can contain only digits and letters: {label}")
            if label in self.labels:
                raise RISCvLabelError(f"label {label} redefined")
            self.labels[label] = instr_cnt
            del split[0]
            if len(split) == 0:
                return None

        _error_index = error_index
        error_index -= 1
        for label in split:
            error_index += 1
            if label.endswith(':'):
                raise RISCvLabelError(
                    f'label {label} in the middle of the instruction')
        error_index = _error_index

        op = split[0].lower()
        if op in self.R_inst:
            instr = self.Rtype(split)
        elif op in self.I_inst:
            instr = self.Itype(split)
        elif op in self.S_inst:
            instr = self.Stype(split)
        elif op in self.B_inst:
            instr = self.Btype(split)
        elif op in self.U_inst:
            instr = self.Utype(split)
        elif op in self.J_inst:
            instr = self.Jtype(split)
        elif op in self.Pseudo_inst:
            instr = self.PseudoType(split)
        else:
            raise RISCvSyntaxError(
                '{YELLOW}illegal instruction {CYAN}`' + op[0] + '`{RESET}')
        return instr

    def check_args(self, line, fmt):
        for i in range(len(fmt)):
            if i >= len(line):
                if fmt[i] == 'imm':
                    raise RISCvSyntaxError('expected immediate value')
                elif fmt[i] == 'reg':
                    raise RISCvSyntaxError('expected register')
                elif fmt[i] == 'label':
                    raise RISCvSyntaxError('expected label')
                else:
                    raise SyntaxError(
                        f'unexpected format checker value: `{fmt[i]}`')
            elif fmt[i] == 'imm':
                continue
            elif fmt[i] == 'reg':
                continue
            elif fmt[i] == 'label':
                if fmt[i] in self.labels:
                    return self.labels[fmt[i]]
                else:
                    pass

    def parse_offset(self, offset):
        return 0, 0

    def Rtype(self, line):

        op_ht = {
            'slli': OpHt(funct7=0b0000000, funct3=0b001, opcode=0b0010011),
            'srli': OpHt(funct7=0b0000000, funct3=0b101, opcode=0b0010011),
            'srai': OpHt(funct7=0b0100000, funct3=0b101, opcode=0b0010011),
            'add': OpHt(funct7=0b0000000, funct3=0b000, opcode=0b0110011),
            'sub': OpHt(funct7=0b0100000, funct3=0b000, opcode=0b0110011),
            'sll': OpHt(funct7=0b0000000, funct3=0b001, opcode=0b0110011),
            'slt': OpHt(funct7=0b0000000, funct3=0b010, opcode=0b0110011),
            'sltu': OpHt(funct7=0b0000000, funct3=0b011, opcode=0b0110011),
            'xor': OpHt(funct7=0b0000000, funct3=0b100, opcode=0b0110011),
            'srl': OpHt(funct7=0b0000000, funct3=0b101, opcode=0b0110011),
            'sra': OpHt(funct7=0b0100000, funct3=0b101, opcode=0b0110011),
            'or': OpHt(funct7=0b0000000, funct3=0b110, opcode=0b0110011),
            'and': OpHt(funct7=0b0000000, funct3=0b111, opcode=0b0110011),
        }

        self.check_args(line, ('op', 'reg', 'reg', ('reg', 'imm')))

        op = line[0]
        funct7 = op_ht[op].funct7
        if op in ('slli', 'srli', 'srai'):
            rs2 = Immediate(line[3], 'shift')
        else:
            rs2 = Register(line[3])

        rs1 = Register(line[2])
        funct3 = op_ht[op].funct3
        rd = Register(line[1])
        opcode = op_ht[op].opcode

        instr_bin = f'{funct7}{rs2}{rs1}{funct3}{rd}{opcode}'
        return [instr_bin]

    def Itype(self, line):

        op_ht = {
            'lb': OpHt(funct3=0b000, opcode=0b0000011),
            'lh': OpHt(funct3=0b001, opcode=0b0000011),
            'lw': OpHt(funct3=0b010, opcode=0b0000011),
            'lbu': OpHt(funct3=0b100, opcode=0b0000011),
            'lhu': OpHt(funct3=0b101, opcode=0b0000011),
            'addi': OpHt(funct3=0b000, opcode=0b0010011),
            'slti': OpHt(funct3=0b010, opcode=0b0010011),
            'sltiu': OpHt(funct3=0b011, opcode=0b0010011),
            'xori': OpHt(funct3=0b100, opcode=0b0010011),
            'ori': OpHt(funct3=0b110, opcode=0b0010011),
            'andi': OpHt(funct3=0b111, opcode=0b0010011)
        }

        self.check_args(line, ('op', 'reg', 'reg', 'imm'))

        op = line[0]
        imm = Immediate(line[3], 'I')
        rs1 = Register(line[2])
        funct3 = op_ht[op].funct3
        rd = Register(line[1])
        opcode = op_ht[op].opcode

        instr_bin = f'{imm}{rs1}{funct3}{rd}{opcode}'
        return [instr_bin]

    def Stype(self, line):

        op_ht = {
            'sb': OpHt(funct3=0b000, opcode=0b0100011),
            'sh': OpHt(funct3=0b001, opcode=0b0100011),
            'sw': OpHt(funct3=0b010, opcode=0b0100011)
        }

        self.check_args(line, ('reg', 'offset'))

        op = line[0]
        imm, rs1 = self.parse_offset(line[2])
        imm = Immediate(imm, 'I')
        rs2 = Register(line[1])
        rs1 = Register(rs1)
        funct3 = op_ht[op].funct3
        opcode = op_ht[op].opcode

        instr_bin = f'{imm[11:5]}{rs2}{rs1}{funct3}{imm[4:0]}{opcode}'
        return [instr_bin]

    def Btype(self, line):

        op_ht = {
            'beq': OpHt(funct3=0b000, opcode=0b1100011),
            'bne': OpHt(funct3=0b001, opcode=0b1100011),
            'blt': OpHt(funct3=0b100, opcode=0b1100011),
            'bge': OpHt(funct3=0b101, opcode=0b1100011),
            'bltu': OpHt(funct3=0b110, opcode=0b1100011),
            'bgeu': OpHt(funct3=0b111, opcode=0b1100011)
        }

        imm = self.check_args(line, ('reg', 'reg', 'label', 'imm'))

        op = line[0]
        imm = Immediate(imm, 'B')
        rs2 = Register(line[2])
        rs1 = Register(line[1])
        funct3 = op_ht[op].funct3
        opcode = op_ht[op].opcode

        instr_bin = f'{imm[11]}{imm[19:4]}{rs2}{rs1}{funct3}{imm[3:0]}{imm[10]}'
        return [instr_bin]

    def Utype(self, line):

        op_ht = {
            'lui': OpHt(opcode=0b0110111),
            'auipc': OpHt(opcode=0b0010111)
        }

        self.check_args(line, ('reg', 'imm'))

        op = line[0]
        reg = Register(line[1])
        imm = Immediate(line[2], 'U')
        opcode = op_ht[op].opcode

        instr_bin = f'{imm}{reg}{opcode}'
        return [instr_bin]

    def Jtype(self, line):

        op_ht = {
            'jal': OpHt(opcode=0b1101111)
        }

        imm = self.check_args(line, ('reg', 'label'))

        op = line[0]
        imm = Immediate(line[2], 'J')
        reg = Register(line[1])
        opcode = op_ht[op].opcode

        instr_bin = f'{imm[19]}{imm[9:0]}{imm[10]}{imm[18:11]}{reg}{opcode}'
        return [instr_bin]

    def PseudoType(self, line):
        return None


def compile(file):
    instr = Instruction()
    instructions = []
    line_num = 0
    while True:
        line = file.readline()
        if line == '':
            return instr
        line = line.strip('\n')
        line = line.strip()
        if '#' in line:
            line = line[:line.index('#')]
        next = instr.parse(line, line_num)
        instructions += next
        line_num += len(next)


def main():
    if len(sys.argv) == 1:
        print('no input files')
        return
    for file in sys.argv:
        if not file.endswith('.s'):
            if '.' in file:
                print(f'unsupported file format: .{file.split(".")[-1]}')
            else:
                print(f'unsupported file format: {file}')
            continue
        try:
            with open(file, 'r') as f:
                instr = compile(f)
        except FileNotFoundError as exc:
            print(f'cannot open {f.name}')
        else:
            print('compilation successful')
            with open(file[:-2] + '.bin', 'w') as outf:
                outf.write('\n'.join(instr))


if __name__ == '__main__':
    main()
