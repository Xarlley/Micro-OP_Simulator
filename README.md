# Micro-OP_Simulator
Simulates the execution of five instructions broken down into micro-operations.


## Instruction Type and Micro Operations

1. BR 指令（分支指令）

- 功能：根据条件是否满足进行跳转。
- 微操作序列：
```
iFetch：从内存中取指令到 IR，PC 增加 4。
opFetch-DCD：
    A <= Reg[IR[rs]]（将源寄存器的值加载到操作数寄存器 A）
    B <= Reg[IR[rt]]（将目标寄存器的值加载到操作数寄存器 B）
BR-Eval：根据具体的条件（如等于、大小等）评估是否满足跳转条件。
BR-Addr：
    如果满足条件，计算目标地址：PC <= PC + (offset << 1)。
    如果条件不满足，则 PC 保持为原来的顺序地址（即 PC <= PC + 4）。
```

2. JR/JAL/J 指令（跳转指令）

- 功能：无条件跳转或链接跳转。
- 微操作序列：
```
iFetch：从内存中取指令到 IR，PC 增加 4。
opFetch-DCD：
    如果是 JR 指令，则 A <= Reg[IR[rs]]。
    如果是 JAL 指令，则链接寄存器 Reg[ra] <= PC（存储返回地址）。
J-Addr：
JR 指令：PC <= A。
JAL/J 指令：PC <= (PC[31:28] | IR[25:0] << 2)。
```

3. RR 指令（寄存器-寄存器类型）

- 功能：对两个寄存器进行算术或逻辑运算。
- 微操作序列：
```
iFetch：从内存中取指令到 IR，PC 增加 4。
opFetch-DCD：A <= Reg[IR[rs]]，B <= Reg[IR[rt]]。
RR-ALU：r <= A op IRop B（根据操作码进行运算）。
WB：WB <= r（将结果存入临时寄存器 WB）。
RR-WB：Reg[IR[rd]] <= WB（将结果写回目的寄存器）。
```

4. RI 指令（寄存器-立即数类型）

- 功能：使用寄存器和立即数进行运算。
- 微操作序列：
```
iFetch：从内存中取指令到 IR，PC 增加 4。
opFetch-DCD：A <= Reg[IR[rs]]。
RI-ALU：r <= A op IRop IRim（使用寄存器 A 和立即数进行运算）。
WB：WB <= r（将结果存入临时寄存器 WB）。
RI-WB：Reg[IR[rd]] <= WB（将结果写回目的寄存器）。
```

5. LD/ST 指令（加载/存储类型）

- 功能：从内存加载数据到寄存器，或将寄存器的数据存储到内存。
- 微操作序列（以 LD 为例）：
```
iFetch：从内存中取指令到 IR，PC 增加 4。
opFetch-DCD：A <= Reg[IR[rs]]。
Addr-Calc：计算目标地址 Address <= A + SignExt(IR[Imm])。
Memory-Access：
    对于 LD：从内存中读取数据 MDR <= Mem[Address]。
    对于 ST：写入数据 Mem[Address] <= B（B 为源寄存器中的数据）。
LD-WB：对于 LD 指令，将数据 MDR 写入目标寄存器：Reg[IR[rt]] <= MDR。
```

## Introduction

本程序对于五种类型的指令分别实现了**beq**, **j**, **add**, **addi**, **lb**指令，将它们按照上述微操作拆分完成。

## How to Run

代码中已包含了示例演示程序

```
python Run.py
```

## Authors

```
LSF NUDT Homework (^_^)
```