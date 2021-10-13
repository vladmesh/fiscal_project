import datetime

import aiohttp.web
from marshmallow import ValidationError

from core.asyncdb.PostgresHelper import PostgresAsyncHelper
from core.entities.Enums import Tax, DocumentType
from core.entities.entities import Company, Ticket
from core.redis_api.RedisApi import RedisApi
from fiscal_face.aiohttp_client import FiscalSender
from fiscal_face.atol.ErrorHandler import ErrorHandler, MegapolisApiErrorType
from fiscal_face.atol.schemas.answers import GetTicketAnswerSchema, MegapolisApiAnswerSchema, MegapolisAnswerStatus, \
    MegapolisApiAnswerSchemaGetTicket
from fiscal_face.atol.schemas.requests import PostTicketSchema, GetTicketSchema


async def get_token(request):
    return aiohttp.web.Response(text='{"token": "testtoken"}', content_type='application/json')


async def post_ticket(request):
    error_handler = ErrorHandler()
    data = await request.read()
    try:
        schema = PostTicketSchema()
        dict_request = schema.loads(data)
    except ValidationError as e:
        fields_list = []
        for field in e.messages:
            field_dict = {'field_name': field, 'message': e.messages[field]}
            fields_list.append(field_dict)
        return await error_handler.generate(MegapolisApiErrorType.WRONG_FIELDS_FORMAT, data, fields_list)

    redis_api = RedisApi()
    company: Company = await redis_api.get_company_by_inn_kpp(dict_request['company_inn'], dict_request['company_kpp'])
    if company is None:
        return await error_handler.generate(MegapolisApiErrorType.UNKNOWN_COMPANY, data)
    postgres_helper = PostgresAsyncHelper()
    ticket = Ticket(0, 'paiq', dict_request['ticket_id'], dict_request['price'], dict_request['payment_type'],
                    dict_request['client_email'], company.id, Tax.GEN, dict_request['vat'])
    await postgres_helper.insert_ticket(ticket)
    return aiohttp.web.Response(text='ok', content_type='application/json')


async def get_ticket(request):
    error_handler = ErrorHandler()
    data = await request.read()
    try:
        schema = GetTicketSchema()
        dict_request = schema.loads(data)
    except ValidationError as e:
        fields_list = []
        for field in e.messages:
            field_dict = {'field_name': field, 'message': e.messages[field]}
            fields_list.append(field_dict)
        return await error_handler.generate(MegapolisApiErrorType.WRONG_FIELDS_FORMAT, data, fields_list)
    ticket_number = dict_request['ticket_id']
    postgres_helper = PostgresAsyncHelper()
    ticket = await postgres_helper.get_ticket(ticket_number)
    if ticket is None:
        return await error_handler.generate(MegapolisApiErrorType.TICKET_DOESNT_EXISTS, data)
    document = await postgres_helper.get_document(ticket.id)
    document.document_type = DocumentType(document.document_type)
    if document is None:
        answer_dict = {'timestamp': datetime.datetime.now(), 'status': MegapolisAnswerStatus.IN_PROCESS, 'answer': None}
        full_answer_schema = MegapolisApiAnswerSchema()
        answer_json = full_answer_schema.dumps(answer_dict)
    else:
        answer_schema = GetTicketAnswerSchema()
        answer_json = answer_schema.dumps(document)
        answer_dict = {'timestamp': datetime.datetime.now(), 'status': MegapolisAnswerStatus.OK, 'answer': document}
        full_answer_schema = MegapolisApiAnswerSchemaGetTicket()
        answer_json = full_answer_schema.dumps(answer_dict)
    return aiohttp.web.Response(text=answer_json, content_type='application/json')

