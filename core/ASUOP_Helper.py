from abc import ABC, abstractmethod

import datetime as dt
from typing import List

from core.asyncdb.MSSQLHelper import MSSql
from core.asyncdb.MySqlHelper import MySqlHelper
from core.asyncdb.OracleHelper import OracleHelper
from core.entities.entities import Company, SourceSettings
from core.utils import change_timezone
from core.webax_api.WebaxHelper import WebaxHelper
from revise_service.entities import SourceType, ReviseTicket


class BULRecord:
    def __init__(self, record):
        self.date = record['DATE']
        self.route_id = record['ROUTEID']
        self.spool_id = record['SPOOLID'].upper()
        self.ticket_number_from = record['TICKETNUMBERFROM']
        self.ticket_number_to = record['TICKETNUMBERTO']
        self.release = record['RELEASE']
        self.id = record['RECID']
        self.vat = "NONDS" if record['VAT'] == 6 else "NDS20"
        self.created_dt = record['DATEINS']
        self.inn = record['INN_RU']
        self.kpp = record['KPP_RU']

    def get_tickets(self):
        tickets = set()
        for i in range(self.ticket_number_from, self.ticket_number_to):
            ticket = ReviseTicket()
            ticket.date_trip = self.date
            ticket.date_ins = self.created_dt
            series_split = self.spool_id.split('-')
            if i == 1000:
                tmpnum = '000'
            else:
                tmpnum = f"{'0' * (3 - len(str(i)))}{i}"
            ticket.ticket_number = f"{series_split[2]}{tmpnum}"
            ticket.payment_type = 1
            ticket.inn = self.inn.strip()
            ticket.kpp = self.kpp.strip()
            # ticket.type = self.fiscal_type
            ticket.price = int(float(series_split[3]) * 100)
            ticket.ticket_series = f"{series_split[0]}-{series_split[1]}-{ticket.price}"
            ticket.ticket_series = ticket.ticket_series.upper()
            ticket.recid = self.id
            ticket.route_id = self.route_id
            ticket.vat = self.vat
            ticket.release = self.release
            ticket.spool_id = self.spool_id
            tickets.add(ticket)
        return tickets


class SourceHelper(ABC):
    @abstractmethod
    async def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, companies: List[Company]) -> set:
        return set()

    @abstractmethod
    async def get_new_tickets(self, companies: List[Company] = None) -> set:
        return set()

    def __init__(self, settings: SourceSettings):
        self.settings = settings


class SourceMysqlHelper(SourceHelper):
    """База MySql, используется в СПБ для хранения безналичных транзакций"""

    async def get_new_tickets(self, companies: List[Company] = None) -> set:
        pass

    def __init__(self, settings: SourceSettings):
        self.mysqlHelper = MySqlHelper(settings.address, settings.database_name,
                                       settings.login,
                                       settings.password)
        SourceHelper.__init__(self, settings)

    async def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, companies: List[Company]):
        answer = set()
        inn_kpp_str = ','.join([f"{x.inn + x.kpp}" for x in companies])
        inn_kpp_str = f"({inn_kpp_str})"
        command = self.settings.query_revise.replace('{date_from}', str(date_from)).replace('{date_to}', str(date_to))
        command = command.replace('{companies}', inn_kpp_str)
        rows = await self.mysqlHelper.execute_query(command)
        for row in rows:
            ticket = ReviseTicket()
            ticket.init_from_mysql_transaction(row)
            answer.add(ticket)
        return answer


class SourceHelperMsSqlAxBUL(SourceHelper):
    """Аксаптовские БД MSSQL, в них хранится наличка по СПБ"""

    async def get_new_tickets(self, companies: List[Company] = None) -> set:
        return set()

    def __init__(self, local_settings: SourceSettings):
        self.mssql_helper = MSSql(local_settings.address, local_settings.database_name, local_settings.login,
                                  local_settings.password)
        SourceHelper.__init__(self, local_settings)

    async def get_intervals_on_date(self, date_from: dt.datetime, date_to: dt.datetime):
        date_from_str = date_from.strftime("%Y-%m-%dT%H:%M:%S")
        date_to_str = date_to.strftime("%Y-%m-%dT%H:%M:%S")
        answer = []
        command = self.settings.query_revise.replace('{date_from}', date_from_str).replace('{date_to}', date_to_str)
        rows = await self.mssql_helper.execute(command)
        for row in rows:
            bul_record = BULRecord(row)
            answer.append(bul_record)
        return answer

    async def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, companies: List[Company]) -> set:
        answer = set()
        intervals = await self.get_intervals_on_date(date_from, date_to)
        for interval in intervals:
            answer = answer.union(interval.get_tickets())
        return answer


