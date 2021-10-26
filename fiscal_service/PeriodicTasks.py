from typing import Any

from aiomisc.service.periodic import PeriodicService

from core.asyncdb.PostgresHelper import PostgresAsyncHelper, PostgresHelperDev, PostgresHelperTmp
from core.redis_api.RedisApi import RedisApi
from fiscal_service.CashboxSender import CashboxSender
import asyncio


class FiscalPeriodic(PeriodicService):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.redis_api = RedisApi()

    async def callback(self):
        print('periodic_fiscal')
        unfiscal_tickets = await self.redis_api.get_new_tickets()
        if unfiscal_tickets:
            for ticket in unfiscal_tickets:
                try:
                    cashbox = await self.redis_api.get_cashbox_for_ticket(ticket)
                    sender = CashboxSender(cashbox.ip, cashbox.port)
                    loop = asyncio.get_event_loop()
                    loop.create_task(sender.fiscal_ticket(ticket))
                except:
                    pass  # TODO Send ERRORS
