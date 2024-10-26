class RISCVCpuSimulator:
    def __init__(self):
        self.registers = [0] * 32      # 32个寄存器初始化为0
        self.memory = {}               # 内存字典
        self.pc = 0                    # 程序计数器
        self.ir = 0                    # 指令寄存器
        self.mdr = 0                   # 内存数据寄存器
        self.wb = 0                    # 写回寄存器
        self.offset = 4                # 默认偏移量

    # 从内存中读取指令的iFetch微操作
    def iFetch(self):
        self.ir = self.memory.get(self.pc, 0)
        print(f"iFetch: IR <= Mem[{self.pc}], PC += 4")
        self.pc += 4

    # 操作数提取和指令译码的微操作
    def opFetch_DCD(self, rs=None, rt=None, rd=None):
        if rs is not None:
            self.A = self.registers[rs]
        else:
            self.A = None  # 为 J 指令保留空值

        if rt is not None:
            self.B = self.registers[rt]
        else:
            self.B = None  # J 指令不需要 B 操作数

        print(f"opFetch-DCD: A <= Reg[{rs if rs is not None else 'N/A'}] ({self.A}), "
            f"B <= Reg[{rt if rt is not None else 'N/A'}] ({self.B if self.B is not None else 'N/A'})")

    # BR指令条件判断
    def BR_Eval(self, condition):
        self.branch_taken = condition(self.A, self.B)
        print(f"BR-Eval: branch_taken = {self.branch_taken}")

    # BR指令目标地址计算
    def BR_Addr(self):
        if self.branch_taken:
            self.pc = self.pc + (self.offset << 1)
        else:
            self.pc += 4
        print(f"BR-Addr: PC <= {self.pc}")

    # 跳转地址的J-Addr微操作
    def J_Addr(self, address):
        self.pc = address
        print(f"J-Addr: PC <= {self.pc}")

    # RR指令ALU微操作
    def RR_ALU(self, operation):
        self.r = operation(self.A, self.B)
        print(f"RR-ALU: r <= A op B = {self.r}")

    # RI指令ALU微操作
    def RI_ALU(self, operation, immediate):
        self.r = operation(self.A, immediate)
        print(f"RI-ALU: r <= A op Immediate = {self.r}")

    # Load/Store的地址计算微操作
    def Addr_Calc(self, immediate):
        self.Address = self.A + immediate
        print(f"Addr-Calc: Address <= {self.Address}")

    # Memory访问微操作
    def Memory_Access(self, load=True):
        if load:
            self.mdr = self.memory.get(self.Address, 0)
            print(f"Memory-Access (Load): MDR <= Mem[{self.Address}] ({self.mdr})")
        else:
            self.memory[self.Address] = self.B
            print(f"Memory-Access (Store): Mem[{self.Address}] <= B ({self.B})")

    # 通用的写回寄存器WB微操作
    def WB(self):
        self.wb = self.r
        print(f"WB: WB <= r ({self.wb})")

    # RR指令的RR-WB微操作
    def RR_WB(self, rd):
        self.registers[rd] = self.wb
        print(f"RR-WB: Reg[{rd}] <= WB ({self.wb})")

    # RI指令的RI-WB微操作
    def RI_WB(self, rd):
        self.registers[rd] = self.wb
        print(f"RI-WB: Reg[{rd}] <= WB ({self.wb})")

    # LD指令的LD-WB微操作
    def LD_WB(self, rt):
        self.registers[rt] = self.mdr
        print(f"LD-WB: Reg[{rt}] <= MDR ({self.mdr})")

    # 分支（BR）指令
    def execute_beq(self, rs, rt, offset):
        self.iFetch()
        self.opFetch_DCD(rs, rt)
        self.BR_Eval(lambda a, b: a == b)
        self.BR_Addr()

    # 跳转（J）指令
    def execute_j(self, address):
        self.iFetch()
        self.opFetch_DCD(rs=None)
        self.J_Addr(address)

    # 寄存器-寄存器（RR）指令
    def execute_add(self, rs, rt, rd):
        self.iFetch()
        self.opFetch_DCD(rs, rt)
        self.RR_ALU(lambda a, b: a + b)
        self.WB()
        self.RR_WB(rd)

    # 寄存器-立即数（RI）指令
    def execute_addi(self, rs, immediate, rd):
        self.iFetch()
        self.opFetch_DCD(rs)
        self.RI_ALU(lambda a, imm: a + imm, immediate)
        self.WB()
        self.RI_WB(rd)

    # Load（LD）指令
    def execute_lb(self, rs, immediate, rt):
        self.iFetch()
        self.opFetch_DCD(rs)
        self.Addr_Calc(immediate)
        self.Memory_Access(load=True)
        self.LD_WB(rt)
        print(f"LD-WB: Reg[{rt}] <= MDR ({self.mdr})")

    # 展示寄存器内容
    def display_registers(self):
        print("寄存器内容：", self.registers)

    # 展示内存内容
    def display_memory(self, start, length):
        for addr in range(start, start + length):
            print(f"地址 {addr}: {self.memory.get(addr, 0)}")

