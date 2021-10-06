from CheckSum import CheckSum


class CommandGenerator:
    def __init__(self):
        self.startBytes = bytearray.fromhex("B6 29")

    def generate(self, command, data=b''):
        checker = CheckSum()
        byte_command = b''
        length = len(data) + 1
        byte_command += length.to_bytes(2, 'big')
        byte_command += command.value.to_bytes(1, 'big')
        if length != 1:
            byte_command += data
        byte_command += checker.crc(byte_command)
        byte_command = self.startBytes + byte_command
        return byte_command


def generate_command(command, data=b''):
    generator = CommandGenerator()
    return generator.generate(command, data)


def generate_parameter_int(code: int, value: int, int_length=4):
    answer = b''
    answer += code.to_bytes(2, 'little')
    tmp_bytes = value.to_bytes(int_length, 'little')
    answer += len(tmp_bytes).to_bytes(2, 'little')
    answer += tmp_bytes
    return answer


def generate_parameter_str(code: int, value: str):
    answer = b''
    answer += code.to_bytes(2, 'little')
    tmp_bytes = bytearray(value, 'cp866')
    answer += len(tmp_bytes).to_bytes(2, 'little')
    answer += tmp_bytes
    return answer
