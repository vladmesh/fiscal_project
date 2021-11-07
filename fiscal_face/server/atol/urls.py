import aiohttp.web
from server.atol.views import get_token, post_ticket, get_ticket

urls = [aiohttp.web.post('/megapolis/v1/get_token', get_token),
        aiohttp.web.post('/megapolis/v1/post_ticket', post_ticket),
        aiohttp.web.post('/megapolis/v1/get_document', get_ticket),
        aiohttp.web.post('/megapolis/v1/get_token/', get_token),
        aiohttp.web.post('/megapolis/v1/post_ticket/', post_ticket),
        aiohttp.web.post('/megapolis/v1/get_document/', get_ticket)
        ]
