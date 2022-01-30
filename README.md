# RISCV-compiler
compiler for RISC-V assembly language \
compiling in R32I extension, more info in offical [specification][SPEC]

## Compiler Usage

You need any python version above 3.6
### to compile type command
```bash
python3 compiler.py file1.s file2.s [...]
```
it will create compiled binary files `file1.bin`, `file2.s`, ...
### Supported instructions
| Instr	| Syntax			| Type  | Explain					| Comment								|
| ----- | -----------------	|:-----:| ------------------------- | --------------------------------- 	|
| add	| add a0 a1 a2		| R		| a0 <= a1 + a2				| arithmetic signed sum					|
| sub	| sub a0 a1 a2		| R		| a0 <= a1 - a2				| arithmetic signed substruction		|
| xor	| xor a0 a1 a2		| R		| a0 <= a1 ^ a2				| binary xor							|
| or	| or a0 a1 a2		| R		| a0 <= a1 \| a2			| binary or								|
| and	| and a0 a1 a2		| R		| a0 <= a1 & a2				| binary and							|
| sll	| sll a0 a1 a2		| R		| a0 <= a1 << a2			| logical shift left (unsiged)			|
| srl	| srl a0 a1 a2		| R		| a0 <= a1 >> a2			| logical shift right (unsiged)			|
| srl	| srl a0 a1 a2		| R		| a0 <= a1 >> a2			| logical shift right (unsiged)			|
| sra	| sra a0 a1 a2		| R		| a0 <= a1 >>> a2			| arithmetic shift right (signed)		|
| slt	| slt a0 a1 a2		| R		| a0 <= a1 > a2 ? 1 : 0		| set less than (signed)				|
| sltu	| slt a0 a1 a2		| R		| a0 <= a1 > a2 ? 1 : 0		| set less than (unsigned)				|
| addi	| addi a0 a1 123	| I		| a0 <= a1 + 123			| arithmetic signed sum					|
| xori	| xori a0 a1 123	| I		| a0 <= a1 ^ 123			| binary xor							|
| ori	| ori a0 a1 123		| I		| a0 <= a1 \| 123			| binary or								|
| andi	| andi a0 a1 123	| I		| a0 <= a1 & 123			| binary and							|
| slli	| slli a0 a1 123	| I		| a0 <= a1 << 123			| logical shift left (unsiged)			|
| srli	| srli a0 a1 123	| I		| a0 <= a1 >> 123			| logical shift right (unsiged)			|
| srli	| srli a0 a1 123	| I		| a0 <= a1 >> 123			| logical shift right (unsiged)			|
| srai	| srai a0 a1 123	| I		| a0 <= a1 >>> 123			| arithmetic shift right (signed)		|
| slti	| slti a0 a1 123	| I		| a0 <= a1 > 123 ? 1 : 0	| set less than (signed)				|
| sltui	| slti a0 a1 123	| I		| a0 <= a1 > 123 ? 1 : 0	| set less than (unsigned)				|
| lb	| lb a0 123(a0)		| L		| a0 <= MEM[123 + a0][7:0]	| load byte from memory					|
| lh	| lh a0 123(a0)		| L		| a0 <= MEM[123 + a0][15:0]	| load half from memory					|
| lw	| lw a0 123(a0)		| L		| a0 <= MEM[123 + a0][31:0]	| load word from memory					|
| lbu	| lbu a0 123(a0)	| L		| a0 <= MEM[123 + a0][7:0]	| load byte from memory (unsigned)		|
| lhu	| lhu a0 123(a0)	| L		| a0 <= MEM[123 + a0][15:0]	| load half from memory	(unsigned)		|
| sb	| sb a0 123(a0)		| S		| MEM[123 + a0][7:0] <= a0	| store byte to memory					|
| sh	| sh a0 123(a0)		| S		| MEM[123 + a0][15:0] <= a0	| store half to memory					|
| sw	| sw a0 123(a0)		| S		| MEM[123 + a0][31:0] <= a0	| store word to memory					|
| beq	| beq a0 a1 label	| B		| if (a0 == a1) goto label	| conditional jump to label				|
| bne	| bne a0 a1 label	| B		| if (a0 != a1) goto label	| conditional jump to label				|
| blt	| blt a0 a1 label	| B		| if (a0 < a1) goto label	| conditional jump to label				|
| bge	| bge a0 a1 label	| B		| if (a0 >= a1) goto label	| conditional jump to label				|
| bltu	| bltu a0 a1 label	| B		| if (a0 < a1) goto label	| conditional jump to label (unsigned)	|
| bgeu	| bgeu a0 a1 label	| B		| if (a0 >= a1) goto label	| conditional jump to label (unsigned)	|
| jal	| jal ra label		| J		| ra <= pc + 4, goto label	| unconditional jump to label with saving return address	|
| jalr	| jalr ra 123(s0)	| J		| ra <= pc + 4, goto $\[s0 + 123\]	| jump and link to register		|
| lui	| lui a0 123		| U		| a0 <= 123 << 12			| load upper immediate					|
| auipc	| auipc a0 123		| U		| a0 <= pc + (123 << 12)	| add upper immediate to register		|
| auipc	| auipc a0 123		| U		| a0 <= pc + (123 << 12)	| add upper immediate to register		|
| ebreak| ebreak			| I		| meoc <= pc, mcause <= interrupt	| call interrupt handler		|
| mret	| mret				| I		| pc <= mepc				| return from interrupt handler			|
| csrrw	| csrrw a0 csr s0	| I		| a0 <= csr, csr <= s0		| read/write csr register				|
| csrrs	| csrrs a0 csr s0	| I		| a0 <= csr, csr |= s0		| read/set bit to csr register			|
| csrrc	| csrrc a0 csr s0	| I		| a0 <= csr, csr &= ~s0		| read/unsetset bit to csr register		|
| li	| li a0 123			| -		| a0 <= 123					| load immediate to register			|
| la	| la a0 label		| -		| a0 <= label				| load label address ti register		|
| j		| j label			| -		| goto label				| jump to label without saving return address	|

# Disassembly

You need any python version above 3.6
### to dissassembly single command type
```bash
python3 disassembly.py 0x12412
````
it will print information about single instruction in hex

# Test Assembly

You need any python version above 3.10
### to compile type command
```bash
python3 asm.py file1.s file2.s [...]
````
it will compile assembly code to binary files `file1.bin`, `file2.s`, ... by following rules:
|B |C |WE| WS  | ALU | RA1 | RA2 | WA |CONST|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|31|30|29|28:27|26:23|22:18|17:13|12:8| 7:0 |
- B: unconditional jump flag
- C: conditional jump flag
- WE: reg file write enable
- WS: write source data (0 - const, 1 - switches, 2 - alu)
- ALU: alu operation
- RA1: first alu operand register address
- RA2: second alu operand register address
- WA: write address of register
- CONST: constant


[SPEC]: https://raw.githubusercontent.com/tlucanti/RISCV-compiler/master/riscv-spec.pdf
