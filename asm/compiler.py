# -*- coding: utf-8 -*-
# @Author: kostya
# @Date:   2021-12-08 20:56:10
# @Last Modified by:   kostya
# @Last Modified time: 2021-12-09 16:09:14

import sys
import platform

class Color():
	if platform.system() == 'Windows':
		import ctypes
		kernel32 = ctypes.windll.kernel32
		kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
	BLACK  = "\033[1;90m"
	RED    = "\033[1;91m"
	GREEN  = "\033[1;92m"
	YELLOW = "\033[1;93m"
	BLUE   = "\033[1;94m"
	PURPLE = "\033[1;95m"
	CYAN   = "\033[1;96m"
	WHITE  = "\033[1;97m"
	RESET  = "\033[0m"

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
		
# ------------------------------ SUPPORT CLASSES -------------------------------
class _ALU():
	ALU_ADD = 0b0000
	ALU_SUB = 0b0001
	ALU_XOR = 0b0010
	ALU_OR  = 0b0011
	ALU_AND = 0b0100
	ALU_SRA = 0b0101
	ALU_SRL = 0b0110
	ALU_SLL = 0b0111
	ALU_LTS = 0b1000
	ALU_LTU = 0b1001
	ALU_GES = 0b1010
	ALU_GEU = 0b1011
	ALU_EQ  = 0b1100
	ALU_NE  = 0b1101


class Immidiate():

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
						'{__base__}', '16').replace( \
						'{__value__}', i), \
						(error_index, error_index))
			case '0o' | '0O':
				i = st[2:]
				base = 8
				if not contains_only(i, '01234567'):
					raise ImmidiateError(IMMIDIATE_ERROR_MESSAGE.replace( \
					   '{__base__}', '8').replace( \
					   '{__value__}', i), \
						(error_index, error_index))
			case '0b' | '0B':
				i = st[2:]
				base = 2
				if not contains_only(i, '01'):
					raise ImmidiateError(IMMIDIATE_ERROR_MESSAGE.replace( \
					   '{__base__}', '2').replace( \
					   '{__value__}', i), \
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

	def __init__(self, imm, size):
		self.imm = imm
		self.imm_str = '{imm:0{size}b}'.format(size=size, imm=imm)

	def __getitem__(self, other):
		return imm_str[::-1][other.stop:other.start][::-1]


class Register():

	def __new__(self, reg):
		if reg is None:
			return None

		REGISTER_INDEX_MESSAGE = '{YELLOW}Invalid register index: ' \
			'{CYAN}`{__reg__}`{RESET}'
		REGISTER_LIMIT_MESSAGE = '{YELLOW}Invalid register index: ' \
			'{CYAN}`{__reg__}`{YELLOW}, ' \
			'limit is {PURPLE}{__limit__}{RESET}'
		REGISTER_FORMAT_MESSAGE = '{YELLOW}Invalid register format: ' \
			'{CYAN}`{__reg__}`{RESET}'

		if not contains_only(st.lower(), '0123456789rasgfptxzeo'):
			raise RegisterError(REGISTER_FORMAT_MESSAGE.replace('{__reg__}',st))
		match st.lower():
			case 'zero':
				return Register('x0')
			case 'ra':
				return Register('x1')
			case 'sp':
				return Register('x2')
			case 'gp':
				return Register('x3')
			case 'tp':
				return Register('x4')
			case 't0' | 't1' | 't2' as T:
				return Register('x' + str(int(T[1]) + 5))
			case 's0' | 'fp':
				return Register('x8')
			case 's1':
				return Register('x9')
			case _:
				pass

		if st.startswith(('a', 't', 'x')) and st[1].isdigit():
			try:
				reg_cnt = int(st[1:])
			except ValueError:
				raise RegisterError(REGISTER_INDEX_MESSAGE.replace('{__reg__}',\
					st[1:]))
			match st[0]:
				case 'a':
					if reg_cnt > 7:
						raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
							'{__reg__}', st[1:]).replace('{__limit__}', '7'))
					return Register('x' + str(reg_cnt + 10), error_index)
				case 't':
					if reg_cnt > 6:
						raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
							'{__reg__}', st[1:]).replace('{__limit__}', '6'))
					return Register('x' + str(reg_cnt + 25))
				case 's':
					if reg_cnt > 11:
						raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
							'{__reg__}', st[1:]).replace('{__limit__}', '11'))
					return Register('x' + str(reg_cnt + 16))
				case 'x':
					if reg_cnt > 31:
						raise RegisterError(REGISTER_LIMIT_MESSAGE.replace( \
							'{__reg__}', st[1:]).replace('{__limit__}', \
							str(REGISTER_NUMBER - 1)))
					Register.__init__(self, reg_cnt)
					return self
		else:
			raise RegisterError(REGISTER_FORMAT_MESSAGE.replace('{__reg__}',st))
		
	def __init__(self, reg_cnt):
		self.reg = reg_cnt

	def __str__(self):
		return '{reg:05b}'.format(reg=self.reg)
	

