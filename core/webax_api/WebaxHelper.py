import datetime
import logging
from typing import List

import requests
import json
import aiohttp

from core.config import Config
from core.entities.entities import Company, SourceSettings
from core.webax_api.schemas.answers import UpdateDictionariesSchema, GetSourceSettingsSchema, GetAsuopSettingsSchema
from core.webax_api.schemas.requests import UpdateStatusRequest, GetInnKppByPartyIdRequest, WebaxRequest, \
    GetInnKppByRoute, WebaxRequestGetSourceSettings, WebaxRequestGetAsuopSettings, UpdateReviseDataSchema, \
    WebaxRequestGetFiscalApiSettings, WebaxRequestGetToken


class WebaxHelper:
    def __init__(self):
        self.url = Config.WEBAX_URL
        self.update_status_uid = '0fd8d67c-b393-4a2f-91bd-01aff594527b'
        self.get_inn_kpp_by_partyId_uid = 'c363c7f7-ba1f-47e2-adb0-7ad2923b3f76'
        self.update_revise_data_uid = 'd3dd3e6d-08a0-4d36-acf8-1403f67cd41c'
        self.get_inn_kpp_by_routeId_uid = 'ab4d7720-35b2-4f22-8665-906f9894deba'
        self.get_dictionaries_uid = 'dbdea34a-cdab-4f51-8964-2811e3c0a417'
        self.get_source_settings_uid = '76810788-73bc-454e-bb8c-dc07a94e6b0a'
        self.get_asuop_settings_uid = '4a695995-5251-418e-80de-778c8e6b1a56'
        self.get_token_uid = '5c938bee-d1f0-45cb-bd6e-208e7344fe74'
        self.get_api_settings_uid = 'af9fe3b9-1178-4036-877a-8b7a8afa1413'

    async def update_revise_data(self, company: Company, additional_tickets, missed_tickets, additional_docs,
                                 missed_docs, has_error: bool, date: datetime.date,
                                 amount_tickets_db_cash, amount_tickets_db_cashless,
                                 amount_tickets_asuop_cash, amount_tickets_asuop_cashless,
                                 amount_documents_db_cash, amount_documents_db_cashless,
                                 amount_documents_ofd_cash, amount_documents_ofd_cashless, answer
                                 ):
        # TODO with marshmallow
        request = {'additional_tickets': additional_tickets,
                   'missed_tickets': missed_tickets,
                   'additional_documents': additional_docs,
                   'missed_documents': missed_docs,
                   'inn': company.inn,
                   'kpp': company.kpp,
                   'has_error': has_error,
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
                   'action': self.update_revise_data_uid}
        data = UpdateReviseDataSchema().dumps(request)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=data) as resp:
                _ = await resp.json(content_type=None)
        return ''

    def update_fiscal_status(self, recid: int, status: int):
        request = UpdateStatusRequest(recid, status, self.update_status_uid)
        answer = requests.post(url=self.url, json=request.__dict__)
        if answer.status_code != 200:
            return False
        return True

    def DEL_get_inn_kpp_by_partyid_uid(self, party_id: str):
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
                action_data = answer_json['ActionData']
                request_data = request_schema.loads(action_data)
                return request_data

    async def get_sources_settings(self) -> List[SourceSettings]:
        request = WebaxRequestGetSourceSettings(self.get_source_settings_uid)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request.__dict__) as resp:
                answer_json = await resp.json(content_type=None)
                request_schema = GetSourceSettingsSchema()
                action_data = answer_json['ActionData'].replace("\n", '')
                request_data = request_schema.loads(action_data)
                return request_data['source_settings']

    async def get_asuop_settings(self, companies: list):
        request = WebaxRequestGetAsuopSettings(self.get_asuop_settings_uid, companies)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request.__dict__) as resp:
                answer_json = await resp.json(content_type=None, encoding='utf-8')
                request_schema = GetAsuopSettingsSchema()
                action_data = answer_json['ActionData']
                request_data = request_schema.loads(action_data)
                return request_data

    async def get_fiscal_api_settings(self):
        request = WebaxRequestGetFiscalApiSettings(self.get_api_settings_uid)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request.__dict__) as resp:
                answer_json = await resp.json(content_type=None, encoding='utf-8')
                request_schema = GetAsuopSettingsSchema()
                action_data = answer_json['ActionData']
                request_data = request_schema.loads(action_data)
                return request_data

    async def get_fiscal_api_token(self, user_id):
        request = WebaxRequestGetToken(self.get_token_uid, user_id)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request.__dict__) as resp:
                answer_json = await resp.json(content_type=None, encoding='utf-8')
                action_data = answer_json['ActionData']
                answer_dict = json.loads(action_data)
                if "error" in answer_dict:
                    logging.error('')
                    return None
                return request_data
