import asyncio
import datetime
import logging

from aiomisc.log import basic_config
from marshmallow import ValidationError

from core.asyncdb.PostgresHelper import PostgresHelperDbf
from core.entities.Enums import Tax, Vat
from core.entities.entities import Company
from core.entities.entity_schemas import CompanySchema, DocumentSchema, TicketSchema
from core.redis_api.RedisApi import RedisApi
from .schemas.requests import InsertDocumentsAsuopSchema, InsertTicketsAsuopSchema, \
    BindDocumentsSchema, StartReviseSchema
import aiohttp.web

from revise.Checker import Revise


async def future_to_coroutine(future):
    return await future


async def start_revise(request):

    data = await request.read()
    try:
        schema = StartReviseSchema()
        dict_request = schema.loads(data)
    except ValidationError as e:
        return aiohttp.web.Response(text=f'{{"error": "{e}"}}', content_type='application/json', status=400)
    #  если промежуток слишком большой - бьём на части
    date_from = dict_request['date_from']
    date_to = dict_request['date_to']
    date_to_tmp = date_from + datetime.timedelta(days=4)
    tasks = []
    while date_to_tmp < date_to:
        dict_request['date_to'] = date_to_tmp
        revise: Revise = Revise(**dict_request)
        error = await revise.init()
        if error:
            return aiohttp.web.Response(text=f'{{"error": "{error}"}}', content_type='application/json', status=400)
        tasks.append(revise.run())
        date_from_tmp = date_to_tmp + datetime.timedelta(days=1)
        date_to_tmp = date_from_tmp + datetime.timedelta(days=3)
        dict_request['date_from'] = date_from_tmp

    if dict_request['date_from'] > date_to:
        dict_request['date_from'] = date_to
    dict_request['date_to'] = date_to
    revise: Revise = Revise(**dict_request)
    error = await revise.init()
    if error:
        return aiohttp.web.Response(text=f'{{"error": "{error}"}}', content_type='application/json', status=400)
    tasks.append(revise.run())

    loop = asyncio.get_event_loop()
    loop.create_task(future_to_coroutine(asyncio.gather(*tasks)))
    return aiohttp.web.Response(text='{"answer": "OK"}', content_type='application/json')


async def load_dbf_documents(request):
    try:
        postgres = PostgresHelperDbf()
        redis = RedisApi()
        data = await request.read()
        schema = InsertDocumentsAsuopSchema()
        dict_request = schema.loads(data)
        company: Company = await redis.get_entity(dict_request['company_id'], CompanySchema())
        company_id = await postgres.get_company_id_by_inn_kpp(company.inn, company.kpp)
        if not company_id:
            return aiohttp.web.Response(text='{"error": "Wrong Company"}')
        documents: set = dict_request[DocumentSchema.key]
        for document in documents:
            document.company_id = company_id
            if document.tax == Tax.GEN:
                document.tax = 2
            if document.tax == Tax.SIMP:
                document.tax = 3
            if document.tax == Tax.SIMPEXP:
                document.tax = 1
            if document.vat == Vat.NONDS:
                document.vat = 1
            if document.vat == Vat.NDS20:
                document.vat = 2
            await postgres.insert_document(document)
        return aiohttp.web.Response(text='{"answer": "OK"}', content_type='application/json')
    except Exception as e:
        str_e = str(e).replace('"', "'")
        return aiohttp.web.Response(text=f'{{"error": "{str_e}"}}')


async def load_dbf_tickets(request):
    try:
        postgres = PostgresHelperDbf()
        redis = RedisApi()
        data = await request.read()
        schema = InsertTicketsAsuopSchema()
        dict_request = schema.loads(data)
        tickets: set = dict_request[TicketSchema.key]
        company: Company = await redis.get_entity(dict_request['company_id'], CompanySchema())
        company_id = await postgres.get_company_id_by_inn_kpp(company.inn, company.kpp)
        if not company_id:
            return aiohttp.web.Response(text='{"error": "Wrong Company"}')
        logging.debug(f'size {len(tickets)}')
        for ticket in tickets:
            ticket.company_id = company_id
            if ticket.tax == Tax.GEN:
                ticket.tax = 2
            if ticket.tax == Tax.SIMP:
                ticket.tax = 3
            if ticket.tax == Tax.SIMPEXP:
                ticket.tax = 1
            if ticket.vat == Vat.NONDS:
                ticket.vat = 1
            if ticket.vat == Vat.NDS20:
                ticket.vat = 2

            await postgres.insert_ticket(ticket)
        return aiohttp.web.Response(text='{"answer": "OK"}', content_type='application/json')
    except Exception as e:
        logging.error(e)
        str_e = str(e).replace('"', "'")
        return aiohttp.web.Response(text=f'{{"error": "{str_e}"}}')


async def bind_document_task(need_date: bool):
    logging.debug("start bind docs")
    success = 0
    dbhelper = PostgresHelperDbf()
    tickets_without_docs = await dbhelper.get_tickets_without_docs()
    total = len(tickets_without_docs)
    for ticket in tickets_without_docs:
        doc = await dbhelper.get_document_for_ticket(ticket, need_date)
        if doc:
            await dbhelper.bind_doc_to_ticket(doc, ticket)
        else:
            await dbhelper.remove_ticket(ticket)

    await dbhelper.remove_documents_without_tickets()
    logging.debug(f'total - {total}, success - {success}')
    logging.debug("start bind docs")


async def bind_documents(request):
    basic_config(level=logging.DEBUG, buffered=False)
    try:
        data = await request.read()
        schema = BindDocumentsSchema()
        dict_request = schema.loads(data)
        loop = asyncio.get_event_loop()
        loop.create_task(bind_document_task(dict_request['useDateTime']))
        return aiohttp.web.Response(text=f'{{"answer": "OK"}}')
    except Exception as e:
        str_e = str(e).replace('"', "'")
        return aiohttp.web.Response(text=f'{{"error": "{str_e}"}}')


async def ping(request):
    pass
