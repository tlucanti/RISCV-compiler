# -*- coding: utf-8 -*-
# @Author: kostya
# @Date:   2021-12-08 20:56:10
# @Last Modified by:   kostya
# @Last Modified time: 2022-01-28 09:10:23

import sys
import platform
import re

error_index = 0
line_start = 0


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
        self.name = '[y]Syntax error[]'
        self.what = what
        self.index = error_index


class RISCvImmediateError(RISCvSyntaxError):
    def __init__(self, what):
        super().__init__(what)
        self.name = '[y]Immediate value error[]'


class RISCvRegisterError(RISCvSyntaxError):
    def __init__(self, what):
        super().__init__(what)
        self.name = '[y]Register name error[]'


class RISCvLabelError(RISCvSyntaxError):
    def __init__(self, what):
        super().__init__(what)
        self.name = '[y]Invalid label name[]'


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
        imm = str(imm)
        if not contains_only(imm, '+-0123456789bBoOxXabcdefABCDEF'):
            raise RISCvSyntaxError(f'[w]invalid immediate literal: [c]`{imm}`[]')
        self.imm = None
        if re.fullmatch(r'^[-+]?[0-9]+$', imm) is not None:
            imm = int(imm)
        elif re.fullmatch(r'^[-+]?0[xX][0-9a-fA-F]+$', imm) is not None:
            imm = int(imm, 16)
        elif re.fullmatch(r'^[-+]?0[oO][0-7]+$', imm) is not None:
            imm = int(imm, 8)
        elif re.fullmatch(r'^[-+]?0[bB][0-1]+$', imm) is not None:
            imm = int(imm, 2)
        else:
            raise RISCvSyntaxError(f'[w]invalid immediate literal: [c]`{imm}`[]')

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
            self.imm_bin = twos_complement(imm, 5)
        elif imm_type == 'any':
            rng = AlwaysContains()
        elif imm_type == 'li':
            if imm < 0:
                rng = range(-2147483648, 2147483648)
            else:
                rng = range(0, 4294967296)
        else:
            raise SystemError(
                f'[r][internal error]: Immediate::__init__ (invalid immediate type: {imm_type})[]')

        self.imm_int = imm
        if imm not in rng:
            raise RISCvImmediateError(
                f'[r]immediate of type {imm_type} is out of range {str(rng)[5:]}[]')

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
    message = '[w]register [c]`{reg}`[w] is not recognized[]'

    def __init__(self, reg):
        if reg not in self.reg_map:
            raise RISCvRegisterError(self.message.format(reg=reg))
        self.reg = self.reg_map[reg]
        self.str = reg

    def __bytes__(self):
        return '{reg:05b}'.format(reg=self.reg)

    def __repr__(self):
        return self.__bytes__()


class CsrRegister(Register):

    reg_map = {
        'mie': 0x304,
        'mtvec': 0x305,
        'mscratch': 0x340,
        'mepc': 0x341,
        'mcause': 0x342
    }
    message = '[w]csr register [c]`{reg}`[w] is not recognized[]'

    def __init__(self, reg):
        super().__init__(reg)

    def __bytes__(self):
        return '{reg:012b}'.format(reg=self.reg)


