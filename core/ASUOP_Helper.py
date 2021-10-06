from abc import ABC, abstractmethod

import datetime as dt

from core.MSSQLHelper import MSsqlOLEDB, MSSql
from core.MySqlHelper import MySqlHelper
from core.OracleHelper import OracleHelper
from core.PostgresHelper import FinkHelper, SettingsHelper
from core.Ticket import Ticket
from core.TicketRecord import BULRecord
from core.asuop_settings import ASUOP_settings
from core.utils import change_timezone


class ASUOPHelper(ABC):
    @abstractmethod
    def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, timezone) -> set:
        return set()

    def __init__(self, settings: ASUOP_settings):
        self.settings = settings


class ASUOP_Oracle_Helper(ASUOPHelper, OracleHelper):
    """Классический АСУОП на базе оракл, на 07.21 работает в Влг, Сочи, ПТЗ"""

    def __init__(self, settings: ASUOP_settings):
        conn_string = f'{settings.login}/{settings.password}@{settings.address}/{settings.db_name}'
        OracleHelper.__init__(self, conn_string)
        ASUOPHelper.__init__(self, settings)

    def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, timezone):
        answer = set()
        fink = FinkHelper()
        divisions = fink.get_divizions()
        fink_companies = fink.get_companies()
        fink_routes = fink.get_routes()
        divisions_str = ','.join([f"'{x}'" for x in divisions])
        fink_query = self.settings.query
        date_from = change_timezone(date_from, 'utc', timezone)
        date_to = change_timezone(date_to, 'utc', timezone)
        q = fink_query.replace('{comp}', f'{divisions_str}').replace('{start}',
                                                                     f"{date_from.strftime('%d.%m.%Y %H:%M:%S')}")
        q = q.replace('{end}', f"{date_to.strftime('%d.%m.%Y %H:%M:%S')}")
        records = self.execute(command=q)
        for record in records:
            ticket = Ticket()
            ticket.init_from_oracle(record, timezone)
            company = next(x for x in fink_companies if x.division == record['ID_DIVISION'])
            ticket.inn = company.inn
            ticket.kpp = company.kpp
            route = next(x for x in fink_routes if x.code == record['ID_ROUTE'])
            ticket.vat = route.vat
            answer.add(ticket)
        return answer


class ASUOP_MS_OLEDB_Helper(ASUOPHelper, MSsqlOLEDB):
    """Базы MSSQL с доступом через протокол OLEDB, на 06.21 такая используется в НКЗ и как вспомогательная в Сочи"""

    def __init__(self, local_settings: ASUOP_settings):
        ASUOPHelper.__init__(self, local_settings)
        MSsqlOLEDB.__init__(self, local_settings.address, local_settings.db_name)
        self.settings = SettingsHelper().getSettings()

    def get_tickets_on_date(self, date_from, date_to, timezone):
        answer = set()
        date_from_str = date_from.strftime("%Y-%m-%dT%H:%M:%S")
        date_to_str = date_to.strftime("%Y-%m-%dT%H:%M:%S")
        command = f"select  axRecId, rrTransDateTimeUtc0, rrAmountTerminal, rrTerminalId, rrPaymentERN, " \
                  f" axRouteId, rrTransRouteNum, axDateRelease, axTimeAbs, axRouteId, " \
                  f"axINN_RUCalc4Fiscal, axKPPU_RUCalc4Fiscal, " \
                  f"rrRegDateTimeUtc0 from  dbo.v_ValidatorTransImportView4Fiscal where" \
                  f" rrRegDateTimeUtc0 >= '{date_from_str}' " \
                  f"and rrRegDateTimeUtc0 < '{date_to_str}' and axPassCardTypeId = 14 " \
                  f"and axRouteId not in (24, 18) order by axRecId"
        rows = self.execute(command)
        for row in rows:
            ticket = Ticket()
            ticket.init_from_ax_transaction(row, timezone)
            answer.add(ticket)
        return answer


class ASUOP_MYSQL_SPB_HELPER(ASUOPHelper, MySqlHelper):
    """База MySql, используется в СПБ для хранения безналичных транзакций"""
    def __init__(self, local_settings: ASUOP_settings):
        ASUOPHelper.__init__(self, local_settings)
        MySqlHelper.__init__(self, local_settings.address, local_settings.db_name, local_settings.login,
                             local_settings.password)
        self.settings = SettingsHelper().getSettings()

    def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, timezone):
        answer = set()
        command = f"SELECT * FROM TicketBankTrans where created_date >= '{date_from}' and created_date < '{date_to}' "
        rows = self.execute_query(command)
        for row in rows:
            ticket = Ticket()
            ticket.init_from_mysql_transaction(row)
            answer.add(ticket)
        return answer


class ASUOP_MSSQL_AX_HELPER(ASUOPHelper, MSSql):
    """Аксаптовские БД MSSQL, в них хранится наличка по СПБ"""
    def __init__(self, local_settings: ASUOP_settings):
        ASUOPHelper.__init__(self, local_settings)
        MSSql.__init__(self, local_settings.address, local_settings.db_name, local_settings.login,
                       local_settings.password)
        self.settings = SettingsHelper().getSettings()

    def get_intervals_on_date(self, date_from: dt.datetime, date_to: dt.datetime):
        date_from_str = date_from.strftime("%Y-%m-%dT%H:%M:%S")
        date_to_str = date_to.strftime("%Y-%m-%dT%H:%M:%S")
        answer = []
        command = f"select DATE, f.ROUTEID, f.SPOOLID, TICKETNUMBERFROM, TICKETNUMBERTO, VAT, " \
                  f"RELEASE, f.RECID, f.CREATEDDATETIME, INN_RU, KPP_RU, s.PRICE from dbo.fiscalticketsforbul f" \
                  f" join dbo.A_TICKETSPOOL s on (s.SPOOLID = f.SPOOLID and s.DATAAREAID = f.DATAAREAID) " \
                  f" join dbo.RouteReleaseTypeExtLink link on (link.ROUTEID = f.ROUTEID and link.DATEFROM <= f.DATE " \
                  f" and (link.DATETO > f.DATE or link.DATETO = '1900-01-01 00:00:00') and link.DATAAREAID = " \
                  f"f.DATAAREAID) " \
                  f" join dbo.FiscalFIReleaseTypeTaxLink flink on (flink.FIReleaseType = link.ReleaseTypeExt)"
        command += f" where f.CREATEDDATETIME >= '{date_from_str}' and f.CREATEDDATETIME < '{date_to_str}'"
        command += ' order by RECID'
        rows = self.execute(command)
        for row in rows:
            bul_record = BULRecord(row)
            answer.append(bul_record)
        return answer

    def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, timezone) -> set:
        answer = set()
        intervals = self.get_intervals_on_date(date_from, date_to)
        for interval in intervals:
            answer = answer.union(interval.get_tickets())
        return answer


def construct(asuop_settings: ASUOP_settings) -> ASUOPHelper:
    if asuop_settings.source_type == 5:
        return ASUOP_MS_OLEDB_Helper(asuop_settings)
    if asuop_settings.source_type == 2:
        return ASUOP_Oracle_Helper(asuop_settings)
    if asuop_settings.source_type == 3:
        return ASUOP_MYSQL_SPB_HELPER(asuop_settings)
    if asuop_settings.source_type == 4:
        return ASUOP_MSSQL_AX_HELPER(asuop_settings)
    raise Exception(f"Обработчик для типа источника {asuop_settings.source_type} не реализован")
