###====--------------------------====###
#   test program to compute fibonacci  #
#     numbers                          #
#       fib index is in x1             #
#       result is in x2                #
###====--------------------------====###

li      x1      13          # 0  # x1 = 13 (find 13th fib number)

li      t1      1           # 1  # t1 (x6) = 1 (first fib number)
li      t2      1           # 2  # t2 (x7) = 1 (second fib number)

li      s0      1           # 3  # s2 (x8) = 1 (register with one)
li      s1      2           # 4  # s1 (x9) = 3 (stop border)

blt     zero    x1      3   # 5  # if (x1 > 0): goto (8)
  li    x2      -1          # 6  # x2 = -1 (if fib index < 0: return -1)
  j     0                   # 7  # end (infinit loop)

blt     s1      x1      3   # 8  # if (x1 > 2): goto (11)
  add   x2      zero    t2  # 9  # x2 = t2 (place answer to x2)
  j     0                   # 10 # end (infinit loop)

add     t0      zero    t2  # 11 # t3 = t2 (save t2 value to then move it to t1)
add     t2      t2      t1  # 12 # t2 = t2 + t1 (fib step)
add     t1      zero    t0  # 13 # t2 = t3 (move saved t2 value to t1)
sub     x1      x1      s0  # 14
j       -7                  # 15 # goto (8) (back to chech remaining steps)
