import asyncio

from core.entities.entities import Company
from core.entities.entity_schemas import TicketSchema, DocumentSchema, CompanySchema
from core.redis_api.RedisApi import RedisApi
from server.admin.schemas.requests import InsertTicketsAsuopSchema, InsertDocumentsAsuopSchema, \
    BindDocumentsSchema
import aiohttp.web


async def load_dbf_tickets(request):
    pass
    # try:
    #     postgres = PostgresHelperDbf()
    #     redis = RedisApi()
    #     data = await request.read()
    #     schema = InsertTicketsAsuopSchema()
    #     dict_request = schema.loads(data)
    #     tickets: set = dict_request[TicketSchema.key]
    #     company: Company = await redis.get_entity(dict_request['company_id'], CompanySchema())
    #     company_id = await postgres.get_company_id_by_inn_kpp(company.inn, company.kpp)
    #     if not company_id:
    #         return aiohttp.web.Response(text='{"error": "Wrong Company"}')
    #     for ticket in tickets:
    #         ticket.company_id = company_id
    #         await postgres.insert_ticket(ticket)
    #     return aiohttp.web.Response(text='{"answer": "OK"}', content_type='application/json')
    # except Exception as e:
    #     str_e = str(e).replace('"', "'")
    #     return aiohttp.web.Response(text=f'{{"error": "{str_e}"}}')


async def ping(request):
    return aiohttp.web.Response(text='{"answer": "{OK}"}')


async def load_dbf_documents(request):
    pass
    # try:
    #     postgres = PostgresHelperDbf()
    #     redis = RedisApi()
    #     data = await request.read()
    #     schema = InsertDocumentsAsuopSchema()
    #     dict_request = schema.loads(data)
    #     company: Company = await redis.get_entity(dict_request['company_id'], CompanySchema())
    #     company_id = await postgres.get_company_id_by_inn_kpp(company.inn, company.kpp)
    #     if not company_id:
    #         return aiohttp.web.Response(text='{"error": "Wrong Company"}')
    #     documents: set = dict_request[DocumentSchema.key]
    #     for document in documents:
    #         document.company_id = company_id
    #         await postgres.insert_document(document)
    #     return aiohttp.web.Response(text='{"answer": "OK"}', content_type='application/json')
    # except Exception as e:
    #     str_e = str(e).replace('"', "'")
    #     return aiohttp.web.Response(text=f'{{"error": "{str_e}"}}')


async def bind_document_task(need_date: bool):
    pass
    # dbhelper = PostgresHelperDbf()
    # tickets_without_docs = await dbhelper.get_tickets_without_docs()
    # for ticket in tickets_without_docs:
    #     doc = await dbhelper.get_document_for_ticket(ticket, need_date)
    #     if doc:
    #         await dbhelper.bind_doc_to_ticket(doc, ticket)
    #     else:
    #         await dbhelper.remove_ticket(ticket)
    #
    # await dbhelper.remove_documents_without_tickets()


async def bind_documents(request):
    pass
    # try:
    #     data = await request.read()
    #     schema = BindDocumentsSchema()
    #     dict_request = schema.loads(data)
    #     loop = asyncio.get_event_loop()
    #     loop.create_task(bind_document_task(dict_request['useDateTime']))
    #     return aiohttp.web.Response(text=f'{{"answer": "OK"}}')
    # except Exception as e:
    #     str_e = str(e).replace('"', "'")
    #     return aiohttp.web.Response(text=f'{{"error": "{str_e}"}}')
