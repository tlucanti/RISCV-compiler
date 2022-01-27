###====------------------------====###
#   test program to check program    #
#     interruption handling          #
###====------------------------====###

li		a1		123				# 0x0 # 1
csrrw	zero	mie		a1		# 0x4 # 2
li		a0		-1				# 0x8 # 3
csrrw	zero	mie		a0		# 0xc # 4

csrrw	a0		mepc	a1		# 0x10 # 5
csrrw	a0		mscratch	a1	# 0x14 # 6
csrrw	a0		mcause	a1		# 0x18 # 7

la		a0		handler			# 0x1c # 8
								# 0x20 # 9
csrrw	zero	mtvec	a0		# 0x24 # 10
ebreak							# 0x28 # 11
j		end						# 0x2c # 12 (17)


handler:
	li	a0	123					# 0x30 # 13 (12)
	csrr	a0		mepc		# 0x34 # 14 (13)
	addi	a0		a0		4	# 0x38 # 15 (14)
	csrw	mepc	a0			# 0x3c # 16 (15)
	mret						# 0x40 # 17 (16)



end:
	j	end						# 0x44 # 18
