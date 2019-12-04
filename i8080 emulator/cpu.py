from memory import Memory
import instructions

class Register:
    '''
    8-битный регистр.
    Хранит значение и обеспечивает доступ к нему через свойство value.
    '''
    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, x):
        self._value = x & 0xFF


class RegisterPair:
    '''
    Регистровая пара.
    Обеспечивает работу с двумя 8-битными регистрами как с одним 16-битным числом.
    Доступ к значению производится через свойство value.
    '''
    def __init__(self, h, l):
        '''
        Параметры:
        h - старший регистр пары;
        l - младший регистр пары.

        Запомнинает h и l в переменных объекта
        '''
        self._h = h
        self._l = l

    @property
    def value(self):
        '''
        Вычисляет и возвращает значение пары
        '''
        return self._h.value * 0x100 + self._l.value

    @value.setter
    def value(self, v):
        '''
        Разделяет 16-битное значение v на младший и старший байты и
        записывает их в соответствющие регистры пары
        '''
        self._h.value = v // 0x100
        self._l.value = v & 0x00FF
        

class CPU:
    '''
    Центральный процессор.
    Хранит регистры, обеспечивает доступ к ним.
    '''
    ALL_REGISTERS = 'BCDEHLFASP'    # Имена всех регистров процессора
    REGISTER_NAMES = 'BCDEHLMA'     # Имена регистров, используемых в командах с регистровыми аргументами
    PAIR_NAMES_1 = ['BC', 'DE', 'HL', 'SP']    # Имена регистров, использующихся в командах работы с парами, первый тип
    PAIR_NAMES_2 = ['BC', 'DE', 'HL', 'AF']    # Имена регистров, использующихся в командах работы с парами, второй тип
    registers = [Register() for r in ALL_REGISTERS]
    pairs_1 = []
    for p in PAIR_NAMES_1:
        pairs_1.append(RegisterPair(registers[ALL_REGISTERS.index(p[0])], registers[ALL_REGISTERS.index(p[1])]))
    pairs_2 = []
    for p in PAIR_NAMES_2:
        pairs_2.append(RegisterPair(registers[ALL_REGISTERS.index(p[0])], registers[ALL_REGISTERS.index(p[1])]))
    pc = 0
    registers[6].value = 0b00000010   #Flag register (F) bits: S, Z, 0, A, 0, P, 1, C
    go = 0
    
    
    def __init__(self, memory):
        '''
        Инициализирует необходимые переменные
        '''
        self._m = memory
        self._S = (CPU.registers[6].value & 0b10000000) // 0b10000000
        self._Z = (CPU.registers[6].value & 0b01000000) // 0b1000000
        self._A = (CPU.registers[6].value & 0b00010000) // 0b10000
        self._P = (CPU.registers[6].value & 0b00000100) // 0b100
        self._C = (CPU.registers[6].value & 0b00000001) // 0b1

    def step(self):
        '''
        Выполняет один шаг работы процессора
        '''
        print(CPU.pc)
        opcode = self._m[CPU.pc]
        print('opcode =', hex(opcode))
        print('opcode =', bin(opcode))
        instr = self.decode(opcode)
        CPU.pc += 1
        instr._length
        instr.execute()
        CPU.pc += instr._length - 1
        

    def run(self):
        '''
        Бесконечный цикл в котором выполняется step()
        '''
        CPU.go = 1
        while CPU.go:
            self.step()
            print(self)


    def split_opcode(self, opcode):
        '''
        Разделяет значение opcode на группы битов XX, YYY, ZZZ
        '''
        XX = opcode // 0b1000000
        tmp = opcode - XX * 0b1000000
        YYY = tmp // 0b1000
        ZZZ = tmp & 0b111
        return XX, YYY, ZZZ
        

    def decode(self, opcode):
        '''
        Декодирует инструкцию c кодом opcode
        Эта функция по opcode возвращает объект Instruction, реализующий соответствующую инструкцию
        Для разбора опкода используется split_opcode()
        '''
        xx, yyy, zzz = self.split_opcode(opcode)
        if xx == 0b00:
            if yyy == 0b000 and zzz == 0b000:  #Инструкция NOP
                CPU.go = 0
                return instructions.InstructionNOP(self, xx, yyy, zzz)
            elif (yyy == 0b000 or yyy == 0b010) and zzz == 0b010:  #Инструкция STAX
                return instructions.InstructionSTAX(self, xx, yyy, zzz)
            elif yyy&0b001 == 0 and zzz == 0b001:  #Инструкция LXI
                return instructions.InstructionLXI(self, xx, yyy, zzz)
            elif zzz == 0b110:  #Инструкция MVI
                return instructions.InstructionMVI(self, xx, yyy, zzz)
            elif (yyy == 0b001 or yyy == 0b011) and zzz == 0b010:  #Инструкция LDAX
                return instructions.InstructionLDAX(self, xx, yyy, zzz)
            elif yyy == 0b100 and zzz == 0b010:  #Инструкция SHLD
                return instructions.InstructionSHLD(self, xx, yyy, zzz)
            elif yyy == 0b101 and zzz == 0b010:  #Инструкция LHLD
                return instructions.InstructionLHLD(self, xx, yyy, zzz)
            elif yyy == 0b110 and zzz == 0b010:  #Инструкция STA
                return instructions.InstructionSTA(self, xx, yyy, zzz)
            elif yyy == 0b111 and zzz == 0b010:  #Инструкция LDA
                return instructions.InstructionLDA(self, xx, yyy, zzz)
        if xx == 0b01:
            if yyy == 0b110 and zzz == 0b110:
                print('HLT?')
            else:  #Инструкция MOV
                return instructions.InstructionMOV(self, xx, yyy, zzz)
        if xx == 0b10:
            if yyy == 0b000:  #Инструкция ADD
                return instructions.InstructionADD(self, xx, yyy, zzz)
            elif yyy == 0b001:  #Инструкция ADC
                return instructions.InstructionADC(self, xx, yyy, zzz)
            elif yyy == 0b010:  #Инструкция SUB
                return instructions.InstructionSUB(self, xx, yyy, zzz)
        if xx == 0b11:
            if yyy == 0b101 and zzz == 0b001:  #Инструкция PCHL
                return instructions.InstructionPCHL(self, xx, yyy, zzz)
            elif yyy == 0b101 and zzz == 0b011:  #Инструкция XCHG
                return instructions.InstructionXCHG(self, xx, yyy, zzz)
            elif yyy == 0b111 and zzz == 0b001:  #Инструкция SPHL
                return instructions.InstructionSPHL(self, xx, yyy, zzz)
        else:  #Инструкция Error
            return instructions.InstructionNotImplemented(self, xx, yyy, zzz)


    def get_register(self, rrr):
        '''
        Возвращает значение регистра с индеком rrr
        Если индекс равен 0b110, возвращает значение из ячейки памяти с адресом, записанном в паре HL
        '''
        if rrr == 0b110:
            return self._m[CPU.pairs_1[2].value]
        return CPU.registers[rrr].value

    def get_pair1(self, DD):
        '''
        Возвращает значение регистровой пары с индеком DD (Первый тип)
        '''
        return CPU.pairs_1[DD].value

    def set_register(self, rrr, v):
        '''
        Записывает значение v в регистр с индеком rrr
        Если индекс равен 0b110, записывает значение v в ячейку памяти, с адресом, записанном в паре HL
        '''
        if rrr == 0b110:
            self._m[CPU.pairs_1[2].value] = v
        else:
            CPU.registers[rrr].value = v

    def __str__(self):
        '''
        Возвращает описание процессора в текстовом виде
        Выводит значения всех регистров
        '''
        s = ''
        for i in range(len(CPU.ALL_REGISTERS)):
            s += CPU.ALL_REGISTERS[i] + '=' + str(CPU.registers[i].value) + '; '
        s += 'PC=' + str(CPU.pc) + '; '
        s += 'SP=' + str(self.get_pair1(0b11)) + '; '
        s += 'Flag_S=' + str(self._S) + '; '
        s += 'Flag_Z=' +str(self._Z) + '; '
        s += 'Flag_A=' +str(self._A) + '; '
        s += 'Flag_P=' +str(self._P) + '; '
        s += 'Flag_C=' +str(self._C)
        return s



def main():
    p = CPU(Memory())
    print(p)
    
    p.set_register(0b001, 75)
    p.set_register(0b111, 255)
    p.set_register(0b000, 2)
    p._m[0] = 0x51
    p.pairs_1[2].value = 0x30
    print('HL =', p.pairs_1[2].value)
    p._m[p.pairs_1[2].value] = 6
    p._m[1] = 0x5E
    p._m[2] = 0x80
    p.run()  #MOV D,C; MOV E,M; ADD B
    print()

if __name__ == '__main__':
    main()


