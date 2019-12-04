class Instruction:
    '''
    Базовый класс для всех инструкций.
    Объявляет методы инструкции и обеспечивает релизацию для простых случаев.
    '''
    def __init__(self, cpu, length, cycles = 4):
        '''
        :param cpu: Процессор (класс CPU)
        :param opcode: Код инструкции
        :param length: Длина инструкции в байтах
        :param cycles: Время выполнения инструкции в циклах
        '''
        self._cpu = cpu
        self._length = length
        self._cycles = cycles
        '''
        Следующие две переменные класса устанавливаются конструкторами дочерних классов
        чтобы обеспечить вывод инструкции в текстовом виде.
        '''
        self._mnemonic = None
        self._argument = None   # Аргумент (аргументы), если есть. None - аргументов нет.

    def execute(self):
        '''
        Выполняет команду
        '''
        print(self._mnemonic)
        self.instruction_logic()

    def instruction_logic(self):
        '''
        Дочерние классы переопределяют эту функцию и реализовывают
        в ней логику работы инструкции.
        '''
        pass

    def byte_len(self):
        '''
        Возвращает размер инструкции в байтах.
        '''
        return self._length

    def cycle_count(self):
        '''
        Возвращает время работы инструкции в циклах.
        '''
        return self._cycles

    def mnemonic(self):
        '''
        Возвращает текстовое представление инструкции.
        '''
        if self._argument is None:
            return self._mnemonic
        return '%s %s' % (self._mnemonic, self._argument)


class InstructionNotImplemented(Instruction):
    '''
    Объект для неподдерживаемой инструкции.
    Выбрасывает исключение при попытке выполнения.
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1)
        self._opcode = xx * 0b1000000 + yyy * 0b1000 + zzz
        self._mnemonic = 'Invalid opcode %s' % hex(self._opcode)  # Мнемоника команды.

    def instruction_logic(self):
        raise Exception('Invalid instruction opcode:', self._opcode)


class InstructionNOP(Instruction):
    '''
    Интструкция NOP - ничего не делать.
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1)
        self._mnemonic = 'NOP'

    def instruction_logic(self):
        print('Инстр. NOP Выполнена')


class InstructionMOV(Instruction):
    '''
    Инструкция MOV - передача данных между регистрами или между регистрами и памятью, адресуемой HL.
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 5)
        self.dst, self.src = yyy, zzz
        self._mnemonic = 'MOV'
        self._argument = '%s, %s' % (self._cpu.REGISTER_NAMES[self.dst], self._cpu.REGISTER_NAMES[self.src])

    def instruction_logic(self):
        if self.dst == 0b110 or self.src == 0b110:
            self._cycles = 7
        self._cpu.set_register(self.dst, self._cpu.get_register(self.src))
        print('Инстр. MOV Выполнена')


class InstructionMVI(Instruction):
    '''
    Инструкция MVI - передача данных между регистрами и памятью (8 бит)
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 2, 7)
        self.dst = yyy
        self.scr = self._cpu._m[self._cpu.pc + 1]
        self._mnemonic = 'MVI'
        self._argument = '%s, %s' % (self._cpu.REGISTER_NAMES[self.dst], self.src)

    def instruction_logic(self):
        if self.dst == 0b110:
            self._cycles = 10
        self._cpu.set_register(self.dst, self.src)
        print('Инстр. MVI Выполнена')


class InstructionLDA(Instruction):
    '''
    Инструкция LDA - передача данных между регистром A и памятью (16 бит)
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 3, 13)
        self.dst = 0b111
        addr = self._cpu._m[self._cpu.pc + 1] + self._cpu._m[self._cpu.pc + 2] * 0x100
        self.src = self._cpu._m[addr]
        self._mnemonic = 'LDA'
        self._argument = '%s, %s' % (self._cpu.REGISTER_NAMES[7], self.src)

    def instruction_logic(self):
        self._cpu.set_register(self.dst, self.src)
        print('Инстр. LDA Выполнена')


class InstructionSTA(Instruction):
    '''
    Инструкция STA - передача данных между памятью и регистром A (16 бит)
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 3, 13)
        self.addr = self._cpu._m[self._cpu.pc + 1] + self._cpu._m[self._cpu.pc + 2] * 0x100
        self.src = self._cpu.get_register(0b111)
        self._mnemonic = 'STA'
        self._argument = '%s, %s' % (self._cpu._m[self.addr], self._cpu.REGISTER_NAMES[7])

    def instruction_logic(self):
        self._cpu._m[self.addr] = self.src
        print('Инстр. STA Выполнена')


