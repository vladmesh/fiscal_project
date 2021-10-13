from core.entities.entities import Cashbox
from core.redis_api.RedisApi import RedisApi
from fiscal_service.CashboxSender import CashboxSender
from fiscal_service.schemas.requests import GetCashboxDataRequestSchema, GetCashboxDataRequest, \
    CashboxRegisterRequestSchema, CashboxRegisterRequest
from fiscal_service.schemas.responds import GetCashboxDataAnswer, CashboxDataAnswerSchema, \
    init_answer_from_status_answers, TerminalErrorCodeSchema

import aiohttp.web


async def get_cashbox_data(request):
    data = await request.read()
    schema = GetCashboxDataRequestSchema()
    request: GetCashboxDataRequest = schema.loads(data)
    # redis_api = RedisApi()
    sender = CashboxSender(request.ip, request.port)
    fn_status = sender.get_storage_status()
    terminal_status = sender.get_terminal_status()
    if fn_status.phaseFN > 1:
        reg_status = sender.get_reg_status()
    else:
        reg_status = None
    cashbox_answer = init_answer_from_status_answers(terminal_status, fn_status, reg_status)
    answer_schema = CashboxDataAnswerSchema()
    return aiohttp.web.Response(text=answer_schema.dumps(cashbox_answer), content_type='application/json')


async def close_fn(request):
    pass


async def register_cashbox(request):
    data = await request.read()
    schema = CashboxRegisterRequestSchema()
    request: CashboxRegisterRequest = schema.loads(data)
    sender = CashboxSender(request.ip, request.port)
    code = sender.register_cashbox(company_name=request.company_name.replace("'", '"'),
                                   company_authorized_person_name=request.company_authorized_person_name.replace("'",
                                                                                                                 '"'),
                                   company_inn=request.company_inn,
                                   company_tax=request.company_tax,
                                   company_payment_place=request.company_payment_place,
                                   company_agent_agent=request.company_agent_agent,
                                   ofd_email=request.ofd_email,
                                   ofd_name=request.ofd_name.replace("'", '"'),
                                   ofd_inn=request.ofd_inn,
                                   cashbox_registry_number=request.cashbox_registry_number,
                                   install_place_address=request.install_place_address.replace("'", '"'),
                                   register_type=request.register_type,
                                   reason=request.reason,
                                   cashbox_auto_device_number=request.cashbox_auto_device_number)
    schema_answer = TerminalErrorCodeSchema()
    answer_dict = {"code": code.code, "description": code.description}
    return aiohttp.web.Response(text=schema_answer.dumps(answer_dict), content_type='application/json')


async def close_session(requests):
    pass
