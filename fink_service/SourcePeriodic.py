from typing import Any

from aiomisc.service.periodic import PeriodicService
from abc import abstractmethod

from core.ASUOP_Helper import construct
from core.redis_api.RedisApi import RedisApi
from core.webax_api.WebaxHelper import WebaxHelper
from fink_service.DocumentChecker import DocumentChecker
from FiscalSender import FiscalSender
from core.asyncdb import OracleHelper

import datetime as dt

from core.utils import change_timezone


class SourcePeriodic(PeriodicService):
    def __init__(self,  **kwargs: Any):
        super().__init__(**kwargs)
        self.fiscal_api = FiscalSender()
        self.redis = RedisApi()
        self.webax = WebaxHelper()
        self.checker = DocumentChecker()

    async def callback(self):
        sources = await self.webax.get_sources_settings()
        tickets = set()
        for asuop_settings in sources:
            asoup_helper = construct(asuop_settings)
            if asoup_helper:
                tickets = tickets.union(await asoup_helper.get_new_tickets())
        for ticket in tickets:
            await self.fiscal_api.send_ticket(ticket)

    @abstractmethod
    async def get_unfiscalized_tickets(self):
        pass

    async def handle_error(self, param):
        pass


