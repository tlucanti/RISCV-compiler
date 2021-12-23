###====--------------------------====###
#   test program to compute fibonacci  #
#     numbers                          #
#       fib index is in x1             #
#       result is in x2                #
###====--------------------------====###

li      x1      13          # 0x00 # x1 = 13 (find 13th fib number)

li      t1      1           # 0x04 # t1 (x6) = 1 (first fib number)
li      t2      1           # 0x08 # t2 (x7) = 1 (second fib number)

li      s0      1           # 0x0c # s2 (x8) = 1 (register with one)
li      s1      2           # 0x10 # s1 (x9) = 3 (stop border)

blt     zero    x1   check  # 0x14 # if (x1 > 0): goto (8)
  li    x2      -1          # 0x18 # x2 = -1 (if fib index < 0: return -1)
  j     end                 # 0x1c # end (infinit loop)

check:
blt     s1      x1    step  # 0x20 # if (x1 > 2): goto (11)
  add   x2      zero    t2  # 0x24 # x2 = t2 (place answer to x2)
  j     end                 # 0x28 # end (infinit loop)

step:
add     t0      zero    t2  # 0x2c # t3 = t2 (save t2 value to then move it to t1)
add     t2      t2      t1  # 0x30 # t2 = t2 + t1 (fib step)
add     t1      zero    t0  # 0x34 # t2 = t3 (move saved t2 value to t1)
sub     x1      x1      s0  # 0x38 # x1 = x1 - 1
j       check               # 0x3c # goto (8) (back to check remaining steps)

end:
j       end                 # 0x40 #
