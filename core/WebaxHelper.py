import datetime

import requests
import json
import aiohttp

from core.entities import Company


class WebaxRequest:
    def __init__(self, uid):
        self.action = uid


class UpdateStatusRequest(WebaxRequest):
    def __init__(self, recid, status, uid):
        self.status = status
        self.recid = recid
        WebaxRequest.__init__(self, uid)


class GetInnKppByPartyIdRequest(WebaxRequest):
    def __init__(self, partyId, uid):
        self.partyId = partyId
        WebaxRequest.__init__(self, uid)


class GetInnKppByRoute(WebaxRequest):
    def __init__(self, routeId, region, uid, release_date):
        self.routeId = int(routeId)
        self.releaseDate = str(release_date)
        self.region = region
        WebaxRequest.__init__(self, uid)


class WebaxHelper:
    def __init__(self):
        self.url = 'https://spkh-webax04.piteravto.ru/WebAX?Request'
        self.update_status_uid = '0fd8d67c-b393-4a2f-91bd-01aff594527b'
        self.get_inn_kpp_by_partyId_uid = 'c363c7f7-ba1f-47e2-adb0-7ad2923b3f76'
        self.update_revise_data_uid = 'd3dd3e6d-08a0-4d36-acf8-1403f67cd41c'
        self.get_inn_kpp_by_routeId_uid = 'ab4d7720-35b2-4f22-8665-906f9894deba'
        self.get_dictionaries_uid = 'dbdea34a-cdab-4f51-8964-2811e3c0a417'
        self.get_cashboxes_uid = '41cecce8-ec6b-4527-8af6-0cdfdb7d5428'

    def update_revise_data(self, regionid, company: Company, additional_tickets, missed_tickets, additional_docs,
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
                   'region': regionid,
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

    def get_inn_kpp_by_route(self, routeId: str, region: str, release_date):
        request = GetInnKppByRoute(routeId, region, self.get_inn_kpp_by_routeId_uid, release_date)
        answer = requests.post(url=self.url, json=request.__dict__)
        answer_dict = json.loads(answer.content)
        if "error" in answer_dict:
            print(f"При запросе данных о маршруте {routeId} произошла ошибка: {answer_dict['error']}")
            return None
        answer_dict = answer_dict['ActionData']
        if 'INN' in answer_dict and 'KPP' in answer_dict:
            return json.loads(answer_dict)
        print(f"При запросе данных о маршруте {routeId} вернулся некорректный ответ: {answer.content}")
        return None

    async def get_dictionaries(self):
        request = WebaxRequest(self.get_dictionaries_uid)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request.__dict__) as resp:
                return await resp.json(content_type=None)

    async def get_cashboxes(self):
        request = WebaxRequest(self.get_cashboxes_uid)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request.__dict__) as resp:
                return await resp.json(content_type=None)
