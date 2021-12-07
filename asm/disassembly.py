# -*- coding: utf-8 -*-
# @Author: kostya
# @Date:   2021-12-04 21:23:40
# @Last Modified by:   kostya
# @Last Modified time: 2021-12-07 14:30:50

import sys

class Instruction(object):

	LUI_OPCODE		= 0b0110111
	AUIPC_OPCODE	= 0b0010111
	JAL_OPCODE		= 0b1101111
	JALR_OPCODE		= 0b1100111
	BEQ_OPCODE		= 0b1100011
	BNE_OPCODE		= 0b1100011
	BLT_OPCODE		= 0b1100011
	BGE_OPCODE		= 0b1100011
	BLTU_OPCODE		= 0b1100011
	BGEU_OPCODE		= 0b1100011
	LB_OPCODE		= 0b0000011
	LH_OPCODE		= 0b0000011
	LW_OPCODE		= 0b0000011
	LBU_OPCODE		= 0b0000011
	LHU_OPCODE		= 0b0000011
	SB_OPCODE		= 0b0100011
	SH_OPCODE		= 0b0100011
	SW_OPCODE		= 0b0100011
	ADDI_OPCODE		= 0b0010011
	SLTI_OPCODE		= 0b0010011
	SLTIU_OPCODE	= 0b0010011
	XORI_OPCODE		= 0b0010011
	ORI_OPCODE		= 0b0010011
	ANDI_OPCODE		= 0b0010011
	SLLI_OPCODE		= 0b0010011
	SRLI_OPCODE		= 0b0010011
	SRAI_OPCODE		= 0b0010011
	ADD_OPCODE		= 0b0110011
	SUB_OPCODE		= 0b0110011
	SLL_OPCODE		= 0b0110011
	SLT_OPCODE		= 0b0110011
	SLTU_OPCODE		= 0b0110011
	XOR_OPCODE		= 0b0110011
	SRL_OPCODE		= 0b0110011
	SRA_OPCODE		= 0b0110011
	OR_OPCODE		= 0b0110011
	AND_OPCODE		= 0b0110011
	FENCE_OPCODE	= 0b0001111
	ECALL_OPCODE	= 0b1110011
	EBREAK_OPCODE	= 0b1110011

	R_OPCODE = {
		ADD_OPCODE, SUB_OPCODE, XOR_OPCODE, \
		OR_OPCODE, AND_OPCODE, SLL_OPCODE, \
		SRL_OPCODE, SRA_OPCODE, SLT_OPCODE, \
		SLTIU_OPCODE, SLLI_OPCODE, SRLI_OPCODE, \
		SRAI_OPCODE \
	}
	I_OPCODE = {
		ADDI_OPCODE, XORI_OPCODE, ORI_OPCODE, \
		ANDI_OPCODE, SLTI_OPCODE, SLTIU_OPCODE, \
		LB_OPCODE, LH_OPCODE, LW_OPCODE, \
		LBU_OPCODE, LHU_OPCODE, JALR_OPCODE, \
		FENCE_OPCODE, ECALL_OPCODE, EBREAK_OPCODE \
	}
	S_OPCODE = {
		SB_OPCODE, SH_OPCODE, SW_OPCODE, \
	}
	B_OPCODE = {
		BEQ_OPCODE, BNE_OPCODE, BLT_OPCODE, \
		BGE_OPCODE, BLTU_OPCODE, BGEU_OPCODE \
	}
	J_OPCODE = {JAL_OPCODE}
	U_OPCODE = {LUI_OPCODE, AUIPC_OPCODE}

	def __init__(self, instr):
		self.instr = instr
		self.instr_bin_rev = '{:032b}'.format(self.instr)
		self.instr_bin = self.instr_bin_rev[::-1]
		self.opcode_bin = self.instr_bin[0:7][::-1]
		self.opcode = int(self.opcode_bin, 2)
		if self.opcode in Instruction.R_OPCODE:
			self.type = 'R'
		elif self.opcode in Instruction.I_OPCODE:
			self.type = 'I'
		elif self.opcode in Instruction.S_OPCODE:
			self.type = 'S'
		elif self.opcode in Instruction.B_OPCODE:
			self.type = 'B'
		elif self.opcode in Instruction.J_OPCODE:
			self.type = 'J'
		elif self.opcode in Instruction.U_OPCODE:
			self.type = 'U'
		else:
			self.instruction = 'ILLINSTR'
			self.type = 'None'
			ans = 'opcode: {op:02x} = {op:07b} = {op}\n'.format(op=self.opcode)
			print(ans)
			return

		if self.type in 'R':
			self.funct7_bin = self.instr_bin[25:32][::-1]
			self.funct7 = int(self.funct7_bin, 2)
		if self.type in 'RSB':
			self.rs2_bin = self.instr_bin[20:25][::-1]
			self.rs2 = int(self.rs2_bin, 2)
		if self.type in 'RISB':
			self.rs1_bin = self.instr_bin[15:20][::-1]
			self.rs1 = int(self.rs1_bin, 2)
		if self.type in 'RISB':
			self.funct3_bin = self.instr_bin[12:15][::-1]
			self.funct3 = int(self.funct3_bin, 2)
		if self.type in 'RIUJ':
			self.rd_bin = self.instr_bin[7:12][::-1]
			self.rd = int(self.rd_bin, 2)
		if self.type in 'I':
			self.imm_bin = self.instr_bin[20:32][::-1]
			self.imm = int(self.imm_bin, 2)
		if self.type in 'S':
			self.imm_bin = self.instr_bin[25:32][::-1]
			self.imm = int(self.imm_bin, 2)
		if self.type in 'B':
			self.imm_bin = self.instr_bin[32] + self.instr_bin[7] \
			+ self.instr_bin[25:31][::-1] + self.instr_bin[8:12][::-1] + '0'
			self.imm = int(self.imm_bin, 2)
		if self.type in 'U':
			self.imm_bin = self.instr_bin[12:32][::-1] + '0' * 11
			self.imm = int(self.imm_bin, 2)
		if self.type in 'J':
			self.imm_bin = self.instr_bin[32] + self.instr_bin[12:20][::-1] + \
			self.instr_bin[20] + self.instr_bin[21:31][::-1] + '0'
			self.imm = int(self.imm_bin, 2)

		if self.opcode == Instruction.LUI_OPCODE:
			self.instruction = 'LUI'
		elif self.opcode == Instruction.AUIPC_OPCODE:
			self.instruction = 'AUIPC'
		elif self.opcode == Instruction.JAL_OPCODE:
			self.instruction = 'JAL'
		elif self.opcode == Instruction.JALR_OPCODE:
			self.instruction = 'JALR'
		elif self.opcode == Instruction.BEQ_OPCODE:
			if self.funct3 == 0b000:
				self.instruction = 'BEQ'
			elif self.funct3 == 0b001:
				self.instruction = 'BNE'
			elif self.funct3 == 0b100:
				self.instruction = 'BLT'
			elif self.funct3 == 0b101:
				self.instruction = 'BGE'
			elif self.funct3 == 0b110:
				self.instruction = 'BLTU'
			elif self.funct3 == 0b111:
				self.instruction = 'BGEU'
			else:
				self.instruction = 'INVALID BRANCH INSTRUCTION (funct3)'
		elif self.opcode == Instruction.LB_OPCODE:
			if self.funct3 == 0b000:
				self.instruction = 'LB'
			elif self.funct3 == 0b001:
				self.instruction = 'LH'
			elif self.funct3 == 0b010:
				self.instruction = 'LW'
			elif self.funct3 == 0b100:
				self.instruction = 'LBU'
			elif self.funct3 == 0b101:
				self.instruction = 'LHU'
			else:
				self.instruction = 'INVALID LOAD INSTRUCTION (funct3)'
		elif self.opcode == Instruction.SB_OPCODE:
			if self.funct3 == 0b000:
				self.instruction = 'SB'
			elif self.funct3 == 0b001:
				self.instruction = 'SH'
			elif self.funct3 == 0b010:
				self.instruction = 'SW'
			else:
				self.instruction = 'INVALID STORE INSTRUCTION (funct3)'
		elif self.opcode == Instruction.ADDI_OPCODE:
			if self.funct3 == 0b000:
				self.instruction = 'ADDI'
			elif self.funct3 == 0b010:
				self.instruction = 'SLTI'
			elif self.funct3 == 0b011:
				self.instruction = 'SLTIU'
			elif self.funct3 == 0b100:
				self.instruction = 'XORI'
			elif self.funct3 == 0b110:
				self.instruction = 'ORI'
			elif self.funct3 == 0b111:
				self.instruction = 'ANDI'
			elif self.funct3 == 0b001:
				if self.funct7 == 0:
					self.instruction = 'SLLI'
				else:
					self.instruction = 'INVALID SLLI INSTRUCTION (funct7)'
			elif self.funct3 == 0b101:
				if self.funct7 == 0:
					self.instruction = 'SRLI'
				elif self.funct7 == 0b0100000:
					self.instruction = 'SRAI'
				else:
					self.instruction = 'INVALID SRLI/SRAI INSTRUCTION (funct7)'
			else:
				self.instruction = 'INVALID IMMIDIATE INSTRUCTION (funct3)'
		elif self.opcode == Instruction.ADD_OPCODE:
			if self.funct3 == 0b000:
				if self.funct7 == 0:
					self.instruction = 'ADD'
				elif self.funct7 == 0b0100000:
					self.instruction = 'SUB'
				else:
					self.instruction = 'INVALID ADD/SUB INSTRUCTION (funct7)'
			elif self.funct3 == 0b001:
				if self.funct7 == 0:
					self.instruction = 'SLL'
				else:
					self.instruction = 'INVALID SLL INSTRUCTION (funct7)'
			elif self.funct3 == 0b001:
				if self.funct7 == 0:
					self.instruction = 'SLL'
				else:
					self.instruction = 'INVALID SLL INSTRUCTION (funct7)'
			elif self.funct3 == 0b010:
				if self.funct7 == 0:
					self.instruction = 'SLT'
				else:
					self.instruction = 'INVALID SLT INSTRUCTION (funct7)'
			elif self.funct3 == 0b011:
				if self.funct7 == 0:
					self.instruction = 'SLTU'
				else:
					self.instruction = 'INVALID SLTU INSTRUCTION (funct7)'
			elif self.funct3 == 0b100:
				if self.funct7 == 0:
					self.instruction = 'XOR'
				else:
					self.instruction = 'INVALID XOR INSTRUCTION (funct7)'
			elif self.funct3 == 0b0101:
				if self.funct7 == 0:
					self.instruction = 'SRL'
				elif self.funct7 == 0b0100000:
					self.instruction = 'SRA'
				else:
					self.instruction = 'INVALID SRL/SRA INSTRUCTION (funct7)'
			elif self.funct3 == 0b001:
				if self.funct7 == 0:
					self.instruction = 'SLL'
				else:
					self.instruction = 'INVALID SLL INSTRUCTION (funct7)'
			elif self.funct3 == 0b110:
				if self.funct7 == 0:
					self.instruction = 'OR'
				else:
					self.instruction = 'INVALID OR INSTRUCTION (funct7)'
			elif self.funct3 == 0b111:
				if self.funct7 == 0:
					self.instruction = 'AND'
				else:
					self.instruction = 'INVALID AND INSTRUCTION (funct7)'
			else:
				self.instruction = 'INVALID ARITHMETIC INSTRUCTION (funct3)'
		elif self.opcode == self.FENCE_OPCODE:
			if self.funct3 == 0:
				self.instruction = 'FENCE'
			else:
				self.instruction = 'INVALID FENCE INSTRUCTION (funct3)'
		elif self.opcode == Instruction.ECALL_OPCODE:
			if self.funct3 != 0:
				self.instruction = 'INVALID ECALL/EBREAK INSTRUCTION (funct3)'
			elif self.funct7 != 0:
				self.instruction = 'INVALID ECALL/EBREAK INSTRUCTION (funct7)'
			elif self.imm == 0:
				self.instruction = 'ECALL'
			elif self.imm == 1:
				self.instruction = 'EBREAK'
			else:
				self.instruction = 'INVALID ECALL/EBREAK INSTRUCTION (imm)'
		else:
			self.instruction = 'INVALID INSTRUCTION (opcode)'

	def __str__(self):
		ans = 'class {} instruction: {}\n'.format(self.type, self.instruction)
		ans += 'instr : 0x{instr:08x} = {instr:032b} = {instr}\n'.format(instr=self.instr)
		if self.type in 'R':
			ans += 'funct7: 0x{f7:02x} = {f7:07b} = {f7}\n'.format(f7=self.funct7)
		if self.type in 'RSB':
			ans += 'rs2   : 0x{rs2:02x} = {rs2:05b} = {rs2}\n'.format(rs2=self.rs2)
		if self.type in 'RISB':
			ans += 'rs1   : 0x{rs1:02x} = {rs1:05b} = {rs1}\n'.format(rs1=self.rs1)
		if self.type in 'RISB':
			ans += 'funct3: 0x{f3:01x} = {f3:03b} = {f3}\n'.format(f3=self.funct3)
		if self.type in 'RIUJ':
			ans += 'rd    : 0x{rd:02x} = {rd:05b} = {rd}\n'.format(rd=self.rd)
		if self.type in 'IS':
			ans += 'imm   : 0x{imm:03x} = {imm:011b} = {imm}\n'.format(imm=self.imm)
		if self.type in 'B':
			ans += 'imm   : 0x{imm:03x} = {imm:012b} = {imm}\n'.format(imm=self.imm)
		if self.type in 'J':
			ans += 'imm   : 0x{imm:05x} = {imm:020b} = {imm}\n'.format(imm=self.imm)
		if self.type in 'U':
			ans += 'imm   : 0x{imm:08x} = {imm:032b} = {imm}\n'.format(imm=self.imm)
		ans += 'opcode: 0x{op:02x} = {op:07b} = {op}\n'.format(op=self.opcode)
		return ans


instr_arr = []
argv = sys.argv[1:]
for instr in argv:
	print(f'parsing instruction {instr}')
	print(Instruction(int(instr, 16)))
	print()
for instr in instr_arr:
	print(f'parsing instruction {instr}')
	print(Instruction(instr))
	print()
