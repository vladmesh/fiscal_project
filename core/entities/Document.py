"""
Фискальный документ. Любая сущность, которую возвращает ККТ. Чеки, отчёты об открытии/закрытии смены,
отчёты о регистрации/перерегистрации
"""
from datetime import datetime


class Document:
    def __init__(self, record=None):  # инициализируем из записи
        if record:
            self.id = record['id']
            self.fiscal_number = record['fiscal_number']
            self.fiscal_sign = record['fiscal_sign']
            self.num_in_session = record['num_in_session']
            self.date_fiscal = record['date_fiscal']
            self.document_type = record['type_id']
            self.company_id = record['company_id']
            self.price = record['price']
            self.fn_number = record['fn_number']
        else:
            self.inn = ''
            self.kpp = ''
            self.session_num = 0
            self.price = 0
            self.operation_type = ''
            self.company_id = -1
            self.cashbox_id = -1
            self.cashbox_factory_num = ''
            self.cashbox_reg_num = ''
            self.paymenttype = 'null'
