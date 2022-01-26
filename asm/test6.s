###====------------------------====###
#   test program to check program    #
#     interruption handling          #
###====------------------------====###

mret
csrrw x1 mie t0
csrrs x13 mepc zero
csrrc a0 mcause x0
