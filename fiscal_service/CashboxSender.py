import socket
from time import sleep
from typing import Optional

from core.entities.entities import Cashbox, InstallPlace, Company, Ofd
from fiscal_service.CommandGenerator import generate_command, generate_parameter_str, generate_parameter_int
from fiscal_service.Enums import ErrorCode, Commands
from fiscal_service.ResponseParser import parse
from fiscal_service.TerminalAnswer import FiscalStorageStatus, TerminalStatus, FiscalDocument, RegStatus


class CashboxSender:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send(self, command):
        if not (self.ip or self.port):
            raise Exception("Не заданы данные подключения для ККТ")
        sock = socket.socket()
        sock.connect((self.ip, self.port))
        sock.send(command)
        sleep(1.5)  # даём ККТ немного подумать
        answer = parse(sock.recv(1024))  # TODO мб поменьше
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        if answer[1] == 1:
            return ErrorCode(answer[2])
        return answer

    def register_cashbox(self,
                         company_name: str,
                         company_authorized_person_name: str,
                         company_payment_place: str,
                         install_place_address: str,
                         ofd_inn: str,
                         ofd_name: str,
                         ofd_email: str,
                         company_agent_agent: bool,
                         company_inn: str,
                         company_tax: int,
                         register_type: int,
                         cashbox_registry_number: str,
                         reason: Optional[int],
                         cashbox_auto_device_number: Optional[str]):
        command = generate_command(Commands.BEGIN_REGISTRATION,
                                   register_type.to_bytes(4, 'little'))
        answer = self.send(command)

        data = b''
        data += generate_parameter_str(1048, company_name)
        data += generate_parameter_str(1009, install_place_address)
        data += generate_parameter_str(1187, company_payment_place)
        data += generate_parameter_str(1021, company_authorized_person_name)
        # data += generate_parameter_str(1203, inn)
        data += generate_parameter_str(1017, ofd_inn)
        data += generate_parameter_str(1046, ofd_name)
        data += generate_parameter_str(1117, ofd_email)
        if cashbox_auto_device_number:
            data += generate_parameter_str(1036, cashbox_auto_device_number)
        payment_agent = 0
        if company_agent_agent:
            payment_agent = 64
        data += generate_parameter_int(1057, payment_agent, 1)
        mode = 8  # по умолчанию пока везде ставим "применение в сфере услуг"
        data += generate_parameter_int(9999, mode, 1)
        command = generate_command(Commands.SEND_REGISTRATION_DATA, data)
        print(command.hex())
        answer = self.send(command)

        data = b''
        data += bytearray(company_inn, 'cp866')
        data += bytearray(cashbox_registry_number, 'cp866')
        data += company_tax.to_bytes(1, 'little')
        if reason:
            data += reason.to_bytes(1, 'little')

        command = generate_command(Commands.MAKE_REGISTRATION_REPORT, data)
        answer = self.send(command)
        return answer

    def close_fn(self, authorized_person_name: str, inn: str):
        command = generate_command(Commands.BEGIN_CLOSE_FN)
        answer = self.send(command)
        data = b''
        data += generate_parameter_str(1021, authorized_person_name)
        data += generate_parameter_str(1203, inn)
        command = generate_command(Commands.CLOSE_FN_DATA, data)
        print(command.hex())
        answer = self.send(command)
        command = generate_command(Commands.CLOSE_FN_FINISH)
        answer = self.send(command)

    def get_terminal_status(self):
        command = generate_command(Commands.GET_STATUS)
        status = TerminalStatus(self.send(command))
        return status

    def get_storage_status(self):
        command = generate_command(Commands.GET_FISCAL_STORAGE_STATUS)
        status = FiscalStorageStatus(self.send(command))
        return status

    def get_reg_status(self):
        command = generate_command(Commands.REGISTRATION_PARAMETERS)
        status = RegStatus(self.send(command))
        return status

    def get_fiscal_document(self, document_num: int):
        command = generate_command(Commands.GET_DOCUMENT,
                                   document_num.to_bytes(4, 'little') + int.to_bytes(0, 1, 'big'))
        document = FiscalDocument(self.send(command))
        return document
