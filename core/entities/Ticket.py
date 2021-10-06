from datetime import datetime, timedelta

from core.utils import change_timezone


class Ticket:
    def __init__(self, record=None):
        if record:
            self.id = record['id']
            self.ticket_series = record['ticket_series']
            self.ticket_number = record['ticket_number']
           # self.date_ins = record['date_ins_asuop']
            self.payment_type = record['payment_type']
            self.date_trip = record['date_trip']
            self.company_id = record['company_id']
            self.vat = record['vat_id']
            self.price = record['price']
            #self.tax = record['tax_id']

    def init_from_oracle(self, record, timezone):
        self.id = record['ID']
        self.ticket_series = record['TICKETSERIES']
        self.ticket_number = str(record['TICKETNUMBER'])
        self.payment_type = int(record['PAYMENTTYPE'])
        self.date_ins = change_timezone(record['INS_DATE'], timezone, 'utc')
        self.date_trip = change_timezone(record['DATETRIP'], timezone, 'utc')
        self.price = int(record['PRICE'])

    def init_from_ax_transaction(self, record, timezone):
        self.id = record['axRecId']
        trans_date_time = record['rrTransDateTimeUtc0']
        self.price = 0 if record['rrAmountTerminal'] is None else int(record['rrAmountTerminal'] * 100)
        tid = record['rrTerminalId']
        self.ticket_number = record['rrPaymentERN']
        self.payment_type = 1
        self.inn = record['axINN_RUCalc4Fiscal']
        self.kpp = record['axKPPU_RUCalc4Fiscal']
        self.date_ins = record['rrRegDateTimeUtc0']
        release_date = datetime.strptime(record['axDateRelease'], '%Y-%m-%d')
        time_abs = record['axTimeAbs']
        local_dt_from_ax = release_date + timedelta(seconds=time_abs)
        self.date_trip = change_timezone(local_dt_from_ax, timezone, 'utc')
        local_dt_from_terminal = change_timezone(trans_date_time, 'utc', timezone)
        self.ticket_series = local_dt_from_terminal.strftime("%d%m%Y%H%M%S") + f"-{tid}"
        
    def init_from_mysql_transaction(self, record):
        self.id = record['record_id']
        self.tax = "GEN"
        self.vat = "NONDS"
        self.payment_type = 2
        self.price = record['amount']
        td = record['terminal_date']
        self.date_ins = record['created_date']
        self.date_trip = td
        self.ticket_series = td.strftime("%m%d%Y") + "-" + record['terminal_id']
        self.ticket_number = str(td.hour * 60 * 60 + td.minute * 60 + td.second)

    def __str__(self):
        return self.ticket_series + '\t' + self.ticket_number

    def __eq__(self, other):
        """
        Для быстрой сверки между источниками используем немного магии
        Переопределяем методы сравнения так, чтобы объекты с одинаковыми значениями ключевых полей
        считались одним объектом, это помогает искать нужный документ по ключевым полям за O(1)
        """
        if not isinstance(other, Ticket):
            return False

        return (self.ticket_number == other.ticket_number and
                self.ticket_series == other.ticket_series)

    def __hash__(self):
        return hash((self.ticket_number, self.ticket_series))
