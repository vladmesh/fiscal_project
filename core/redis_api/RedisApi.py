import asyncio

import aioredis

from core.entities.entities import Company
from core.entities.entity_schemas import CompanySchema, OfdSchema, InstallPlaceSchema, CashboxSchema, EntitySchema
from core.webax_api.WebaxHelper import WebaxHelper


class RedisApi:
    """Класс для взаизмодействия с очередями Redis"""

    def __init__(self):
        self.redis = aioredis.from_url('redis://localhost', decode_responses=True, encoding="utf-8")
        self.webax = WebaxHelper()
        self.lock = asyncio.Lock()

    async def get_new_tickets(self) -> list:
        tickets = await self.redis.get("tickets")
        return tickets

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

    async def get_company_by_inn_kpp(self, inn: str, kpp: str):
        keys = await self.redis.hkeys(CompanySchema.key)
        for key in [str(x) for x in keys]:
            company: Company = await self.get_entity(key, CompanySchema())
            if company.inn == inn and company.kpp == kpp:
                return company

    async def get_cashbox_for_ticket(self, ticket):
        free_cashbox = await self.redis.hget(ticket.company_id, 1)
        return free_cashbox