class Label:
    labels = dict()

    @staticmethod
    def create(label, cnt):
        if re.fullmatch(r'^[0-9a-zA-Z_]+$', label) is None:
            raise RISCvLabelError(
                f'[w]label name can contain only digits and letters: [c]`{label}`[]')
        if label in Label.labels:
            raise RISCvLabelError(f'[w]label [c]`{label}`[w] redefined[]')
        Label.labels[label] = cnt

    def __init__(self, label):
        if re.fullmatch(r'^[0-9a-zA-Z_]+$', label) is None:
            raise RISCvLabelError(
                f'[w]label name can contain only digits and letters: [c]`{label}`[]')
        self.label = label

    def to_immediate(self, imm_type, cnt, label_index):
        global error_index

        error_index = label_index
        if self.label not in self.labels:
            raise RISCvLabelError(f'[w]label [c]`{self.label}`[w] is not defined[]')
        imm = self.labels[self.label] - cnt
        if imm_type == 'la':
            imm += 1
            imm <<= 1
            imm_type = 'I'
        return Immediate(imm << 1, imm_type)


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
              'xori', 'ori', 'andi',
              'ebreak', 'mret', 'csrrw', 'csrrs', 'csrrc'}
    S_inst = {'sb', 'sh', 'sw'}
    B_inst = {'beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu'}
    U_inst = {'lui', 'auipc'}
    J_inst = {'jal'}
    Pseudo_inst = {'li', 'j', 'la', 'csrr', 'csrw'}

    # Pseudo_inst = {'la', 'nop', 'mv', 'not', 'neg', 'seqz', 'sneq', 'sltz',
    #                'sgez',
    #                'beqz', 'bnez', 'blez', 'bgez', 'bltz',
    #                'bgtz', 'ble', 'bgtu', 'bleu', 'j', 'jr', 'ret', 'call',
    #                'tail'}

    def __init__(self):

        self.imm = None
        self.funct7 = None
        self.funct3 = None
        self.rs1 = None
        self.rs2 = None
        self.rd = None
        self.label = None
        self.opcode = None
        self.type = None
        self.op = None
        self.reg = None
        self.instr_cnt = None
        self.line = None
        self.label_index = None

    def __repr__(self):
        return self.line

    def parse(self, line, instr_cnt):
        global error_index, line_start

        self.line = line
        self.instr_cnt = instr_cnt
        split = line.split()
        error_index = 0
        line_start = 0
        while len(split) > 0 and split[0].endswith(':'):
            Label.create(split[0][:-1], instr_cnt)
            error_index += 1
            del split[0]
        if len(split) == 0:
            return []

        line_start = error_index
        for label in split:
            if label.endswith(':'):
                raise RISCvLabelError(
                    f'[w]label [c]`{label[:-1]}`[w] in the middle of the instruction[]')
            error_index += 1
        error_index = line_start

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
                f'[w]illegal instruction [c]`{op[0]}`[]')
        return instr

    def check_args(self, line, fmt):
        global error_index, line_start

        line = line[1:]
        for i in range(len(fmt)):
            error_index = line_start + i + 1
            if i >= len(line):
                if fmt[i] == 'imm':
                    raise RISCvSyntaxError('[w]expected immediate value[]')
                elif fmt[i] == 'reg':
                    raise RISCvSyntaxError('[w]expected register[]')
                elif fmt[i] == 'label':
                    raise RISCvSyntaxError('[w]expected label[]')
                elif fmt[i] == 'offset':
                    raise RISCvSyntaxError('[w]expected offset value[]')
                else:
                    raise SystemError(
                        f'[r][internal error]: compiler::Instruction::check_args (invalid format checker value {fmt[i]})[]')
            elif fmt[i] == 'imm':
                _ = Immediate(line[i], 'any')
            elif fmt[i] == 'reg':
                _ = Register(line[i])
            elif fmt[i] == 'label':
                self.label_index = error_index
                _ = Label(line[i])
            elif fmt[i] == 'offset':
                _ = self.parse_offset(line[i])
            elif fmt[i] == 'csr':
                _ = CsrRegister(line[i])
            else:
                raise SystemError(
                    f'[r][internal error]: compiler::Instruction::check_args (invalid format checker value {fmt[i]})[]')

    def compile(self, instr_cnt):
        global error_index, line_start

        imm = self.imm
        funct7 = self.funct7
        funct3 = self.funct3
        rs1 = self.rs1
        rs2 = self.rs2
        rd = self.rd
        label = self.label
        opcode = self.opcode
        reg = self.reg

        if self.type == 'la':
            error_index = line_start + 2
            imm = label.to_immediate('la', instr_cnt, self.label_index)
            self.type = 'I'

        if self.type == 'R':
            instr_bin = f'{funct7}{rs2}{rs1}{funct3}{rd}{opcode}'
        elif self.type == 'I':
            instr_bin = f'{imm}{rs1}{funct3}{rd}{opcode}'
        elif self.type == 'S':
            instr_bin = f'{imm[11:5]}{rs2}{rs1}{funct3}{imm[4:0]}{opcode}'
        elif self.type == 'B':
            error_index = line_start + 3
            imm = label.to_immediate('B', instr_cnt, self.label_index)
            instr_bin = f'{imm[11]}{imm[9:4]}{rs2}{rs1}{funct3}{imm[3:0]}{imm[10]}{opcode}'
        elif self.type == 'U':
            instr_bin = f'{imm}{reg}{opcode}'
        elif self.type == 'J':
            error_index = line_start + 2
            imm = label.to_immediate('J', instr_cnt, self.label_index)
            instr_bin = f'{imm[19]}{imm[9:0]}{imm[10]}{imm[18:11]}{reg}{opcode}'
        else:
            raise SystemError(f'[r][internal error]: compiler::Instruction::compile (invalid isntruction type {self.type})[]')

        return instr_bin

    @staticmethod
    def parse_offset(offset):
        split = offset.split('(')
        if len(split) != 2:
            raise RISCvSyntaxError(f'[w]invalid offset format: [c]`{offset}`[]')
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

        self.type = 'R'
        self.op = line[0]

        self.funct7 = op_ht[self.op].funct7
        if self.op in ('slli', 'srli', 'srai'):
            self.check_args(line, ('reg', 'reg', 'imm'))
            self.rs2 = Immediate(line[3], 'shift')
        else:
            self.check_args(line, ('reg', 'reg', 'reg'))
            self.rs2 = Register(line[3])

        self.rs1 = Register(line[2])
        self.funct3 = op_ht[self.op].funct3
        self.rd = Register(line[1])
        self.opcode = op_ht[self.op].opcode

        return [self]

    def i_type(self, line):

        op_ht = {
            'jalr': OpHt(funct3=0b000, opcode=0b1100111),
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
            'andi': OpHt(funct3=0b111, opcode=0b0010011),
            'mret': OpHt(funct3=0b000, opcode=0b1110011),
            'csrrw': OpHt(funct3=0b001, opcode=0b1110011),
            'csrrs': OpHt(funct3=0b010, opcode=0b1110011),
            'csrrc': OpHt(funct3=0b011, opcode=0b1110011),
            'ebreak': OpHt(funct3=0b000, opcode=0b1110011)
        }

        self.type = 'I'
        self.op = line[0]

        if self.op in {'mret', 'ebreak'}:
            self.check_args(line, ())
            if self.op == 'mret':
                self.imm = Immediate(0, 'I')
            elif self.op == 'ebreak':
                self.imm = Immediate(1, 'I')
            else:
                raise SyntaxError(f'[r][internal error] compiler::Instruction::i_type (invalid system instruction {self.op})[]')
            self.rs1 = Register('x0')
            self.rd = Register('x0')
        elif self.op in {'csrrw', 'csrrs', 'csrrc'}:
            self.check_args(line, ('reg', 'csr', 'reg'))
            self.imm = CsrRegister(line[2])
            self.rs1 = Register(line[3])
            self.rd = Register(line[1])
        elif self.op in {'lb', 'lh', 'lw', 'lbu', 'lhu'}:
            self.check_args(line, ('reg', 'offset'))
            self.imm, self.rs1 = self.parse_offset(line[2])
            self.imm = Immediate(self.imm, 'I')
            self.rs1 = Register(self.rs1)
            self.rd = Register(line[1])
        else:
            self.check_args(line, ('reg', 'reg', 'imm'))
            self.imm = Immediate(line[3], 'I')
            self.rs1 = Register(line[2])
            self.rd = Register(line[1])
        self.funct3 = op_ht[self.op].funct3

        self.opcode = op_ht[self.op].opcode

        return [self]

    def s_type(self, line):

        op_ht = {
            'sb': OpHt(funct3=0b000, opcode=0b0100011),
            'sh': OpHt(funct3=0b001, opcode=0b0100011),
            'sw': OpHt(funct3=0b010, opcode=0b0100011)
        }

        self.check_args(line, ('reg', 'offset'))

        self.type = 'S'
        self.op = line[0]
        self.imm, self.rs1 = self.parse_offset(line[2])
        self.imm = Immediate(self.imm, 'S')
        self.rs2 = Register(line[1])
        self.rs1 = Register(self.rs1)
        self.funct3 = op_ht[self.op].funct3
        self.opcode = op_ht[self.op].opcode

        return [self]

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

        self.type = 'B'
        self.op = line[0]
        self.label = Label(line[3])
        self.rs2 = Register(line[2])
        self.rs1 = Register(line[1])
        self.funct3 = op_ht[self.op].funct3
        self.opcode = op_ht[self.op].opcode

        return [self]

    def u_type(self, line):

        op_ht = {
            'lui': OpHt(opcode=0b0110111),
            'auipc': OpHt(opcode=0b0010111)
        }

        self.check_args(line, ('reg', 'imm'))

        self.type = 'U'
        self.op = line[0]
        self.reg = Register(line[1])
        self.imm = Immediate(line[2], 'U')
        self.opcode = op_ht[self.op].opcode

        return [self]

    def j_type(self, line):

        op_ht = {
            'jal': OpHt(opcode=0b1101111)
        }

        self.check_args(line, ('reg', 'label'))

        self.type = 'J'
        self.op = line[0]
        self.label = Label(line[2])
        self.reg = Register(line[1])
        self.opcode = op_ht[self.op].opcode

        return [self]

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
                lui = Instruction().parse(f'lui {reg.str} {upper_immediate}', self.instr_cnt)
                self.instr_cnt += 1
                rs1 = reg.str
            else:
                upper_immediate = 0
                imm = imm.imm_int
                lui = []
                rs1 = 'x0'
            self.instr_cnt += 1
            addi = Instruction().parse(f'addi {reg.str} {rs1} {imm - (upper_immediate << 12)}', self.instr_cnt)
            return lui + addi
        elif op == 'j':
            self.check_args(line, ('label',))
            instr = Instruction().parse(f'jal x0 {line[1]}', self.instr_cnt)
            for i in instr:
                i.line = ' '.join(line)
                i.label_index = 1
            return instr
        elif op == 'la':

            auipc = Instruction().parse(f'auipc {line[1]} 0', self.instr_cnt)
            for i in auipc:
                i.line = ' '.join(line)
                i.label_index = 2
            self.instr_cnt += 1
            op_ht = {
                'la': OpHt(funct3=0b000, opcode=0b0010011),
            }

            self.check_args(line, ('reg', 'label'))

            self.type = 'la'
            self.op = line[0]
            self.label = Label(line[2])
            self.rd = Register(line[1])
            self.rs1 = Register(line[1])
            self.funct3 = op_ht[self.op].funct3
            self.opcode = op_ht[self.op].opcode

            return auipc + [self]
        elif op == 'csrr':
            self.check_args(line, ('reg', 'csr'))
            return Instruction().parse(f'csrrs {line[1]} {line[2]} zero', self.instr_cnt)
        elif op == 'csrw':
            self.check_args(line, ('csr', 'reg'))
            return Instruction().parse(f'csrrw zero {line[1]} {line[2]}', self.instr_cnt)
        else:
            raise SystemError(f'[r][internal error] compiler::Instruction::pseudo_type (invalid pseudo instruction {op})[]')


