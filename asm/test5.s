###====------------------------====###
#   test program to check memory     #
#     instructions                   #
###====------------------------====###

# sw		x0		0(x0)
# sw		x0		0x04(x0)
# sw		x0		0x08(x0)
# sw		x0		0x0c(x0)
# sw		x0		0x10(x0)
# sw		x0		0x14(x0)
# sw		x0		0x18(x0)
# sw		x0		0x1c(x0)
# sw		x0		0x20(x0)

li		x1		-1			# 0x00 # x1 = -1
sw		x1		0(x0)		# 0x04 # 0x0 <- -1
lw		x2		0(x0)		# 0x08 # x2 = -1
lh		x3		0(x0)		# 0x0c # x3 = -1
lh		x3		2(x0)		# 0x0c # x3 = -1
lhu		x4		0(x0)		# 0x10 # x4 = 65535
lhu		x4		2(x0)		# 0x10 # x4 = 65535
lb		x5		0(x0)		# 0x14 # x5 = -1
lb		x5		1(x0)		# 0x14 # x5 = -1
lb		x5		2(x0)		# 0x14 # x5 = -1
lb		x5		3(x0)		# 0x14 # x5 = -1
lbu		x6		0(x0)		# 0x18 # x6 = 255
lbu		x6		1(x0)		# 0x18 # x6 = 255
lbu		x6		2(x0)		# 0x18 # x6 = 255
lbu		x6		3(x0)		# 0x18 # x6 = 255

li		x1		65538		# 0x1c # x1 = 65538
li		x31		0x4			# 0x20 # x31 = 0x4
sh		x1		0(x31)		# 0x24 # 0x4 <- 65538 % 65536 = 2
lw		x7		0(x31)		# 0x28 # x7 = 2
lh		x8		0(x31)		# 0x2c # x8 = 2
lhu		x9		0(x31)		# 0x30 # x9 = 2
lb		x10		0(x31)		# 0x34 # x10 = 2
lbu		x11		0(x31)		# 0x38 # x11 = 2

li		x1		128			# 0x3c # x1 = 128
sb		x1		0x4(x31)	# 0x40 # 0x8 <- 128
lw		x12		0x4(x31)	# 0x44 # x13 = 128
lh		x13		0x4(x31)	# 0x48 # x14 = 128
lhu		x14		0x4(x31)	# 0x4c # x15 = 128
lb		x15		0x4(x31)	# 0x50 # x16 = -128
lbu		x16		0x4(x31)	# 0x54 # x17 = 128

li		x17		0xAABBCCDD
sw		x17		0x8(x0)
lb		x18		0x8(x0)
lb		x18		0x9(x0)
lb		x18		0xa(x0)
lb		x18		0xb(x0)
lbu		x18		0x8(x0)
lbu		x18		0x9(x0)
lbu		x18		0xa(x0)
lbu		x18		0xb(x0)
lh		x19		0x8(x0)
lh		x19		0xa(x0)
lhu		x19		0x8(x0)
lhu		x19		0xa(x0)
