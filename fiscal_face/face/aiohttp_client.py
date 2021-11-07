import aiohttp

from core.entities.entities import Cashbox, Ofd, Company, InstallPlace


class FiscalSender:
    """Отправка данных в сервис фискализации"""

    def __init__(self, host='http://localhost', port=8083):
        self.host = host
        self.port = port

    async def get_cashbox_data(self, cashbox: Cashbox):
        pass
        # url = f"{self.host}:{self.port}/get_cashbox_data"
        # request = GetCashboxDataRequest(cashbox_id=cashbox.id,
        #                                 company_id=cashbox.company_id,
        #                                 ip=cashbox.ip,
        #                                 port=cashbox.port)
        # schema = GetCashboxDataRequestSchema()
        # json_request = schema.dumps(request)
        # async with aiohttp.ClientSession() as session:
        #     headers = {'content-type': 'application/json'}
        #     async with session.post(url, data=json_request, headers=headers) as resp:
        #         answer_json = await resp.text()
        #         answer_schema = CashboxDataAnswerSchema()
        #         return answer_schema.loads(answer_json)

    async def register_cashbox(self, cashbox: Cashbox, ofd: Ofd, company: Company, install_place: InstallPlace):
        pass
        # url = f"{self.host}:{self.port}/register_cashbox"
        # request = CashboxRegisterRequest(cashbox_id=cashbox.id,
        #                                  company_id=company.id,
        #                                  ip=cashbox.ip,
        #                                  port=cashbox.port,
        #                                  company_name=company.full_name,
        #                                  company_authorized_person_name=company.authorized_person_name,
        #                                  company_payment_place=company.payment_place,
        #                                  install_place_address=install_place.address,
        #                                  ofd_email=ofd.email,
        #                                  ofd_name=ofd.name,
        #                                  ofd_inn=ofd.inn,
        #                                  company_agent_agent=company.agent_agent,
        #                                  company_inn=company.inn,
        #                                  company_tax=company.tax,
        #                                  register_type=1,
        #                                  cashbox_registry_number=cashbox.registry_number,
        #                                  cashbox_auto_device_number=None,
        #                                  reason=None)
        # schema = CashboxRegisterRequestSchema()
        # json_request = schema.dumps(request)
        # async with aiohttp.ClientSession() as session:
        #     headers = {'content-type': 'application/json'}
        #     async with session.post(url, data=json_request, headers=headers) as resp:
        #         answer_json = await resp.text()
        #         answer_schema = TerminalErrorCodeSchema()
        #         return answer_schema.loads(answer_json)
