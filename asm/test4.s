
lui		x1	0
lui		x1	1

auipc	x2	0
auipc	x2	0
auipc	x2	1
auipc	x2	524288

jal		x3	next
next:
jalr	x3	x3	1

li		x1	1
or		x2	x0	x0
ori		x2	x0	0
or		x2	x0	x1
ori		x2	x0	1
or		x2	x1	x0
ori		x2	x1	0
or		x2	x1	x1
ori		x2	x1	1

ecall
