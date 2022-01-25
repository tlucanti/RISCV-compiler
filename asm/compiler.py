# -*- coding: utf-8 -*-
# @Author: kostya
# @Date:   2021-12-08 20:56:10
# @Last Modified by:   kostya
# @Last Modified time: 2022-01-24 17:01:30

import sys
import platform
import re

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


# ------------------------------- UTILS FUNCTIONS ------------------------------
def contains_only(st, available):
    if len(set(st) | set(available)) > len(set(available)):
        return False
    else:
        return True


def twos_complement(n, bits=32):
    n = int(n)
    mask = (1 << bits) - 1
    if n < 0:
        n = ((abs(n) ^ mask) + 1)
    return '{n:0{bits}b}'.format(n=n & mask, bits=bits)


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

    def __init__(self, imm, imm_type):
        if isinstance(imm, Label):
            imm = imm.label
        if not contains_only(imm, '+-0123456789bBoOxXabcdABCD'):
            raise RISCvSyntaxError(f'invalid immediate literal: {imm}')
        self.imm = None
        if re.fullmatch('^[-+]?[0-9]+$', str(imm)) is not None:
            self.imm_int = int(imm)
            imm = self.imm_int
        elif re.fullmatch('^[-+]?0[xX][0-9a-fA-F]+$', str(imm)) is not None:
            self.imm_int = int(imm, 16)
            imm = self.imm_int
        elif re.fullmatch('^[-+]?0[oO][0-7]+$', str(imm)) is not None:
            self.imm_int = int(imm, 8)
            imm = self.imm_int
        elif re.fullmatch('^[-+]?0[bB][0-1]+$', str(imm)) is not None:
            self.imm_int = int(imm, 2)
            imm = self.imm_int
        else:
            raise RISCvSyntaxError(f'invalid immediate literal: {imm}')
        if imm_type in 'IS':
            rng = range(-2048, 2048)
            self.imm_bin = twos_complement(imm, 12)
        elif imm_type in 'B':
            rng = range(-2048, 2048)
            self.imm_bin = twos_complement(imm, 12)
        elif imm_type in 'U':
            rng = range(0, 1048576)
            self.imm_bin = twos_complement(imm, 20)
        elif imm_type in 'J':
            rng = range(-524288, 524288)
            self.imm_bin = twos_complement(imm, 20)
        elif imm_type == 'shift':
            rng = range(0, 31)
            self.imm_bin = twos_complement(imm, 12)
        elif imm_type == 'any':
            rng = AlwaysContains()
        elif imm_type == 'li':
            if imm < 0:
                rng = range(-2147483648, 2147483648)
            else:
                rng = range(0, 4294967296)
        else:
            raise SystemError(
                f'[internal error]: Immediate::__init__ (invalid immediate type: {imm_type})')

        if imm not in rng:
            raise RISCvImmediateError(
                f'immediate of type {imm_type} is out of range {str(rng)[5:]}')

    def __bytes__(self):
        return self.imm_bin

    def __repr__(self):
        return self.__bytes__()

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.imm_bin[::-1][idx]
        else:
            return self.imm_bin[::-1][idx.stop:idx.start + 1][::-1]


class Register:
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
            raise RISCvRegisterError(f'register {reg} is not recognized')
        self.reg = self.reg_map[reg]
        self.str = reg

    def __bytes__(self):
        return '{reg:05b}'.format(reg=self.reg)

    def __repr__(self):
        return self.__bytes__()


