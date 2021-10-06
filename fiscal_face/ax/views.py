from core.entities.Cashbox import Cashbox
from core.entities.Company import Company
from core.entities.InstallPlace import InstallPlace
from core.entities.Ofd import Ofd
from core.redis_api.RedisApi import RedisApi
from schemas.answers import CashboxDataAnswerSchema
from schemas.requests import CloseFNSchema, CashboxRegisterSchema


async def reg_cashbox(request):
    data = await request.read()
    schema = CashboxRegisterSchema()
    dict_request = schema.loads(data)
    redis_api = RedisApi()
    cashbox = await redis_api.get_entity(dict_request['cashbox_id'], Cashbox)
    del dict_request['cashbox_id']
    company = await redis_api.get_entity(cashbox.company_id, Company)
    ofd = await redis_api.get_entity(cashbox.ofd_inn, Ofd)
    install_place = await redis_api.get_entity(cashbox.ofd_inn, InstallPlace)
    sender.register_cashbox(**dict_request, company=company, ofd=ofd, install_place=install_place)


async def close_fn(request):
    data = await request.read()
    schema = CloseFNSchema()
    dict_request = schema.loads(data)
    redis_api = RedisApi()
    cashbox = await redis_api.get_entity(dict_request['cashbox_id'], Cashbox)
    sender = CashboxSender(cashbox)
    del dict_request['cashbox_id']
    sender.close_fn(**dict_request)


async def get_cashbox_data(request):
    params = request.rel_url.query
    redis_api = RedisApi()
    if 'id' in params:
        cashbox = await redis_api.get_entity(params['id'], Cashbox)
        sender = CashboxSender(cashbox)
        fn_status = sender.get_storage_status()
        terminal_status = sender.get_terminal_status()
        reg_status = sender.get_reg_status()
        cashbox_answer = CashboxDataAnswer(terminal_status, fn_status, reg_status)
        answer_schema = CashboxDataAnswerSchema()
        return aiohttp.web.Response(text=answer_schema.dumps(cashbox_answer))
