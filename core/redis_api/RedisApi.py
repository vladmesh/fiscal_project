import asyncio

import aioredis

from core.WebaxHelper import WebaxHelper
from core.entities.Company import Company
from core.entities.InstallPlace import InstallPlace
from core.entities.Ofd import Ofd
from schemas.CashboxSchema import CashboxSchema, CashboxListSchema
from schemas.CompanySchema import CompanySchema
from schemas.InstallPlaceSchema import InstallPlaceSchema
from schemas.OfdSchema import OfdSchema
from schemas.UpdateDictionariesSchema import UpdateDictionariesSchema


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
        answer_json = await self.webax.get_dictionaries()
        answer_json = answer_json['ActionData']
        request_schema = UpdateDictionariesSchema()
        request_data = request_schema.loads(answer_json)
        await self.update_data_records(request_data['companies'], Company.redis_key, CompanySchema())
        await self.update_data_records(request_data['ofds'], Ofd.redis_key, OfdSchema())
        await self.update_data_records(request_data['install_places'], InstallPlace.redis_key,
                                       InstallPlaceSchema())

        answer_json = await self.webax.get_cashboxes()
        answer_json = answer_json['ActionData']
        cashboxes = CashboxListSchema().loads(answer_json)
        await self.update_data_records(cashboxes['cashboxes'], 'cashboxes', CashboxSchema())
        print("ДАННЫЕ ОБНОВЛЕНЫ")

    async def get_entity(self, entity_id, cls):
        entity_json = await self.redis.hget(cls.redis_key, entity_id)
        answer = cls.marshmallow_schema.loads(entity_json)
        return answer
