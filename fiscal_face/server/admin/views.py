import logging

import aiohttp.web
from aiomisc.log import basic_config


async def load_dbf_tickets(request):
    basic_config(level=logging.DEBUG, buffered=False)
    data = await request.read()
    logging.debug(data)
    async with aiohttp.ClientSession() as session:
        async with session.post('http://revise:8085/load_dbf_tickets', data=data) as resp:
            answer = await resp.text()
            return aiohttp.web.Response(text=answer, content_type='application/json')


async def ping(request):
    return aiohttp.web.Response(text='{"answer": "OK"}')


async def load_dbf_documents(request):
    basic_config(level=logging.DEBUG, buffered=False)
    data = await request.read()
    logging.debug(data)
    async with aiohttp.ClientSession() as session:
        async with session.post('http://revise:8085/load_dbf_documents', data=data) as resp:
            answer = await resp.text()
            return aiohttp.web.Response(text=answer, content_type='application/json')


async def bind_documents(request):
    basic_config(level=logging.DEBUG, buffered=False)
    data = await request.read()
    logging.debug(data)
    async with aiohttp.ClientSession() as session:
        async with session.post('http://revise:8085/bind', data=data) as resp:
            answer = await resp.text()
            return aiohttp.web.Response(text=answer, content_type='application/json')
