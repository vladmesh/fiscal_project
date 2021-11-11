import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService


async def ping(request):
    return aiohttp.web.Response(text="{answer:OK}")


class REST(AIOHTTPService):
    async def create_application(self):
        app = aiohttp.web.Application()

        app.add_routes([
            aiohttp.web.get('/ping', ping),
        ])

        return app