class SourceHelperMsSqlTrans(SourceHelper):
    """Вьюхи с транзакциями"""

    async def get_new_tickets(self, companies: List[Company] = None) -> set:
        return set()

    def __init__(self, settings: SourceSettings):
        self.mssql_helper = MSSql(settings.address, settings.database_name, settings.login,
                                  settings.password)
        SourceHelper.__init__(self, settings)

    async def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, companies: List[Company]) -> set:
        date_from_str = date_from.strftime("%Y-%m-%dT%H:%M:%S")
        date_to_str = date_to.strftime("%Y-%m-%dT%H:%M:%S")
        answer = set()
        party_ids_str = ','.join([f"'{x.id}'" for x in companies])
        party_ids_str = f'({party_ids_str})'
        command = self.settings.query_revise.replace('{date_from}', date_from_str).replace('{date_to}', date_to_str)
        command = command.replace('{companies}', party_ids_str)
        rows = await self.mssql_helper.execute(command)
        for row in rows:
            ticket = ReviseTicket()
            ticket.init_from_view_transaction(row)
            if row['axDataAreaId'] == 'nkz':
                if ticket.inn == '' and ticket.kpp == '' and ticket.date_trip < dt.datetime(2021, 4, 15):
                    # костыль для сверки старых транзакций по Нкз
                    ticket.inn = '7819027463'
                    ticket.kpp = '425345001'
            answer.add(ticket)
        return answer


class SourceHelperOracleASUOP(SourceHelper):
    """АСУОП Оракл"""

    async def get_new_tickets(self, companies: List[Company] = None) -> set:
        return set()

    async def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, companies: List[Company]) -> set:
        webax_helper = WebaxHelper()
        asuop_settings = webax_helper.get_asuop_settings([x.id for x in companies])
        divisions_list = asuop_settings.get_divisions()
        divisions_str = ','.join(divisions_list)
        divisions_str = f"({divisions_str})"
        command = self.settings.query_revise.replace('{start}', f'{date_from}').replace('{end}', f'{date_to}')
        command = command.replace('{comp}', divisions_str)

        answer = set()
        rows = await self.oracle_helper.execute(command)
        for row in rows:
            ticket = ReviseTicket()
            ticket.init_from_oracle(row)
            answer.add(ticket)
        return answer

    def __init__(self, settings: SourceSettings):
        port_str = ''
        if settings.port:
            port_str = ':'+str(settings.port)
        self.oracle_helper = OracleHelper(f'{settings.login}/{settings.password}@{settings.address}{port_str}'
                                          f'/{settings.database_name}')
        SourceHelper.__init__(self, settings)


def construct(asuop_settings: SourceSettings) -> SourceHelper:
    if asuop_settings.type == SourceType.MSSQL_BUL:
        return SourceHelperMsSqlAxBUL(asuop_settings)
    if asuop_settings.type == SourceType.MySql:
        return SourceMysqlHelper(asuop_settings)
    if asuop_settings.type == SourceType.MSSQL_Trans:
        return SourceHelperMsSqlTrans(asuop_settings)
    if asuop_settings.type == SourceType.Oracle_ASUOP:
        return SourceHelperOracleASUOP(asuop_settings)
    # raise Exception(f"Обработчик для типа источника {asuop_settings.type} не реализован")


async def sources_cache_tickets(utc_date_from: dt.datetime, utc_date_to: dt.datetime, companies=None) -> set:
    if companies is None:
        companies = []
    webax = WebaxHelper()
    tickets = set()
    asuop_settings_list = await webax.get_sources_settings()
    for asuop_settings in asuop_settings_list:
        asoup_helper = construct(asuop_settings)
        if asoup_helper:
            tickets = tickets.union(await asoup_helper.get_tickets_on_date(utc_date_from, utc_date_to, companies))
    return tickets