class Label:

    labels = dict()

    @staticmethod
    def create(label, cnt):
        if not label.isalnum():
            raise RISCvLabelError(
                f'label name can contain only digits and letters: {label}')
        if label in Label.labels:
            raise RISCvLabelError(f'label {label} redefined')
        Label.labels[label] = cnt

    def __init__(self, label, cnt):
        if label in self.labels:
            if cnt is not None:
                self.label = self.labels[label] - cnt
        else:
            raise RISCvLabelError(f'label {label} is not defined')


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
    Pseudo_inst = {'li'}
    # Pseudo_inst = {'la', 'nop', 'mv', 'not', 'neg', 'seqz', 'sneq', 'sltz',
    #                'sgez',
    #                'beqz', 'bnez', 'blez', 'bgez', 'bltz',
    #                'bgtz', 'ble', 'bgtu', 'bleu', 'j', 'jr', 'ret', 'call',
    #                'tail'}

    def __init__(self):
        self.labels = dict()
        self.instr_cnt = None

    def parse(self, line, instr_cnt):
        global error_index

        self.instr_cnt = instr_cnt
        split = line.split()
        error_index = -1
        while len(split) > 0 and split[0].endswith(':'):
            error_index += 1
            Label.create(split[0][:-1], instr_cnt)
            del split[0]
        if len(split) == 0:
            return []

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
            instr = self.r_type(split)
        elif op in self.I_inst:
            instr = self.i_type(split)
        elif op in self.S_inst:
            instr = self.s_type(split)
        elif op in self.B_inst:
            instr = self.b_type(split)
        elif op in self.U_inst:
            instr = self.u_type(split)
        elif op in self.J_inst:
            instr = self.j_type(split)
        elif op in self.Pseudo_inst:
            instr = self.pseudo_type(split)
        else:
            raise RISCvSyntaxError(
                '{YELLOW}illegal instruction {CYAN}`' + op[0] + '`{RESET}')
        return instr

    def check_args(self, line, fmt):
        global error_index

        line = line[1:]
        for i in range(len(fmt)):
            error_index = i
            if i >= len(line):
                if fmt[i] == 'imm':
                    raise RISCvSyntaxError('expected immediate value')
                elif fmt[i] == 'reg':
                    raise RISCvSyntaxError('expected register')
                elif fmt[i] == 'label':
                    raise RISCvSyntaxError('expected label')
                elif fmt[i] == 'offset':
                    raise RISCvSyntaxError('expected offset value')
                else:
                    raise SystemError(
                        f'[internal error]: compiler::Instruction::check_args (invalid format checker value {fmt[i]})')
            elif fmt[i] == 'imm':
                _ = Immediate(line[i], 'any')
            elif fmt[i] == 'reg':
                _ = Register(line[i])
            elif fmt[i] == 'label':
                _ = Label(line[i], None)
            elif fmt[i] == 'offset':
                _ = self.parse_offset(line[i])
            else:
                raise SystemError(
                    f'[internal error]: compiler::Instruction::check_args (invalid format checker value {fmt[i]})')

    @staticmethod
    def parse_offset(offset):
        split = offset.split('(')
        if len(split) > 2:
            raise RISCvSyntaxError(f'invalid offset format: {offset}')
        imm_str, reg_str = split
        reg_str = reg_str[:-1]
        _ = Immediate(imm_str, 'any')
        _ = Register(reg_str)
        return imm_str, reg_str

    def r_type(self, line):

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

        op = line[0]

        funct7 = op_ht[op].funct7
        if op in ('slli', 'srli', 'srai'):
            self.check_args(line, ('reg', 'reg', 'imm'))
            rs2 = Immediate(line[3], 'shift')
        else:
            self.check_args(line, ('reg', 'reg', 'reg'))
            rs2 = Register(line[3])

        rs1 = Register(line[2])
        funct3 = op_ht[op].funct3
        rd = Register(line[1])
        opcode = op_ht[op].opcode

        instr_bin = f'{funct7}{rs2}{rs1}{funct3}{rd}{opcode}'
        return [instr_bin]

    def i_type(self, line):

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

        op = line[0]
        if op in {'lb', 'lh', 'lw', 'lbu', 'lhu'}:
            self.check_args(line, ('reg', 'offset'))
            imm, rs1 = self.parse_offset(line[2])
            imm = Immediate(imm, 'I')
            rs1 = Register(rs1)
        else:
            self.check_args(line, ('reg', 'reg', 'imm'))
            imm = Immediate(line[3], 'I')
            rs1 = Register(line[2])
        funct3 = op_ht[op].funct3
        rd = Register(line[1])
        opcode = op_ht[op].opcode

        instr_bin = f'{imm}{rs1}{funct3}{rd}{opcode}'
        return [instr_bin]

    def s_type(self, line):

        op_ht = {
            'sb': OpHt(funct3=0b000, opcode=0b0100011),
            'sh': OpHt(funct3=0b001, opcode=0b0100011),
            'sw': OpHt(funct3=0b010, opcode=0b0100011)
        }

        self.check_args(line, ('reg', 'offset'))

        op = line[0]
        imm, rs1 = self.parse_offset(line[2])
        imm = Immediate(imm, 'S')
        rs2 = Register(line[1])
        rs1 = Register(rs1)
        funct3 = op_ht[op].funct3
        opcode = op_ht[op].opcode

        instr_bin = f'{imm[11:5]}{rs2}{rs1}{funct3}{imm[4:0]}{opcode}'
        return [instr_bin]

    def b_type(self, line):

        op_ht = {
            'beq': OpHt(funct3=0b000, opcode=0b1100011),
            'bne': OpHt(funct3=0b001, opcode=0b1100011),
            'blt': OpHt(funct3=0b100, opcode=0b1100011),
            'bge': OpHt(funct3=0b101, opcode=0b1100011),
            'bltu': OpHt(funct3=0b110, opcode=0b1100011),
            'bgeu': OpHt(funct3=0b111, opcode=0b1100011)
        }

        self.check_args(line, ('reg', 'reg', 'label'))

        op = line[0]
        label = Label(line[3], self.instr_cnt)
        imm = Immediate(label, 'B')
        rs2 = Register(line[2])
        rs1 = Register(line[1])
        funct3 = op_ht[op].funct3
        opcode = op_ht[op].opcode

        instr_bin = f'{imm[11]}{imm[19:4]}{rs2}{rs1}{funct3}{imm[3:0]}{imm[10]}{opcode}'
        return [instr_bin]

    def u_type(self, line):

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

    def j_type(self, line):

        op_ht = {
            'jal': OpHt(opcode=0b1101111)
        }

        self.check_args(line, ('reg', 'label'))

        op = line[0]
        imm = Immediate(line[2], 'J')
        reg = Register(line[1])
        opcode = op_ht[op].opcode

        instr_bin = f'{imm[19]}{imm[9:0]}{imm[10]}{imm[18:11]}{reg}{opcode}'
        return [instr_bin]

    def pseudo_type(self, line):
        op = line[0]

        if op == 'li':
            self.check_args(line, ('reg', 'imm'))
            reg = Register(line[1])
            imm = Immediate(line[2], 'li')
            if 2048 <= imm.imm_int or imm.imm_int < -2048:
                imm = twos_complement(imm.imm_int, 32)
                imm = int(imm, 2)
                upper_immediate = imm >> 12
                if imm - (upper_immediate << 12) >= 2048:
                    upper_immediate += 1
                elif imm - (upper_immediate << 12) < -2048:
                    upper_immediate -= 1
                lui = self.parse(f'lui {reg.str} {upper_immediate}', self.instr_cnt)
                rs1 = reg.str
            else:
                upper_immediate = 0
                imm = imm.imm_int
                lui = []
                rs1 = 'x0'
            self.instr_cnt += 1
            addi = self.parse(f'addi {reg.str} {rs1} {imm - (upper_immediate << 12)}', self.instr_cnt)
            return lui + addi


