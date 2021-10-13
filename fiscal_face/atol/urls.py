import aiohttp.web
from fiscal_face.atol.views import get_token, post_ticket, get_ticket

urls = [aiohttp.web.post('/megapolis/getToken', get_token),
        aiohttp.web.post('/megapolis/ticket', post_ticket),
        aiohttp.web.post('/megapolis/get_document', get_ticket)
        ]
