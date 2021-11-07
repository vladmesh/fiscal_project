import aiohttp.web

from .views import start_revise, ping

urls = [aiohttp.web.post('/revise/start', start_revise),
        aiohttp.web.get('/ping', ping)
        ]