# 示例使用
# 初始化 CPU 模拟器
cpu = RISCVCpuSimulator()

# 设置初始寄存器值和内存值，便于验证各指令执行效果
cpu.registers[1] = 10   # 用于 ADD 和 ADDI 指令
cpu.registers[2] = 20   # 用于 ADD 指令
cpu.registers[3] = 1    # 用于 BEQ 比较
cpu.registers[4] = 1    # 用于 BEQ 比较
cpu.registers[5] = 0    # 设置寄存器 5 初始值为 0，用于 J 指令前的显示
cpu.memory[0] = 42      # 用于 LB 指令，从地址 0 加载值到寄存器
cpu.memory[10] = 42     # 用于 LB 指令，地址 10 存储了要加载的值

# 1. 执行 BEQ 指令（如果寄存器相等，则跳转）
print("执行 BEQ 指令前，PC =", cpu.pc)
cpu.execute_beq(rs=3, rt=4, offset=4)  # BEQ 比较寄存器 3 和 4，如果相等则跳转
print("执行 BEQ 指令后，PC =", cpu.pc)  # 寄存器 3 和 4 存储的值相同，应当满足跳转条件

# 2. 执行 J 指令（无条件跳转）
print("\n执行 J 指令前，PC =", cpu.pc)
cpu.execute_j(24)  # 跳转到地址 24
print("执行 J 指令后，PC =", cpu.pc)  # PC 应该更新为 24

# 3. 执行 ADD 指令（寄存器相加）
print("\n执行 ADD 指令前，寄存器 5 =", cpu.registers[5])
cpu.execute_add(rd=5, rs=1, rt=2)  # ADD 寄存器 1 和寄存器 2 的值到寄存器 5
print("执行 ADD 指令后，寄存器 5 =", cpu.registers[5])  # 寄存器 5 应为 30

# 4. 执行 ADDI 指令（寄存器和立即数相加）
print("\n执行 ADDI 指令前，寄存器 6 =", cpu.registers[6])
cpu.execute_addi(rd=6, rs=1, immediate=5)  # ADDI 将寄存器 1 加上立即数 5，结果存入寄存器 6
print("执行 ADDI 指令后，寄存器 6 =", cpu.registers[6])  # 寄存器 6 应为 15

# 5. 执行 LB 指令（从内存加载数据到寄存器）
print("\n执行 LB 指令前，寄存器 7 =", cpu.registers[7])
cpu.execute_lb(rs=1, immediate=0, rt=7)  # 使用寄存器 1 的地址基址（10），偏移量 0
print("执行 LB 指令后，寄存器 7 =", cpu.registers[7])  # 寄存器 7 应为 42