def compile_file(file):
    instr = Instruction()
    instructions = []
    line_num = 0
    while True:
        line = file.readline()
        if line == '':
            return instructions
        if '#' in line:
            line = line[:line.index('#')]
        line = line.expandtabs(4)
        line = line.replace(',', '')
        line = line.strip('\n')
        line = line.strip()
        compiled = instr.parse(line, line_num)
        for inst in compiled:
            if len(inst) != 32:
                raise SystemError("[internal error] compiler::compile_file (instruction length not equal 32)")
        compiled = ['{:08x}'.format(int(instr, 2)) for instr in compiled]
        instructions += compiled
        line_num += len(compiled)


def main():
    if len(sys.argv) == 1:
        print('no input files')
        return
    for file in sys.argv[1:]:
        if not file.endswith('.s'):
            if '.' in file:
                print(f'unsupported file format: .{file.split(".")[-1]}')
            else:
                print(f'unsupported file format: {file}')
            continue
        try:
            with open(file, 'r') as f:
                print(f'started compiling {file}')
                instr = compile_file(f)
        except FileNotFoundError:
            print(f'cannot open {f.name}')
        else:
            print('compilation successful')
            with open(file[:-2] + '.bin', 'w') as outf:
                outf.write('\n'.join(instr))


if __name__ == '__main__':
    main()
