import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService

import fiscal_face.server.atol.urls
import fiscal_face.server.ax.urls
import fiscal_face.server.admin.urls


class REST(AIOHTTPService):
    async def create_application(self):
        app = aiohttp.web.Application()
        urls = fiscal_face.server.atol.urls.urls + fiscal_face.server.ax.urls.urls + fiscal_face.server.admin.urls.urls
        app.add_routes(urls)

        return app
