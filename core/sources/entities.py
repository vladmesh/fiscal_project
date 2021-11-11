import logging
from datetime import datetime, timedelta

from core.entities.Enums import Tax, Vat, PaymentType, DocumentType
from core.utils import change_timezone
from dateutil import tz


class SourceTicket:
    def __init__(self, record=None):
        self.company_id = None
        if record:
            self.id = record['id']
            self.ticket_series = record['ticket_series']
            self.ticket_number = record['ticket_number']
            self.date_ins = record['date_ins_asuop']
            self.payment_type = PaymentType(record['payment_type'])
            self.date_trip = record['date_trip']
            if 'inn' in record:
                self.inn = record['inn']
            if 'kpp' in record:
                self.kpp = record['kpp']
            if 'company_id' in record:
                self.company_id = record['company_id']
            self.vat = record['vat_name']
            self.tax = record['tax_name']
            if self.tax == 'SIMPEXP':
                self.tax = Tax.SIMPEXP
            elif self.tax == 'GEN':
                self.tax = Tax.GEN
            elif self.tax == 'SIMP':
                self.tax = Tax.SIMP
            else:
                raise Exception(f"Неизвестный тип налогообложения {self.tax}")
            if self.vat == 'NONDS':
                self.vat = Vat.NONDS
            elif self.vat == 'NDS20':
                self.vat = Vat.NDS20
            else:
                raise Exception(f"Неизвестная налоговая ставка {self.vat}")
            self.price = record['price']

    def del_init_from_service(self, record):
        self.id = record['ticketid']
        self.ticket_series = record['ticketseries']
        self.ticket_number = record['ticketnumber']
        self.date_ins = record['dateins']
        self.date_trip = record['datetrip']
        self.inn = record['inn']
        self.kpp = record['kpp']
        self.vat = record['vat']
        self.tax = record['tax']
        self.price = record['price']

    def init_from_validator_trans(self, record):
        self.id = record['RECID']
        self.tax = Tax.GEN
        self.vat = Vat.NDS20
        if record['PASSCARDTYPEID'] == 150:
            self.payment_type = PaymentType.CASH
        else:
            self.payment_type = PaymentType.NON_CASH
        self.price = int(record['AMOUNTORIG'])
        self.date_ins = record['CREATEDDATETIME']
        release_date = record['DATERELEASE']
        td = timedelta(seconds=record['TIMEABS'])
        self.date_trip = release_date + td
        self.date_trip = change_timezone(self.date_trip, 'UTC', 'UTC')
        self.date_ins = change_timezone(self.date_ins, 'UTC', 'UTC')
        self.ticket_series = f"{release_date.strftime('%d%m%Y')}-{record['MODULEID']}"

        s = td.total_seconds()
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.ticket_number = '{:02}{:02}{:02}'.format(int(hours), int(minutes), int(seconds))
        self.inn = '4705021744'
        self.kpp = '771545001'

    def init_from_oracle(self, record, timezone):
        self.id = record['ID']
        self.ticket_series = record['TICKETSERIES']
        self.ticket_number = str(record['TICKETNUMBER'])
        self.payment_type = PaymentType(int(record['PAYMENTTYPE']))
        self.date_ins = change_timezone(record['INS_DATE'], timezone, 'UTC')
        self.date_trip = change_timezone(record['DATETRIP'], timezone, 'UTC')
        self.price = int(record['PRICE'])

    def init_from_view_transaction(self, record):
        timezone = 'Asia/Novokuznetsk' if record['axDataAreaId'] == 'nkz' else 'Europe/Moscow'  # TODO вынести в
        # какую-нибудь настройку
        self.id = record['axRecId']
        trans_date_time = record['rrTransDateTimeUtc0']
        self.price = 0 if record['rrAmountTerminal'] is None else int(record['rrAmountTerminal'] * 100)
        tid = record['rrTerminalId']
        self.ticket_number = record['rrPaymentERN']
        if record['axPassCardTypeId'] == 14:
            self.payment_type = PaymentType.CASH
        elif record['axPassCardTypeId'] == 32:
            self.payment_type = PaymentType.NON_CASH
        else:
            raise Exception("Неверный тип карты")

        self.inn = record['axINN_RUCalc4Fiscal']
        self.kpp = record['axKPPU_RUCalc4Fiscal']
        self.date_ins = record['rrRegDateTimeUtc0']
        self.date_ins = change_timezone(self.date_ins, 'UTC', 'UTC')
        date_release = record['axDateRelease']
        # тут небольшой костыль, из вьюхи возвращается то дата, то строка, можно у Димы попросить унифицировать
        if type(date_release) == str:
            date_release = datetime.strptime(record['axDateRelease'], '%Y-%m-%d')
        date_release = datetime(date_release.year, date_release.month, date_release.day)
        time_abs = record['axTimeAbs']
        local_dt_from_ax = date_release + timedelta(seconds=time_abs)
        self.date_trip = change_timezone(local_dt_from_ax, timezone, 'UTC')
        local_dt_from_terminal = change_timezone(trans_date_time, 'UTC', timezone)
        self.ticket_series = local_dt_from_terminal.strftime("%d%m%Y%H%M%S") + f"-{tid}"
        if local_dt_from_terminal != local_dt_from_ax:
            pass  # TODO рассылка предупреждений

    def init_from_mysql_transaction(self, record):
        self.id = record['record_id']
        self.tax = Tax.GEN
        self.vat = Vat.NONDS
        self.payment_type = PaymentType.NON_CASH
        self.price = record['amount']
        td = record['terminal_date']
        self.date_ins = change_timezone(record['created_date'], 'UTC', 'UTC')
        self.date_trip = td
        terminal_id = record['terminal_id']
        if terminal_id == '':
            terminal_id = record['terminal_reg_num']
        self.ticket_series = td.strftime("%m%d%Y") + "-" + terminal_id
        self.ticket_number = str(td.hour * 60 * 60 + td.minute * 60 + td.second)
        if record['bank_source'] == 'Gazprombank':
            self.ticket_number += '-' + str(record['record_id'])
        self.inn = record['fiscal_inn']
        self.kpp = record['fiscal_kpp']

    def __str__(self):
        return self.ticket_series + '\t' + self.ticket_number

    def __eq__(self, other):
        """
        Для быстрой сверки между источниками используем немного магии
        Переопределяем методы сравнения так, чтобы объекты с одинаковыми значениями ключевых полей
        считались одним объектом, это помогает искать нужный документ по ключевым полям за O(1)
        """
        if not isinstance(other, SourceTicket):
            return False

        return (self.ticket_number == other.ticket_number and
                self.ticket_series == other.ticket_series and self.inn == other.inn and self.price == other.price)

    def __hash__(self):
        return hash((self.ticket_number, self.ticket_series, self.inn, self.price))