def draw_arrow(line):
    line = line.split()
    space = 0
    for i in range(min(error_index, len(line))):
        space += len(line[i])
    space += error_index * 4
    if error_index >= len(line):
        arrow = '^~'
    elif len(line[error_index]) == 1:
        arrow = '^'
    else:
        arrow = '^' + (len(line[error_index]) - 2) * '~' + '^'
    return space * ' ' + arrow, space


def print_error(line, fname, line_num, exc):
    arrow, idx = draw_arrow(line)
    printc(f'[p]{fname}:{line_num}:{idx} [r]error: {exc.name}[]')
    printc(exc.what)
    printc('[w]{ln:>5} | {line}'.format(ln=line_num, line='    '.join(line.split())))
    printc('[w]      | [r]{arrow}'.format(arrow=arrow))


def compile_file(file):
    instructions = []
    line_num = 0
    true_line_num = 0
    Label.labels = dict()
    ok = True
    while True:
        line = file.readline()
        true_line_num += 1
        if line == '':
            break
        if '#' in line:
            line = line[:line.index('#')]
        line = line.expandtabs(4)
        line = line.replace(',', '')
        line = line.strip('\n')
        line = line.strip()
        try:
            parsed = Instruction().parse(line, line_num)
        except RISCvSyntaxError as exc:
            print_error(line, file.name, true_line_num, exc)
            ok = False
        instructions += parsed
        line_num += len(parsed)
    for i in range(len(instructions)):
        try:
            instructions[i] = instructions[i].compile(i)
            inst = instructions[i]
        except RISCvSyntaxError as exc:
            print_error(instructions[i].line, file.name, true_line_num, exc)
            ok = False
            inst = None
        if inst is not None and len(inst) != 32:
            raise SystemError("[r][internal error] compiler::compile_file (instruction length not equal 32)[]")
    if ok:
        instructions = ['{:08x}'.format(int(instr, 2)) for instr in instructions]
        return instructions
    else:
        return None


