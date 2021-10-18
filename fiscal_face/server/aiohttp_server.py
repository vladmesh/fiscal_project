import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService

import fiscal_face.server.atol.urls
import fiscal_face.server.ax.urls


class REST(AIOHTTPService):
    async def create_application(self):
        app = aiohttp.web.Application()
        urls = fiscal_face.server.atol.urls.urls + fiscal_face.server.ax.urls.urls
        app.add_routes(urls)

        return app