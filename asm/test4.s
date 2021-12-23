###====------------------------====###
#   test program to check advanced   #
#     instruction work               #
###====------------------------====###

lui     x1  0               # 0x00 # x1 = 0 << 12 == 0
lui     x1  1               # 0x04 # x1 = 1 << 12 == 4096

auipc   x2  0               # 0x08 # x2 = pc + 0 << 12 == 0x08 == 8
auipc   x2  0               # 0x0c # x2 = pc + 0 << 12 == 0x0c == 12
auipc   x2  1               # 0x10 # x2 = pc + 1 << 12 == 0x10 + 4096 == 4112 = 0x1010
auipc   x2  524288          # 0x14 # x2 = pc + 524288 << 12 == 0x14 - 2147483648
                                   # == -2147483628 == 0x80000014
auipc   x2  524287          # 0x18 # x2 = pc + 524287 << 12 == 0x18 * 4 + 2147479552
                                   # == 2147479648 == 0x7ffff060

jal     x3  next            # 0x1c # x3 = pc + 4 == 0x1c + 4 == 0x20
next:
jalr    x3  x3  1           # 0x20 # goto $x3 + 1 << 2

li      x1  1               # 0x24 # x1 = 1
or      x2  x0  x0          # 0x28 # x2 = 0 | 0 = 0
ori     x2  x0  0           # 0x2c # x2 = 0 | 0 = 0
or      x2  x0  x1          # 0x30 # x2 = 0 | 1 = 1
ori     x2  x0  1           # 0x34 # x2 = 0 | 1 = 1
or      x2  x1  x0          # 0x38 # x2 = 1 | 0 = 1
ori     x2  x1  0           # 0x3c # x3 = 1 | 0 = 1
or      x2  x1  x1          # 0x40 # x3 = 1 | 1 = 1
ori     x2  x1  1           # 0x44 # x3 = 1 ! 1 = 1
