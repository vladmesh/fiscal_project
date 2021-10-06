from typing import Any

from aiomisc.service.periodic import PeriodicService
from abc import abstractmethod

from fink_service.DocumentChecker import DocumentChecker
from FiscalSender import FiscalSender
from core.asyncdb import OracleHelper
from core.asyncdb import FinkHelper, SettingsHelper
from core.entities.Ticket import Ticket
from core.entities import SourceSettings
import datetime as dt

from core.utils import change_timezone


class SourcePeriodic(PeriodicService):
    """Абстрактный класс, отвечает за опрос источника по таймеру и выгрузку билетов"""

    def __init__(self, source_settings, **kwargs: Any):
        super().__init__(**kwargs)
        self.fiscal_api = FiscalSender()
        self.checker = DocumentChecker()
        self.source_settings = source_settings

    async def callback(self):
        tickets = await self.get_unfiscalized_tickets()
        for ticket in tickets:
            fiscal_answer = await self.fiscal_api.send_ticket(ticket)
            if fiscal_answer['status'] == 'wait':
                uid = fiscal_answer['uuid']
                await self.checker.check_uid(uid)
            else:
                await self.handle_error(fiscal_answer['error'])

    @abstractmethod
    async def get_unfiscalized_tickets(self):
        pass

    async def handle_error(self, param):
        pass


class PeriodicOracleASUOP(SourcePeriodic):
    """Классический АСУОП на базе оракл, на 07.21 работает в Влг, Сочи, ПТЗ"""

    def __init__(self, source_settings, **kwargs: Any):
        super().__init__(source_settings, **kwargs)
        conn_string = f'{source_settings.login}/{source_settings.password}@{source_settings.address}:1545/' \
                      f'{source_settings.db_name}'
        self.oracle_helper = OracleHelper(conn_string)
        self.fink_helper = FinkHelper()
        self.global_settings = SettingsHelper().getSettings()

    async def get_unfiscalized_tickets(self):
        date_from = self.fink_helper.get_last_query_time()
        date_from = date_from.replace(tzinfo=None)
        now = dt.datetime.now()
        date_to = min(date_from + dt.timedelta(hours=5), now - dt.timedelta(seconds=5))
        return self.get_tickets_on_date(date_from, date_to, self.global_settings.timezone)

    def get_tickets_on_date(self, date_from: dt.datetime, date_to: dt.datetime, timezone):
        answer = set()
        divisions = self.fink_helper.get_divizions()
        fink_companies = self.fink_helper.get_companies()
        fink_routes = self.fink_helper.get_routes()
        divisions_str = ','.join([f"'{x}'" for x in divisions])
        fink_query = self.source_settings.query_new_tickets
        date_from = change_timezone(date_from, 'utc', timezone)
        date_to = change_timezone(date_to, 'utc', timezone)
        q = fink_query.replace('{comp}', f'{divisions_str}').replace('{start}',
                                                                     f"{date_from.strftime('%d.%m.%Y %H:%M:%S')}")
        q = q.replace('{end}', f"{date_to.strftime('%d.%m.%Y %H:%M:%S')}")
        records = self.oracle_helper.execute(command=q)
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


def construct(source_settings: SourceSettings) -> SourcePeriodic:
    if source_settings.source_type == 2:
        return PeriodicOracleASUOP(interval=2, delay=0, source_settings=source_settings)
    raise Exception(f"Обработчик для типа источника {source_settings.source_type} не реализован")
