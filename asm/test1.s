###====------------------------====###
#   test program to check basic      #
#     arithmetics work               #
###====------------------------====###

li		zero	123				# 0x00 # x0 = 123
li		x1		7				# 0x04 # x1 = 7
li		x2		8				# 0x08 # x2 = 8
add		x1		x1		x1		# 0x0c # x1 = x1 + x1 (x1 = 14)
li		x3		0				# 0x10 # x3 = 0
add		x2		x1		x3		# 0x14 # x2 = x1 + x3 (x2 = 14)
sub		x2		x2		x2		# 0x18 # x2 = x2 - x2 (x2 = 0)
li		x1		0b010101		# 0x1c # x1 = 21
li		x2		0b101010		# 0x20 # x2 = 42
xor		x1		x1		x2		# 0x24 # x1 = x1 ^ x2 (x1 = 0b111111 = 63)
xor		x1		x1		x1		# 0x28 # x1 = x1 ^ x1 (x1 = 0)
add		x2		zero	zero	# 0x2c # x2 = 0 + 0 (x2 = 0)
li		x1		1				# 0x30 # x1 = 1
add		x1		x1		x1		# 0x34 # x1 = x1 + x1 (x1 = 2)
add		x1		x1		x1		# 0x38 # x1 = x1 + x1 (x1 = 4)
add		x1		x1		x1		# 0x3c # x1 = x1 + x1 (x1 = 8)
add		x1		x1		x1		# 0x40 # x1 = x1 + x1 (x1 = 16)
end:
j		end						# 0x44 # end (infinit loop)
