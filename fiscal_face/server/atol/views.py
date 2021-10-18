import datetime

import aiohttp.web
from marshmallow import ValidationError

from core.asyncdb.PostgresHelper import PostgresAsyncHelper, PostgresHelperTmp
from core.entities.Enums import Tax, DocumentType
from core.entities.entities import Company, Ticket
from core.redis_api.RedisApi import RedisApi
from fiscal_face.server.atol.ErrorHandler import ErrorHandler, MegapolisApiErrorType
from fiscal_face.server.atol.schemas.answers import GetTicketAnswerSchema, MegapolisApiAnswerSchema, MegapolisAnswerStatus, \
    MegapolisApiAnswerSchemaGetTicket, MegapolisApiAnswerSchemaGetToken
from fiscal_face.server.atol.schemas.requests import PostTicketSchema, GetTicketSchema, GetTokenSchema


async def get_token(request):
    error_handler = ErrorHandler()
    data = await request.read()
    try:
        schema = GetTokenSchema()
        dict_request = schema.loads(data)
    except ValidationError as e:
        fields_list = []
        for field in e.messages:
            field_dict = {'field_name': field, 'message': e.messages[field]}
            fields_list.append(field_dict)
        return await error_handler.generate(MegapolisApiErrorType.WRONG_FIELDS_FORMAT, data, fields_list)
    if dict_request['login'] == 'test' and dict_request['password'] == 'test':
        dict_token = {"token": "testtoken"}
        answer_schema = MegapolisApiAnswerSchemaGetToken()
        answer_dict = {'timestamp': datetime.datetime.now(), 'status': MegapolisAnswerStatus.OK, 'answer': dict_token}
        answer_json = answer_schema.dumps(answer_dict)
        return aiohttp.web.Response(text=answer_json, content_type='application/json')
    else:
        return await error_handler.generate(MegapolisApiErrorType.WRONG_LOGIN_OR_PASSWORD, data, None)


async def post_ticket(request):
    error_handler = ErrorHandler()
    headers = request.headers
    data = await request.read()
    if 'token' not in headers or headers['token'] != 'testtoken':
        return await error_handler.generate(MegapolisApiErrorType.WRONG_TOKEN, data)

    if not len(data):
        return await error_handler.generate(MegapolisApiErrorType.WRONG_FIELDS_FORMAT, data, None, "Пустой запрос")
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
    postgres_helper = PostgresHelperTmp()
    ticket = await postgres_helper.get_ticket(dict_request['ticket_id'])
    if ticket:
        return await error_handler.generate(MegapolisApiErrorType.TICKET_ALREADY_EXISTS, data)
    ticket_dict = {'ticket_series': 'paiq', 'ticket_number': dict_request['ticket_id'], 'tax': Tax.SIMPEXP,
                   'vat': dict_request['vat'], 'payment_date': dict_request['payment_date'],
                   'price': dict_request['price'], 'payment_type': dict_request['payment_type'],
                   'id': 0, 'client_email': dict_request['client_email'],
                   'company_id': company.id}

    ticket = Ticket(**ticket_dict)
    await postgres_helper.insert_ticket(ticket)
    answer_dict = {'timestamp': datetime.datetime.now(), 'status': MegapolisAnswerStatus.OK}
    full_answer_schema = MegapolisApiAnswerSchema()
    answer_json = full_answer_schema.dumps(answer_dict)
    return aiohttp.web.Response(text=answer_json, content_type='application/json')


async def get_ticket(request):
    error_handler = ErrorHandler()
    data = await request.read()
    headers = request.headers
    if 'token' not in headers or headers['token'] != 'testtoken':
        return await error_handler.generate(MegapolisApiErrorType.WRONG_TOKEN, data)
    try:
        schema = GetTicketSchema()
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
    ticket_number = dict_request['ticket_id']
    postgres_helper = PostgresHelperTmp()
    ticket = await postgres_helper.get_ticket(ticket_number)
    if ticket is None:
        return await error_handler.generate(MegapolisApiErrorType.TICKET_DOESNT_EXISTS, data)
    document = await postgres_helper.get_document(ticket.id)
    if document is None:
        answer_dict = {'timestamp': datetime.datetime.now(), 'status': MegapolisAnswerStatus.IN_PROCESS, 'answer': None}
        full_answer_schema = MegapolisApiAnswerSchema()
        answer_json = full_answer_schema.dumps(answer_dict)
    else:
        document.document_type = DocumentType(document.document_type)
        answer_schema = GetTicketAnswerSchema()
        answer_json = answer_schema.dumps(document)
        answer_dict = {'timestamp': datetime.datetime.now(), 'status': MegapolisAnswerStatus.OK, 'answer': document}
        full_answer_schema = MegapolisApiAnswerSchemaGetTicket()
        answer_json = full_answer_schema.dumps(answer_dict)
    return aiohttp.web.Response(text=answer_json, content_type='application/json')