def printc(st):
    st = st.replace('[k]', Color.BLACK)
    st = st.replace('[r]', Color.RED)
    st = st.replace('[g]', Color.GREEN)
    st = st.replace('[y]', Color.YELLOW)
    st = st.replace('[b]', Color.BLUE)
    st = st.replace('[p]', Color.PURPLE)
    st = st.replace('[c]', Color.CYAN)
    st = st.replace('[w]', Color.WHITE)
    st = st.replace('[]', Color.RESET)
    st += Color.RESET
    print(st)


def main():
    if len(sys.argv) == 1:
        printc(f'[w]no input files')
        return
    for file in sys.argv[1:]:
        if not file.endswith('.s'):
            if '.' in file:
                printc(f'[r]error: [w]unsupported file format: [y].{file.split(".")[-1]}')
            else:
                printc(f'[r]error: [w]unsupported file format: [y]{file}')
            continue
        try:
            with open(file, 'r') as f:
                instr = compile_file(f)
                if instr is None:
                    return
        except FileNotFoundError:
            printc(f'[r]error: [w]cannot open [y]{f.name}')
        else:
            printc(f'[w]{f.name}: [g]compilation successful')
            with open(file[:-2] + '.bin', 'w') as outf:
                outf.write('\n'.join(instr))


if __name__ == '__main__':
    main()
