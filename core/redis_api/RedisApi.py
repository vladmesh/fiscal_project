import asyncio

import aioredis

from core.entities.entity_schemas import CompanySchema, OfdSchema, InstallPlaceSchema, CashboxSchema, EntitySchema
from core.webax_api.WebaxHelper import WebaxHelper


class RedisApi:
    """Класс для взаизмодействия с очередями Redis"""

    def __init__(self):
        self.redis = aioredis.from_url('redis://localhost')
        self.webax = WebaxHelper()
        self.lock = asyncio.Lock()

    async def get_new_tickets(self):
        await self.redis.set("ticket", 't1')
        ticket = await self.redis.get("ticket")
        return [ticket]

    async def get_cashboxes(self):
        pass

    async def update_data_records(self, records: list, key: str, schema):
        for record in records:
            record_json = schema.dumps(record)
            await self.redis.hset(key, record.id, record_json)

    async def update_data(self):
        ax_dicts = await self.webax.get_dictionaries()
        await self.update_data_records(ax_dicts[CompanySchema.key], CompanySchema.key, CompanySchema())
        await self.update_data_records(ax_dicts[OfdSchema.key], OfdSchema.key, OfdSchema())
        await self.update_data_records(ax_dicts[InstallPlaceSchema.key], InstallPlaceSchema.key, InstallPlaceSchema())
        await self.update_data_records(ax_dicts[CashboxSchema.key], CashboxSchema.key, CashboxSchema())

    async def get_entity(self, entity_id, schema: EntitySchema):
        entity_json = await self.redis.hget(schema.key, entity_id)
        answer = schema.loads(entity_json)
        return answer
