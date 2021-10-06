from datetime import datetime

from fiscal_service.TerminalAnswer import TerminalStatus, FiscalStorageStatus, RegStatus
from marshmallow import Schema, fields, validate


class CashboxDataAnswer:
    def __init__(self, terminal_status: TerminalStatus, fn_status: FiscalStorageStatus, reg_status: RegStatus):
        self.fn_number = fn_status.StorageNumber
        self.is_session_open = fn_status.SessionIsOpen
        self.factory_number = terminal_status.factoryNum
        self.date_time = datetime.strptime(terminal_status.DateTime, '%Y-%m-%dT%H:%M:%S')
        self.inn = reg_status.inn
        self.reg_num = reg_status.regNum
        self.qty_docs = fn_status.qty
        if fn_status.DateTimeLastDocument:
            self.last_doc_date_time = datetime.strptime(fn_status.DateTimeLastDocument, '%Y-%m-%dT%H:%M:%S')
        else:
            self.last_doc_date_time = None


class CashboxDataAnswerSchema(Schema):
    fn_number = fields.Integer()
    is_session_open = fields.Boolean()
    factory_number = fields.Integer()
    date_time = fields.DateTime()
    inn = fields.String(validate=validate.Length(equal=12))
    reg_num = fields.String()
    qty_docs = fields.Integer()
    last_doc_date_time = fields.DateTime()
