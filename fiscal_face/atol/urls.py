import aiohttp.web
from views import get_token

urls = [aiohttp.web.get('/getToken', get_token),
        aiohttp.web.post('/getToken', get_token),
        aiohttp.web.get('/getToken/', get_token),
        aiohttp.web.post('/getToken/', get_token)]
