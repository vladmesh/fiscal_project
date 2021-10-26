import asyncio

from marshmallow import ValidationError

from fiscal_face.server.atol.ErrorHandler import ErrorHandler
from fiscal_face.server.atol.schemas.inner import MegapolisApiErrorType
from revise_service.Checker import Revise
from revise_service.server.schemas.requests import StartReviseSchema
import aiohttp.web


async def start_revise(request):
    data = await request.read()
    error_handler = ErrorHandler()
    try:
        schema = StartReviseSchema()
        dict_request = schema.loads(data)
    except ValidationError as e:
        fields_list = []
        for field in e.messages:
            field_dict = {'field_name': field, 'message': e.messages[field]}
            fields_list.append(field_dict)
        return await error_handler.generate(MegapolisApiErrorType.WRONG_FIELDS_FORMAT, data, fields_list)
    revise = Revise(**dict_request)
    error = await revise.init()
    if error:
        return aiohttp.web.Response(text=f'{{"error": "{error}"}}', content_type='application/json', status=400)
    loop = asyncio.get_event_loop()
    loop.create_task(revise.run())
    return aiohttp.web.Response(text='{"answer": "OK"}', content_type='application/json')


async def ping(request):
    pass
