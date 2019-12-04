class InvalidMemoryAddressError(Exception):
    pass

class Memory:
    def __init__(self):
        # Memory
        self._buff = bytearray(0xffff)

    def __getitem__(self, addr):
        if addr < 0x0 or addr > 0xffff:
            msg = 'Error: list index out of range'
            raise InvalidMemoryAddressError(msg)
        return self._buff[addr]

    def __setitem__(self, addr, val):
        if addr < 0x0 or addr > 0xffff:
            msg = 'Error: list index out of range'
            raise InvalidMemoryAddressError(msg)
        self._buff[addr] = val

