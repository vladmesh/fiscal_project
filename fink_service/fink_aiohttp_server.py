import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return aiohttp.web.Response(text=text)


class REST(AIOHTTPService):
    async def create_application(self):
        app = aiohttp.web.Application()

        app.add_routes([
            aiohttp.web.get('/', handle),
            aiohttp.web.get('/{name}', handle)
        ])

        return app
