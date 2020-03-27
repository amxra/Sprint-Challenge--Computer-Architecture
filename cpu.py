"""CPU functionality."""

import sys

#create instructions for LDI, PRN, and HLT programs
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101 #added pus, pop and sp
POP = 0b01000110
CALL = 0b01010000
RET  = 0b00010001
ADD = 0b10100000
CMP = 0b10100111 #added instructions for cmp, jmp, jeq n jnu
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001


SP = 7 #stack pointer

#set flags
less_flag = 0b00000100
greater_flag = 0b00000010
equal_flag = 0b00000001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        #setup ram,register and pc
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.fl = 0
        self.branchtable = {
        HLT: self.handle_hlt,
        LDI: self.handle_ldi,
        PRN: self.handle_prn,
        ADD: self.handle_add,
        MUL: self.handle_mul,
        PUSH: self.handle_push,
        POP: self.handle_pop,
        CALL: self.handle_call,
        RET: self.handle_ret,
        CMP: self.handle_cmp,
        JMP: self.handle_jmp,
        JEQ: self.handle_jeq,
        JNE: self.handle_jne
        }

        self.halted = False
        #register 7 is reserved as the stack pointer, which is 0xf4 per specs
        self.reg[SP] = 0xf4


    # Read a value in memory at a particular address
    def ram_read(self, mar):
        # return the memory[Memory Address Register]
        return self.ram[mar]

    # Write a value to the register at a particular address
    def ram_write(self, mdr, mar):
        # Register[Memory Address Register] = Memory Data Register
        self.ram[mar] = mdr


    def load(self, filename):
        """Load a program into memory."""


    #     program = sys.argv[1]

    #     address = 0 #pointer to currently executing instruction

    #     # For now, we've just hardcoded a program:

    #     # program = [
    #     #     # From print8.ls8
    #     #     0b10000010, # LDI R0,8
    #     #     0b00000000,
    #     #     0b00001000,
    #     #     0b01000111, # PRN R0
    #     #     0b00000000,
    #     #     0b00000001, # HLT
    #     # ]



        try:
            address = 0
            #open file
            with open(filename) as file:
                #read the lines
                for line in file:
                    # split line before and after comment symbol
                    comment_split = line.split("#")

                    # extract the first part of the split to a number variable
                    num = comment_split[0].strip() # trim whitespace

                    # ignore blank lines
                    if num == '':
                        continue 

                    # convert our binary string to a number
                    val = int(num, 2)

                    # store val at address in memory
                    self.ram_write(val, address)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            # Add the value in reg a, b and store the result in reg_a
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
             # Multiply the value in reg a, b and store the result in reg_a
            self.reg[reg_a] *= self.reg[reg_b] 
        elif op == "CMP":
            # Compare the values in reg a, b
            # if value at reg_a < value at reg_b
            if self.reg[reg_a] < self.reg[reg_b]:
                # Set L flag to 1
                self.fl = less_flag
              # if value at reg_a > value at reg_b
            elif self.reg[reg_a] > self.reg[reg_b]:
                 # set G flag to 1
                self.fl = greater_flag
            # otherwise, set to equal flag
            else:
                self.fl = equal_flag      
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    #method to handle adding
    def handle_add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
         # Invoke the ALU to perform ADD operation passing operands a and b
        self.alu("ADD", operand_a, operand_b)   

    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_prn(self, operand_a, operand_b):
        # Print the value in the register at a given address
        print(self.reg[operand_a])
        self.pc += 2

    # set running to False and halt to true and /End program run
    def handle_hlt(self, operand_a, operand_b):
        self.halted = True

    def handle_mul(self, operand_a, operand_b):
         # Invoke the ALU to perform MUL operation passing operands a and b
        self.alu("MUL", operand_a, operand_b)

    #method to handle push on the stack
    def handle_push(self, operand_a, operand_b):
        #decrement the SP register
        self.reg[SP] -= 1
        # copy the value in the given register to the address pointed to by SP
        operand_b = self.reg[operand_a]
        self.ram[self.reg[SP]] = operand_b

    #method to handle popping from the stack to the register
    def handle_pop(self, operand_a, operand_b):
        # copy the value from the address pointed to by SP to the given register
        operand_b = self.ram[self.reg[SP]]
        self.reg[operand_a] = operand_b
        #increment the SP
        self.pc += 2

    #method to handle subroutine calls
    def handle_call(self, operand_a, operand_b):
        #push address after call to top of stack
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2
        # set the pc to the given register
        self.pc = self.reg[operand_a]

    #method to handle the return after a call
    def handle_ret(self):
        #return from subroutine
        self.pc = self.ram[self.reg[SP]]
        #pop the value from the stack and store in pc
        self.reg[SP] += 1

    def handle_cmp(self, operand_a, operand_b):
        # Invoke the ALU to perform CMP operation passing operands a and b
        self.alu('CMP', operand_a, operand_b)
        #increment self.pc
        self.pc += 3


    def handle_jmp(self, operand_a, operand_b):
        #set pc to the register of operand_a for the jump
        self.pc = self.reg[operand_a]

    def handle_jeq(self, operand_a, operand_b):
        #if the flag is the equal flag set to true 
        if self.fl & equal_flag:
            #set pc to the register for operand_a
            self.pc = self.reg[operand_a]
            #otherwise increment self.pc
        else:
            self.pc += 2

    def handle_jne(self, operand_a, operand_b):
        # if no self.fl and equal flag after cmp
        if not self.fl & equal_flag:
            #set pc to the register for operand_a
            self.pc = self.reg[operand_a]
            #otherwise increment self.pc
        else:
            self.pc += 2


    def run(self):
        while self.halted != True:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if IR in self.branchtable:
                self.branchtable[IR](operand_a, operand_b)
            else:
                raise Exception(f'Invalid {IR}, not in branch table \t {list(self.branchtable.keys())}')  


    # def run(self):
    #     """Run the CPU."""

    #     #set running to True
    #     running = True

    #     #while cpu is running
    #     while running:
    #         #  set instruction register per step 3
    #         IR = self.ram[self.pc]

    #         # set operand_a to pc+1 per step 3
    #         operand_a = self.ram_read(self.pc + 1)
    #         # set operand_b to pc+2 per step 3
    #         operand_b = self.ram_read(self.pc + 2)

    #         # if the instruction register is LDI
    #         if IR == LDI:
    #             #set register of operand_a to operand_b, jump 3 in PC (to PRN currently)
    #             self.reg[operand_a] = operand_b
    #             self.pc +=3
    #         # if the instruction register is PRN
    #         elif IR == PRN:
    #             #print the register of operand_a, jump 2 in PC
    #             print(self.reg[operand_a])
    #             self.pc +=2
    #         # if the instruction register is the halt command
    #         elif IR == HLT:
    #             #set running to false and exit
    #             running = False
    #             sys.exit(0)
    #         # if anything else, invalid command and quit with failure code 1
    #         else:
    #             print(f"Invalid Command: {self.ram[self.pc]}")
    #             sys.exit(1)