class Funct3():

	def __init__(self, f3):
		self.f3 = f3

	def __str__(self):
		return '{f3:03b}'.format(f3=self.f3)


class Funct7():

	def __init__(self, f7):
		self.f7 = f7

	def __str__(self):
		return '{f7:07b}'.format(f7=self.f7)


class Opcode():

	def __init__(self, op):
		self.op = op

	def __str__(self):
		return '{op:07b}'.format(op=self.op)


# --------------------------- MAIN INSTRUCTION CLASS ---------------------------
class Instruction():

	Rtype = {'slli', 'srli', 'srai', 'add', 'sub', 'sll', 'slt', 'sltu', 'xor',\
		'srl', 'sra', 'or', 'ans'}
	Itype = {'jalr', 'lb', 'lh', 'lw', 'lbu', 'lhu', 'addi', 'slti', 'sltiu', \
		'xori', 'ori', 'andi', 'fence', 'ecall', \
		'ebreak'}
	Stype = {'sb', 'sh', 'sw'}
	Btype = {'beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu'}
	Utype = {'lui', 'auipc'}
	Jtype = {'jal'}
	Pseudo = {'la', 'nop', 'mv', 'not', 'neg', 'seqz', 'sneq', 'sltz', 'sgez', \
		'beqz', 'bnez', 'blez', 'bgez', 'bltz', \
		'bgtz', 'ble', 'bgtu', 'bleu', 'j', 'jr', 'ret', 'call', 'tail'}

	class op_ht():
		def __init__(self, opcode, funct7=None, funct3=None):
			self.funct7 = Funct7(funct7)
			self.funct3 = Funct3(funct3)
			self.opcode = Opcode(opcode)

	def __init__(self):
		self.labels = dict()

	def parse(self, line, instr_cnt):
		split = line.split()
		while split[0].endswith(':'):
			label = split[0][:-1]
			if not label.isalnum():
				raise RISCvLabelError("label name can contain only digits and '\
					'letters", 0)
			if label in self.labels:
				raise RISCvLabelError("label redefined", lb)
			self.labels[label] = instr_cnt
			del split[0]
			if len(split) == 0:
				return None

		op = split[0].lower()
		if op in Rtype:
			instr = self.Rtype(split)
		elif op in Itype:
			instr = self.Itype(split)
		elif op in Stype:
			instr = self.Stype(split)
		elif op in Btype:
			instr = self.Btype(split)
		elif op in Utype:
			instr = self.Utype(split)
		elif op in Jtype:
			instr = self.Jtype(split)
		elif op in Pseudo:
			instr = self.Pseudo(split)
		else:
			raise RISCvSyntaxError(
				'{YELLOW}illegal instruction {CYAN}`' + ops[0] \
				+ '`{RESET}', (0, 0))
		return instr

		def Rtype(self, line):

			op_ht = {
				'slli': Op_ht(funct7=0b0000000, funct3=0b001, opcode=0b0010011),
				'srli': Op_ht(funct7=0b0000000, funct3=0b101, opcode=0b0010011),
				'srai': Op_ht(funct7=0b0100000, funct3=0b101, opcode=0b0010011),
				'add' : Op_ht(funct7=0b0000000, funct3=0b000, opcode=0b0110011),
				'sub' : Op_ht(funct7=0b0100000, funct3=0b000, opcode=0b0110011),
				'sll' : Op_ht(funct7=0b0000000, funct3=0b001, opcode=0b0110011),
				'slt' : Op_ht(funct7=0b0000000, funct3=0b010, opcode=0b0110011),
				'sltu': Op_ht(funct7=0b0000000, funct3=0b011, opcode=0b0110011),
				'xor' : Op_ht(funct7=0b0000000, funct3=0b100, opcode=0b0110011),
				'srl' : Op_ht(funct7=0b0000000, funct3=0b101, opcode=0b0110011),
				'sra' : Op_ht(funct7=0b0100000, funct3=0b101, opcode=0b0110011),
				'or'  : Op_ht(funct7=0b0000000, funct3=0b110, opcode=0b0110011),
				'and' : Op_ht(funct7=0b0000000, funct3=0b111, opcode=0b0110011),
			}

			self.check_args(line, ('op', 'reg', 'reg', ('reg', 'imm')))

			op = line[0]
			funct7 = op_ht[op].funct7
			if op in ('slli', 'srli', 'srai'):
				rs2 = Immidiate(line[3], 5)
			else:
				rs2 = Register(line[3])

			rs1 = Register(line[2])
			funct3 = op_ht[op].funct3
			rd = Register(line[1])
			opcode = op_ht[op].opcode

			instr_bin = '{funct7}{rs2}{rs1}{funct3}{rd}{opcode}'.format(
				funct7=funct7, \
				rs2=rs2, \
				rs1=rs1, \
				funct3=funct3, \
				opcode=opcode
			)
			return [instr]

		def Itype(self, line):

			op_ht = {
				'lb'	: Op_ht(funct3=0b000, opcode=0b0000011),
				'lh'	: Op_ht(funct3=0b001, opcode=0b0000011),
				'lw'	: Op_ht(funct3=0b010, opcode=0b0000011),
				'lbu'	: Op_ht(funct3=0b100, opcode=0b0000011),
				'lhu'	: Op_ht(funct3=0b101, opcode=0b0000011),
				'addi'	: Op_ht(funct3=0b000, opcode=0b0010011),
				'slti'	: Op_ht(funct3=0b010, opcode=0b0010011),
				'sltiu'	: Op_ht(funct3=0b011, opcode=0b0010011),
				'xori'	: Op_ht(funct3=0b100, opcode=0b0010011),
				'ori'	: Op_ht(funct3=0b110, opcode=0b0010011),
				'andi'	: Op_ht(funct3=0b111, opcode=0b0010011)
			}

			self.check_args(line, ('op', 'reg', 'reg', 'imm'))

			op = line[0]
			imm = Immidiate(line[3], 11)
			rs1 = Register(line[2])
			funct3 = op_ht[op].funct3
			rd = Register(line[1])
			opcode = op_ht[op].opcode

			instr_bin = '{imm}{rs1}{funct3}{rd}{opcode}'.format(
				imm=imm, \
				rs1=rs1, \
				funct3=funct3, \
				rd=rd, \
				opcode=opcode
			)
			return [instr]

		def Stype(self, line):

			op_ht = {
				'sb'	: Op_ht(funct3=0b000, opcode=0b0100011),
				'sh'	: Op_ht(funct3=0b001, opcode=0b0100011),
				'sw'	: Op_ht(funct3=0b010, opcode=0b0100011)
			}

			self.check_args(line, ('reg', 'offset'))

			imm, rs1 = self.parse_offset(line[2])
			imm = parse_imm(imm, 7)
			rs2 = Register(line[1])
			rs1 = Register(rs1)
			funct3 = op_ht[op].funct3
			opcode = op_ht[op].opcode

			instr_bin = '{imm_11_5:07b}{rs2:05b}{rs1:05b}{funct3:03b}' \
				'{imm_4_0:05b}{opcode:07b}'.format(
					imm_11_5=imm[11:5], \
					rs2=rs2, \
					rs1=rs1, \
					funct3=funct3, \
					imm_4_0=imm[4:0], \
					opcode=opcode \
				)

			return [instr_bin]

		def Btype(self, line):

			op_ht = {
				'beq'	: Op_ht(funct3=0b000, opcode=1100011),
				'bne'	: Op_ht(funct3=0b001, opcode=1100011),
				'blt'	: Op_ht(funct3=0b100, opcode=1100011),
				'bge'	: Op_ht(funct3=0b101, opcode=1100011),
				'bltu'	: Op_ht(funct3=0b110, opcode=1100011),
				'bgeu'	: Op_ht(funct3=0b111, opcode=1100011)
			}

			imm = self.check_args(line, ('reg', 'reg', ('label', 'imm')))

			imm = Immidiate(imm, 12)
			rs2 = Register(line[2])
			rs1 = Register(line[1])
			funct3 = op_ht[op].funct3
			opcode = op_ht[op].opcode

			instr_bin = '{imm_12:01b}{imm_10_5:06b}{rs2:05b}{rs1:05b}' \
				'{funct3:03b}{imm_4_1:04b}{imm_11:01b}'.format(
					imm_12=imm[12], \
					imm_10_5=imm[10:5], \
					rs2=rs2, \
					rs1=rs1, \
					funct3=funct3, \
					imm_4_1=imm[4:1], \
					imm_11=imm[11]
				)

			return [instr_bin]

		def Utype(self, line):

			op_ht = {
				'lui'	: Op_ht(opcode=0b0110111),
				'auipc'	: Op_ht(opcode=0b0010111)
			}

			self.check_args(line, ('reg', 'imm'))

			reg = Register(line[1])
			imm = Immidiate(line[2], 32)
			

