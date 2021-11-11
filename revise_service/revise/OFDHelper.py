import asyncio
import logging
import time

import requests
from datetime import datetime
import json

import aiohttp

from core.entities.Enums import Tax
from core.entities.entities import Cashbox
from core.entities.entities import Company
from core.sources.entities import SourceDocument

from core.utils import change_timezone


class OFDHelper:
    def __init__(self, login, password):
        self.baseURL = 'https://ofd.ru/api/'
        self.login = login
        self.password = password
        self.createTokenUrl = 'Authorization/CreateAuthToken'
        self.token = self.get_token()

    def get_token(self):
        params = {"Content-Length": 38,
                  "Content-Type": "application/json",
                  "charset": "utf-8"}
        try:
            r = requests.post(self.baseURL + self.createTokenUrl, data={"Login": self.login, "Password": self.password},
                              params=params)
            token = Token(r.content)
        except Exception as e:
            print(e)
            return None
        return token

    def get_KKT_data(self, fn_number, cashbox_number, cashbox_reg_number, inn):
        params = {'FNSerialNumber': fn_number, 'KKTSerialNumber': cashbox_number, 'KKTRegNumber': cashbox_reg_number,
                  'AuthToken': self.token.AuthToken}
        r = requests.get(self.baseURL + 'integration/v1/inn/' + inn + '/kkts', params=params)
        answer = r.content
        return answer

    async def get_documents_json(self, inn, kkt_reg_num, date_from: datetime, date_to: datetime):
        date_from_str = date_from.strftime("%Y-%m-%dT%H:%M:%S")
        date_to_str = date_to.strftime("%Y-%m-%dT%H:%M:%S")
        params = {'dateFrom': date_from_str, 'dateTo': date_to_str, 'AuthToken': self.token.AuthToken}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.baseURL + f'integration/v1/inn/{inn}/kkt/{kkt_reg_num}/receipts',
                                   params=params) as resp:
                answer_json = await resp.json(content_type=None, encoding='utf-8')
                return answer_json

    async def get_ful_documents_json(self, inn, kkt_reg_num, date_from: datetime, date_to: datetime):
        date_from_str = date_from.strftime("%Y-%m-%dT%H:%M:%S")
        date_to_str = date_to.strftime("%Y-%m-%dT%H:%M:%S")
        params = {'dateFrom': date_from_str, 'dateTo': date_to_str, 'AuthToken': self.token.AuthToken}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.baseURL + f'integration/v1/inn/{inn}/kkt/{kkt_reg_num}/receipts-with-fpd-short',
                                   params=params) as resp:
                answer_json = await resp.json(content_type=None, encoding='utf-8')
                return answer_json

    def get_fiscal_number(self, inn, cashbox_number, doc_id):
        params = {'AuthToken': self.token.AuthToken}
        while True:
            try:
                r = requests.get(self.baseURL + f'integration/v1/inn/{inn}/kkt/{cashbox_number}/receipt/{doc_id}',
                                 params=params)
                answer = json.loads(r.content)
                return answer['Data']['DecimalFiscalSign']
            except Exception as e:
                print(e)
                time.sleep(5)
                pass

    async def parse_json_tickets(self, dict_tickets, cashbox: Cashbox, company: Company, timezone):
        answer = set()
        if dict_tickets['Status'] != 'Success':
            print(dict_tickets['Status'])
            return answer
        for dict_ticket in dict_tickets['Data']:
            document = SourceDocument()
            document.init_from_ofd_api(dict_ticket, timezone)
            if document.type == 5:
                ful_data = await self.get_ful_data(company.inn, cashbox.registry_number, document.id)
                document.tax = ful_data.tax
                document.additional_prop = ful_data.additional_prop
                document.fiscal_sign = ful_data.fiscal_sign
            document.cashbox_reg_num = cashbox.registry_number
            document.cashbox_factory_number = cashbox.factory_number
            document.company_id = company.id
            document.inn = company.inn
            document.kpp = company.kpp
            document.cashbox_id = cashbox.id
            answer.add(document)
        return answer

    async def get_documents(self, company: Company, date_from: datetime, date_to: datetime, cashboxes):
        documents = set()
        date_from = change_timezone(date_from, 'UTC', 'UTC')
        date_to = change_timezone(date_to, 'UTC', 'UTC')
        local_date_from: datetime = change_timezone(date_from, 'UTC', company.timezone)
        local_date_to: datetime = change_timezone(date_to, 'UTC', company.timezone)
        for cashbox in cashboxes:
            while True:
                try:
                    json_answer = await self.get_ful_documents_json(company.inn, cashbox.registry_number,
                                                                    local_date_from,
                                                                    local_date_to
                                                                    )
                    if "Status" not in json_answer or json_answer['Status'] != 'Success':
                        logging.error(str(json_answer))
                        await asyncio.sleep(4)
                        continue
                    documents = documents.union(
                        await self.parse_json_tickets(json_answer, cashbox, company, company.timezone))

                    json_answer = await self.get_documents_json(company.inn, cashbox.registry_number,
                                                                local_date_from,
                                                                local_date_to
                                                                )
                    if "Status" not in json_answer or json_answer['Status'] != 'Success':
                        logging.error(str(json_answer))
                        await asyncio.sleep(4)
                        continue
                    documents_tmp = await self.parse_json_tickets(json_answer, cashbox, company, company.timezone)
                    documents = documents.union(documents_tmp.difference(documents))
                    break
                except Exception as e:
                    logging.error(e)
                    await asyncio.sleep(15)
        documents = set(x for x in documents if date_from <= x.date_fiscal < date_to)
        return documents

    async def get_ful_data(self, inn, cashbox_reg_num, doc_id):
        params = {'AuthToken': self.token.AuthToken}
        while True:
            try:
                r = requests.get(self.baseURL + f'integration/v1/inn/{inn}/kkt/{cashbox_reg_num}/receipt/{doc_id}',
                                 params=params)
                answer = json.loads(r.content)
                doc = SourceDocument()
                doc.fiscal_sign = answer['Data']['DecimalFiscalSign']
                doc.tax = Tax.GEN
                if 'TaxationType' in answer['Data']:
                    tax_type = answer['Data']['TaxationType']
                    if tax_type == 1:
                        doc.tax = Tax.GEN
                    if tax_type == 2:
                        doc.tax = Tax.SIMP
                    if tax_type == 3:
                        doc.tax = Tax.SIMPEXP
                doc.additional_prop = ''
                if 'AdditionalRequisite' in answer['Data']:
                    doc.additional_prop = answer['Data']['AdditionalRequisite']
                return doc
            except Exception as e:
                logging.error(e)
                await asyncio.sleep(25)
                pass


class Token:
    def __init__(self, json_string):
        json_dict = json.loads(json_string)
        self.ExpirationDate = datetime.strptime(json_dict['ExpirationDateUtc'], '%Y-%m-%dT%H:%M:%S')
        self.AuthToken = json_dict['AuthToken']
