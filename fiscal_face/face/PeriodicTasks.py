from typing import Any

from aiomisc.service.periodic import PeriodicService

from core.redis_api.RedisApi import RedisApi


class FiscalPeriodic(PeriodicService):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.redis_api = RedisApi()

    async def callback(self):
        await self.redis_api.update_data()
