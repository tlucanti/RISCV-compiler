###====------------------------====###
#   program multiplies 2 numbers     #
#       first operand is in x1       #
#       second operand in x2         #
#       answer in x4                 #
###====------------------------====###

li      x1      11          # 0x00 # x1 = 11
li      x2      5           # 0x04 # x2 = 5

li      x3      1           # 0x08 # x3 = 1
li      x4      0           # 0x0c # x4 = 0
loop:
beq     x2      zero    end # 0x10 # if (x2 == zero): goto (8)
  add   x4      x4      x1  # 0x14 # x4 += x1
  sub   x2      x2      x3  # 0x18 # x2 -= 1
  j     loop                # 0x1c # goto (4)
end:
j       end                 # 0x20 # end (infinit loop)
