from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, post_load, validate

from datetime import datetime

from fiscal_service.TerminalAnswer import TerminalStatus, FiscalStorageStatus, RegStatus


def init_answer_from_status_answers(terminal_status: TerminalStatus,
                                    fn_status: FiscalStorageStatus,
                                    reg_status: RegStatus):
    fn_number = terminal_status.factoryNum
    is_session_open = fn_status.SessionIsOpen
    factory_number = terminal_status.factoryNum
    date_time = datetime.strptime(terminal_status.DateTime, "%Y-%m-%dT%H:%M:%S")
    qty_docs = fn_status.qty
    if reg_status:
        inn = reg_status.inn
        reg_num = reg_status.regNum
        last_doc_date_time = datetime.strptime(fn_status.DateTimeLastDocument, "%Y-%m-%dT%H:%M:%S")
    else:
        inn = None
        reg_num = None
        last_doc_date_time = None
    return GetCashboxDataAnswer(fn_number, is_session_open, factory_number, date_time, inn, reg_num, qty_docs,
                                last_doc_date_time)


@dataclass
class GetCashboxDataAnswer:
    fn_number: int
    is_session_open: bool
    factory_number: int
    date_time: datetime
    inn: Optional[str]
    reg_num: Optional[str]
    qty_docs: Optional[int]
    last_doc_date_time: Optional[datetime]


class CashboxDataAnswerSchema(Schema):
    fn_number = fields.Integer()
    is_session_open = fields.Boolean()
    factory_number = fields.Integer()
    date_time = fields.DateTime()
    inn = fields.String(validate=validate.Length(equal=12), allow_none=True)
    reg_num = fields.String(allow_none=True)
    qty_docs = fields.Integer(validate=validate.Range(max=250000))
    last_doc_date_time = fields.DateTime(allow_none=True)

    @post_load
    def make_model(self, data, **kwargs):
        return GetCashboxDataAnswer(**data)
