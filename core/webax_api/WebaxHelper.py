import datetime

import requests
import json
import aiohttp

from core.entities.entities import Company
from core.webax_api.schemas.answers import UpdateDictionariesSchema
from core.webax_api.schemas.requests import UpdateStatusRequest, GetInnKppByPartyIdRequest, WebaxRequest, \
    GetInnKppByRoute


class WebaxHelper:
    def __init__(self):
        self.url = 'https://spkh-webax04.piteravto.ru/WebAX?Request'
        self.update_status_uid = '0fd8d67c-b393-4a2f-91bd-01aff594527b'
        self.get_inn_kpp_by_partyId_uid = 'c363c7f7-ba1f-47e2-adb0-7ad2923b3f76'
        self.update_revise_data_uid = 'd3dd3e6d-08a0-4d36-acf8-1403f67cd41c'
        self.get_inn_kpp_by_routeId_uid = 'ab4d7720-35b2-4f22-8665-906f9894deba'
        self.get_dictionaries_uid = 'dbdea34a-cdab-4f51-8964-2811e3c0a417'

    def update_revise_data(self, region_id, company: Company, additional_tickets, missed_tickets, additional_docs,
                           missed_docs, has_error: bool, has_warning: bool, date: datetime.date,
                           amount_tickets_db_cash, amount_tickets_db_cashless,
                           amount_tickets_asuop_cash, amount_tickets_asuop_cashless,
                           amount_documents_db_cash, amount_documents_db_cashless,
                           amount_documents_ofd_cash, amount_documents_ofd_cashless, answer,
                           has_ofd_access
                           ):
        request = {'additional_tickets': [x.__dict__ for x in additional_tickets],
                   'missed_tickets': [x.__dict__ for x in missed_tickets],
                   'additional_documents': [x.__dict__ for x in additional_docs],
                   'missed_documents': [x.__dict__ for x in missed_docs],
                   'inn': company.inn,
                   'kpp': company.kpp,
                   'region': region_id,
                   'has_error': has_error,
                   'has_warning': has_warning,
                   'date': date,
                   'amount_tickets_db_cash': amount_tickets_db_cash,
                   'amount_tickets_db_cashless': amount_tickets_db_cashless,
                   'amount_tickets_asuop_cash': amount_tickets_asuop_cash,
                   'amount_tickets_asuop_cashless': amount_tickets_asuop_cashless,
                   'amount_documents_db_cash': amount_documents_db_cash,
                   'amount_documents_db_cashless': amount_documents_db_cashless,
                   'amount_documents_ofd_cash': amount_documents_ofd_cash,
                   'amount_documents_ofd_cashless': amount_documents_ofd_cashless,
                   'answer': answer,
                   'has_ofd_access': has_ofd_access,
                   'action': self.update_revise_data_uid}
        data = json.dumps(request, default=str)
        answer = requests.post(url=self.url, data=data)
        return answer.status_code == 200

    def update_fiscal_status(self, recid: int, status: int):
        request = UpdateStatusRequest(recid, status, self.update_status_uid)
        answer = requests.post(url=self.url, json=request.__dict__)
        if answer.status_code != 200:
            return False
        return True

    def get_inn_kpp_by_partyid_uid(self, party_id: str):
        request = GetInnKppByPartyIdRequest(party_id, self.get_inn_kpp_by_partyId_uid)
        answer = requests.post(url=self.url, json=request.__dict__)
        answer_dict = json.loads(answer.content)
        if "error" in answer_dict:
            print(f"При запросе данных о компании {party_id} произошла ошибка: {answer_dict['error']}")
            return None
        if 'INN' in answer_dict and 'KPP' in answer_dict:
            return answer_dict
        print(f"При запросе данных о компании {party_id} вернулся некорректный ответ: {answer.content}")
        return None

    def get_inn_kpp_by_route(self, route_id: str, region: str, release_date):
        request = GetInnKppByRoute(route_id, region, self.get_inn_kpp_by_routeId_uid, release_date)
        answer = requests.post(url=self.url, json=request.__dict__)
        answer_dict = json.loads(answer.content)
        if "error" in answer_dict:
            print(f"При запросе данных о маршруте {route_id} произошла ошибка: {answer_dict['error']}")
            return None
        answer_dict = answer_dict['ActionData']
        if 'INN' in answer_dict and 'KPP' in answer_dict:
            return json.loads(answer_dict)
        print(f"При запросе данных о маршруте {route_id} вернулся некорректный ответ: {answer.content}")
        return None

    async def get_dictionaries(self):
        request = WebaxRequest(self.get_dictionaries_uid)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request.__dict__) as resp:
                answer_json = await resp.json(content_type=None)
                request_schema = UpdateDictionariesSchema()
                request_data = request_schema.loads(answer_json['ActionData'])
                return request_data