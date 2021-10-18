import aiohttp.web

from revise_service.server.views import start_revise, ping

urls = [aiohttp.web.post('/revise/start', start_revise),
        aiohttp.web.get('/ping', ping)
        ]