class InstructionLDAX(Instruction):
    '''
    Инструкция LDAX - передача данных между регистром A и памятью
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 7)
        self.dst = 0b111
        if yyy == 0b001:
            pair = self._cpu.get_pair1(0b00)
        else:
            pair = self._cpu.get_pair1(0b01)
        self.src = self._cpu._m[pair]
        self._mnemonic = 'LDAX'
        self._argument = '%s, %s' % (self._cpu.REGISTER_NAMES[7], self.src)

    def instruction_logic(self):
        self._cpu.set_register(self.dst, self.src)
        print('Инстр. LDAX Выполнена')


class InstructionSTAX(Instruction):
    '''
    Инструкция STAX - передача данных между памятью и регистром A
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 7)
        if yyy == 0b000:
            self.pair = self._cpu.get_pair1(0b00)
        else:
            self.pair = self._cpu.get_pair1(0b01)
        self.src = self._cpu.get_register(0b111)
        self._mnemonic = 'STAX'
        self._argument = '%s, %s' % (self._cpu._m[self.pair], self._cpu.REGISTER_NAMES[7])

    def instruction_logic(self):
        self._cpu._m[self.pair] = self.src
        print('Инстр. STAX Выполнена')


class InstructionLHLD(Instruction):

    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 3, 16)
        self.dst1 = 0b101
        addr = self._cpu._m[self._cpu.pc + 1] + self._cpu._m[self._cpu.pc + 2] * 0x100
        self.src1 = self._cpu._m[addr]
        self.dst2 = 0b100
        self.src2 = self._cpu._m[addr + 1]
        self._mnemonic = 'LHLD'
        self._argument1 = '%s, %s' % (self._cpu.REGISTER_NAMES[5], self.src1)
        self._argument1 = '%s, %s' % (self._cpu.REGISTER_NAMES[4], self.src2)

    def instruction_logic(self):
        self._cpu.set_register(self.dst1, self.src1)
        self._cpu.set_register(self.dst2, self.src2)
        print('Инстр. LHLD Выполнена')


class InstructionSHLD(Instruction):

    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 3, 16)
        self.src1 = self._cpu.get_register(0b101)
        self.src2 = self._cpu.get_register(0b100)
        self.addr = self._cpu._m[self._cpu.pc + 1] + self._cpu._m[self._cpu.pc + 2] * 0x100
        self._mnemonic = 'SHLD'
        self._argument1 = '%s, %s' % (self._cpu._m[self.addr], self._cpu.REGISTER_NAMES[5])
        self._argument1 = '%s, %s' % (self._cpu._m[self.addr + 1], self._cpu.REGISTER_NAMES[4])

    def instruction_logic(self):
        self._cpu._m[self.addr] = self.src1
        self._cpu._m[self.addr + 1] = self.src2
        print('Инстр. SHLD Выполнена')


class InstructionLXI(Instruction):

    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 3, 10)
        self.src = self._cpu._m[self._cpu.pc + 1] + self._cpu._m[self._cpu.pc + 2] * 0x100
        self.dst = yyy // 2
        self._mnemonic = 'LXI'
        self._argument = '%s, %s' % (self._cpu.PAIR_NAMES_1[self.dst], self.src)

    def instruction_logic(self):
        self._cpu.pairs_1[self.dst].value = self.src
        print('Инстр. LXI Выполнена')


