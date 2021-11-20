###====------------------------====###
#   program multiplies 2 numbers     #
#       first operand is in x1       #
#       second operand from switches #
###====------------------------====###

li      x1      11          # 0 # x1 = 11
ls      x2                  # x2 = switches
li      x3      1           # 2 # x3 = 1
li      x4      0           # 3 # x4 = 0
beq     x2      zero    4   # 4 # if (x2 == zero): goto (8)
  add   x4      x4      x1  # 5 # x4 += x1
  sub   x2      x2      x3  # 6 # x2 -= 1
  j     -3                  # 7 # goto (4)
j       0                   # 8 # end (infinit loop)
