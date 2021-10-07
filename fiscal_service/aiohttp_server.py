import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService

from fiscal_service.urls import urls


class REST(AIOHTTPService):
    async def create_application(self):
        app = aiohttp.web.Application()

        app.add_routes(urls)

        return app