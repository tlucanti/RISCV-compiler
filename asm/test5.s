###====------------------------====###
#   test program to check special    #
#     instructions and illegal       #
#     instructions behavear          #
###====------------------------====###

li		x3		4			# 0x00 # x3 = 4
jalr	x3		x3		1	# 0x04 # x3 = pc + 4 = 4 + 4, pc = 4 + 1 << 2 = 0x08
li		x1		1			# 0x08 # x1 = 1
