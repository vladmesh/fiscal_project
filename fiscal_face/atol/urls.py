import aiohttp.web
from fiscal_face.atol.views import get_token

urls = [aiohttp.web.get('/possystem/v4/getToken', get_token),
        aiohttp.web.post('/possystem/v4/getToken', get_token),
        ]
