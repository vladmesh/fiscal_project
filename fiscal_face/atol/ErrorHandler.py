import datetime
from dataclasses import dataclass
from enum import Enum

import aiohttp.web

from core.asyncdb.PostgresHelper import PostgresAsyncHelper
from fiscal_face.atol.schemas.answers import MegapolisAnswerStatus, MegapolisApiAnswerSchema
from fiscal_face.atol.schemas.inner import MegapolisApiErrorType


@dataclass
class MegapolisApiError:
    error_id: int
    type: MegapolisApiErrorType
    text: str
    fields: list


default_descriptions = {MegapolisApiErrorType.WRONG_TOKEN: "Токен неактивен",
                        MegapolisApiErrorType.WRONG_FIELDS_FORMAT: "Неверный формат или значения полей",
                        MegapolisApiErrorType.UNKNOWN_COMPANY: "Компания не была найдена среди относящихся к аккаунту",
                        MegapolisApiErrorType.WRONG_TAX: "Для компании не было найдено касс с указанным "
                                                         "типом налогообложения",
                        MegapolisApiErrorType.TICKET_DOESNT_EXISTS: "Билет не существует"}


class ErrorHandler:
    def __init__(self):
        self.postgres_helper = PostgresAsyncHelper()

    async def generate(self, error_type: MegapolisApiErrorType, request, fields_list=None, text=''):
        request = request.decode('utf-8')
        answer = ''
        for char in request:
            if char not in ('\r', '\n'):
                answer += char
        request = answer
        if text == '':
            text = default_descriptions[error_type]
        error = MegapolisApiError(0, error_type, text, fields_list)
        error.error_id = await self.postgres_helper.insert_error(error, request)
        answer_schema = MegapolisApiAnswerSchema()
        answer_dict = {'status': MegapolisAnswerStatus.ERROR, 'timestamp': datetime.datetime.now(), 'error': error}
        answer_json = answer_schema.dumps(answer_dict)
        return aiohttp.web.Response(text=answer_json, content_type='application/json')
