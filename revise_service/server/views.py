import asyncio

from marshmallow import ValidationError


from .schemas.requests import StartReviseSchema
import aiohttp.web

from revise.Checker import Revise


async def start_revise(request):
    data = await request.read()
    try:
        schema = StartReviseSchema()
        dict_request = schema.loads(data)
    except ValidationError as e:
        return aiohttp.web.Response(text=f'{{"error": "{e}"}}', content_type='application/json', status=400)
    revise: Revise = Revise(**dict_request)
    error = await revise.init()
    if error:
        return aiohttp.web.Response(text=f'{{"error": "{error}"}}', content_type='application/json', status=400)
    loop = asyncio.get_event_loop()
    loop.create_task(revise.run())
    return aiohttp.web.Response(text='{"answer": "OK"}', content_type='application/json')


async def ping(request):
    pass
