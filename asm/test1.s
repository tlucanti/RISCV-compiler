###====------------------------====###
#   test program to check basic      #
#     arithmetics work               #
###====------------------------====###

li		zero	123				# 0  # x0 = 123
li		x1		7				# 1  # x1 = 7
li		x2		8				# 2  # x2 = 8
add		x1		x1		x1		# 3  # x1 = x1 + x1 (x1 = 14)
li		x3		0				# 4  # x3 = 0
add		x2		x1		x3		# 5  # x2 = x1 + x3 (x2 = 14)
sub		x2		x2		x2		# 6  # x2 = x2 - x2 (x2 = 0)
li		x1		0b010101		# 7  # x1 = 21
li		x2		0b101010		# 8  # x2 = 42
xor		x1		x1		x2		# 9  # x1 = x1 ^ x2 (x1 = 0b111111 = 63)
xor		x1		x1		x1		# 10 # x1 = x1 ^ x1 (x1 = 0)
add		x2		zero	zero	# 11 # x2 = 0 + 0 (x2 = 0)
li		x1		1				# 12 # x1 = 1
add		x1		x1		x1		# 13 # x1 = x1 + x1 (x1 = 2)
add		x1		x1		x1		# 14 # x1 = x1 + x1 (x1 = 4)
add		x1		x1		x1		# 15 # x1 = x1 + x1 (x1 = 8)
add		x1		x1		x1		# 16 # x1 = x1 + x1 (x1 = 16)
end:
j		end						# 17 # end (infinit loop)