class InstructionSPHL(Instruction):

    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 5)
        self.src = self._cpu.pairs_1[2].value
        self._mnemonic = 'SPHL'
        self._argument = '%s, %s' % (self._cpu.PAIR_NAMES_1[3], self._cpu.PAIR_NAMES_1[2])

    def instruction_logic(self):
        self._cpu.pairs_1[3].value = self._cpu.pairs_1[2].value
        print('Инстр. SPHL Выполнена')


class InstructionPCHL(Instruction):

    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 5)
        self.src = self._cpu.pairs_1[2].value
        self._mnemonic = 'CPHL'
        self._argument = '%s, %s' % ('PC', self._cpu.PAIR_NAMES_1[2])

    def instruction_logic(self):
        self._cpu.pc = self._cpu.pairs_1[2].value
        print('Инстр. PCHL Выполнена')


class InstructionXCHG(Instruction):

    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 5)
        self.tmpDE = self._cpu.pairs_1[1].value
        self.tmpHL = self._cpu.pairs_1[2].value
        self._mnemonic = 'XCHG'
        self._argument = '%s, %s' % (self._cpu.PAIR_NAMES_1[2], self._cpu.PAIR_NAMES_1[1])

    def instruction_logic(self):
        self._cpu.pairs_1[2].value = self.tmpDE
        self._cpu.pairs_1[1].value = self.tmpHL
        print('Инстр. XCHG Выполнена')


class InstructionADD(Instruction):
    '''
    Инструкция ADD - прибавление значения регистра к значению регистра A
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 4)
        self.zzz = zzz
        self.src = self._cpu.registers[7].value + self._cpu.registers[zzz].value
        if self.src > 0xFF:
            if self._cpu._C == 0:
                self._cpu.registers[6].value = self._cpu.registers[6].value + 0b1
                self._cpu._C = 1
        else:
            if self._cpu._C == 1:
                self._cpu.registers[6].value = self._cpu.registers[6].value - 0b1
                self._cpu._C = 0
        self._mnemonic = 'ADD'
        self._argument = '%s, %s' % ('A', self._cpu.REGISTER_NAMES[zzz])

    def instruction_logic(self):
        if self.zzz == 0b110:
            self._cycles = 7
        self._cpu.registers[7].value = self.src
        print('Инстр. ADD Выполнена')


class InstructionADC(Instruction):
    '''
    Инструкция ADC - прибавление значения регистра и значения флага C к значению регистра A
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 4)
        self.zzz = zzz
        self.src = self._cpu.registers[7].value + self._cpu.registers[zzz].value + self._cpu._C
        if self.src > 0xFF:
            if self._cpu._C == 0:
                self._cpu.registers[6].value = self._cpu.registers[6].value + 0b1
                self._cpu._C = 1
        else:
            if self._cpu._C == 1:
                self._cpu.registers[6].value = self._cpu.registers[6].value - 0b1
                self._cpu._C = 0
        self._mnemonic = 'ADD'
        self._argument = '%s, %s' % ('A', self._cpu.REGISTER_NAMES[zzz], 'Flag_C')

    def instruction_logic(self):
        if self.zzz == 0b110:
            self._cycles = 7
        self._cpu.registers[7].value = self.src
        print('Инстр. ADC Выполнена')


class InstructionSUB(Instruction):
    '''
    Инструкция SUB - вычитание значения регистра из значения регистра A
    '''
    def __init__(self, cpu, xx, yyy, zzz):
        Instruction.__init__(self, cpu, 1, 4)
        self.zzz = zzz
        self.src = self._cpu.registers[7].value - self._cpu.registers[zzz].value
        if self.src < 0:
            if self._cpu._C == 0:
                self._cpu.registers[6].value = self._cpu.registers[6].value + 0b1
                self._cpu._C = 1
        else:
            if self._cpu._C == 1:
                self._cpu.registers[6].value = self._cpu.registers[6].value - 0b1
                self._cpu._C = 0
        self._mnemonic = 'SUB'
        self._argument = '%s, %s' % ('A', self._cpu.REGISTER_NAMES[zzz])

    def instruction_logic(self):
        if self.zzz == 0b110:
            self._cycles = 7
        self._cpu.registers[7].value = self.src
        print('Инстр. SUB Выполнена')