class SourceDocument:
    def __init__(self, record=None):  # инициализируем из записи
        if record:
            self.id = record['id']
            self.fiscal_number = record['fiscal_number']
            self.fn_number = record['fn_number']
            self.fiscal_sign = record['fiscal_sign']
            self.session_num = record['session_num']
            self.num_in_session = record['num_in_session']
            self.date_fiscal = record['date_fiscal']
            self.price = record['price']
            self.additional_prop = record['additional_prop']
            self.ticket_id = record['ticket_id']
            if 'tax_name' in record:
                self.tax = record['tax_name']
            if 'vat_name' in record:
                self.vat = record['vat_name']
            if self.vat == 'NONDS':
                self.vat = Vat.NONDS
            elif self.vat == 'NDS20':
                self.vat = Vat.NDS20
            else:
                raise Exception(f"Неизвестная налоговая ставка {self.vat}")
            if self.tax == 'SIMPEXP':
                self.tax = Tax.SIMPEXP
            elif self.tax == 'GEN':
                self.tax = Tax.GEN
            elif self.tax == 'SIMP':
                self.tax = Tax.SIMP
            else:
                raise Exception(f"Неизвестный тип налогообложения {self.tax}")
            self.type = DocumentType(record['type_id'])
            self.payment_type = PaymentType(record['payment_type'])
            if 'inn' in record:
                self.inn = record['inn']
            if 'kpp' in record:
                self.kpp = record['kpp']
            if 'company_id' in record:
                self.company_id = record['company_id']

    @staticmethod
    def to_utc(local_date, timezone):
        from_zone = tz.gettz(timezone)
        to_zone = tz.gettz('utc')
        local = local_date.replace(tzinfo=from_zone)
        utc = local.astimezone(to_zone)
        return utc

    def init_from_ofd_api(self, record, timezone):
        if 'DecimalFiscalSign' in record:
            self.fiscal_sign = int(record['DecimalFiscalSign'])
        else:
            self.fiscal_sign = -1
        self.id = record['Id']
        self.date_fiscal = self.to_utc(datetime.strptime(record["DocDateTime"], '%Y-%m-%dT%H:%M:%S'), timezone)
        self.fiscal_number = int(record['DocNumber'])
        self.num_in_session = int(record['ReceiptNumber'])
        self.fn_number = int(record['FnNumber'])
        self.session_num = record['DocShiftNumber']
        self.price = record['TotalSumm']
        if record['CashSumm'] > 0:
            self.payment_type = PaymentType.CASH
        elif record['ECashSumm'] > 0:
            self.payment_type = PaymentType.NON_CASH
        else:
            self.payment_type = PaymentType.CASH

        if 'TaxNaSumm' in record and record['TaxNaSumm'] > 0:
            self.vat = Vat.NONDS
        else:
            self.vat = Vat.NDS20  # сюда же нолики

        if record['IsCorrection']:
            self.type = DocumentType.correction
        else:
            self.type = DocumentType.receipt
        if 'TaxationType' in record:
            tax_type = record['TaxationType']
            if tax_type == 1:
                self.tax = Tax.GEN
            if tax_type == 2:
                self.tax = Tax.SIMP
            if tax_type == 3:
                self.tax = Tax.SIMPEXP
        self.additional_prop = ''
        if 'AdditionalRequisite' in record:
            self.additional_prop = record['AdditionalRequisite']

        if record['OperationType'] == "Income":
            self.operation_type = 1
        elif record['OperationType'] == "RefundIncome":
            self.operation_type = 2
            self.type = 5
            self.price *= -1
        else:
            raise Exception(f"{record['OperationType']} - неизвестный тип операциии")

        if record['Depth'] > 1:
            logging.error(f"Несколько билетов в чеке {self.id}")

    def __eq__(self, other):
        """
        Для быстрой сверки между источниками используем немного магии
        Переопределяем методы сравнения так, чтобы объекты с одинаковыми значениями ключевых полей
        считались одним объектом, это помогает искать нужный документ по ключевым полям за O(1)
        """
        if not isinstance(other, SourceDocument):
            return False

        return (self.fn_number == other.fn_number and
                self.fiscal_number == other.fiscal_number and self.num_in_session == other.num_in_session
                and self.price == other.price and (self.payment_type == other.payment_type or self.price == 0)
                and self.type == other.type)

    def __hash__(self):
        return hash((self.fn_number, self.fiscal_number, self.num_in_session, self.price, self.payment_type, self.type))
