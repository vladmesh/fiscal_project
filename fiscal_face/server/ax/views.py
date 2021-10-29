from core.entities.entities import Cashbox
from core.entities.entity_schemas import CashboxSchema, CompanySchema, OfdSchema, InstallPlaceSchema
from core.redis_api.RedisApi import RedisApi
from fiscal_face.aiohttp_client import FiscalSender
from fiscal_face.server.ax.schemas.requests import CashboxRegisterSchema, CloseFNSchema
import aiohttp.web

from fiscal_service.server.schemas import CashboxDataAnswerSchema, TerminalErrorCodeSchema


async def reg_cashbox(request):
    data = await request.read()
    schema = CashboxRegisterSchema()
    dict_request = schema.loads(data)
    redis_api = RedisApi()
    cashbox: Cashbox = await redis_api.get_entity(dict_request['cashbox_id'], CashboxSchema())
    del dict_request['cashbox_id']
    company = await redis_api.get_entity(cashbox.company_id, CompanySchema())
    ofd = await redis_api.get_entity(cashbox.ofd_inn, OfdSchema())
    install_place = await redis_api.get_entity(cashbox.location_id, InstallPlaceSchema())
    fiscal_sender = FiscalSender()
    json_dict = await fiscal_sender.register_cashbox(ofd=ofd, cashbox=cashbox, install_place=install_place,
                                                     company=company)
    answer_schema = TerminalErrorCodeSchema()
    return aiohttp.web.Response(text=answer_schema.dumps(json_dict), content_type='application/json')


async def close_fn(request):
    data = await request.read()
    schema = CloseFNSchema()
    dict_request = schema.loads(data)
    redis_api = RedisApi()
    cashbox = await redis_api.get_entity(dict_request['cashbox_id'], CashboxSchema())
    del dict_request['cashbox_id']
    # sender.close_fn(**dict_request)


async def get_cashbox_data(request):
    params = request.rel_url.query
    redis_api = RedisApi()
    if 'id' in params:
        cashbox = await redis_api.get_entity(params['id'], CashboxSchema())
        fiscal_sender = FiscalSender()
        cashbox_data = await fiscal_sender.get_cashbox_data(cashbox)
        answer_schema = CashboxDataAnswerSchema()
        return aiohttp.web.Response(text=answer_schema.dumps(cashbox_data))
