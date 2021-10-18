import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService

import revise_service.server.urls


class REST(AIOHTTPService):
    async def create_application(self):
        app = aiohttp.web.Application()
        urls = revise_service.server.urls.urls
        app.add_routes(urls)

        return app
