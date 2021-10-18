from typing import Any

from aiomisc.service.periodic import PeriodicService

from core.asyncdb.PostgresHelper import PostgresAsyncHelper, PostgresHelperDev, PostgresHelperTmp
from core.redis_api.RedisApi import RedisApi


class FiscalPeriodic(PeriodicService):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.redis_api = RedisApi()

    async def callback(self):
        print('periodic_fiscal')
        postgres_helper_dev = PostgresHelperDev()
        postgres_helper_tmp = PostgresHelperTmp()
        unfiscal_tickets = await postgres_helper_tmp.get_unfiscal_tickets()
        for ticket in unfiscal_tickets:
            try:
                await postgres_helper_dev.insert_ticket_dev(ticket)
            except:
                pass
        uniported_documents = await postgres_helper_dev.get_unimported_documents()
        for doc in uniported_documents:
            ticket = await postgres_helper_tmp.get_ticket(doc.ticket_id)
            doc.ticket_id = ticket.id
            await postgres_helper_tmp.insert_document(doc)
            await postgres_helper_dev.set_doc_imported(doc.id)

