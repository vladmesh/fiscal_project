import asyncio
from typing import Any

from aiomisc.service.periodic import PeriodicService

from core.sources.Source_Helper import construct
from core.redis_api.RedisApi import RedisApi
from core.webax_api.WebaxHelper import WebaxHelper


class FinkPeriodic(PeriodicService):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.redis = RedisApi()
        self.webax = WebaxHelper()

    async def callback(self):
        tickets = set()
        funcs = []  # TODO тут бы нужно поставить таймауты и посмотреть в сторону asyncio.wait и отменяемых задач
        # иначе зависание одного источника приведёт к невозможности выгрузки по остальным
        asuop_settings_list = await self.webax.get_sources_settings()
        companies = await self.redis.get_companies()  # тут получаем полный список закэшированных компаний.
        for asuop_settings in asuop_settings_list:
            asoup_helper = construct(asuop_settings)
            if asoup_helper:
                funcs.append(asoup_helper.get_new_tickets(companies))
        group = asyncio.gather(*funcs)
        results = await group
        tickets = tickets.union(*results)
        for ticket in tickets:
            await self.redis.insert_ticket(ticket)
